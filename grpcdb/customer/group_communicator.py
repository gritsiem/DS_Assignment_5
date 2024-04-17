from helper import Helper

from dotenv import load_dotenv
import os
import socket
import pickle
import threading
import time

load_dotenv()

class Types:
    request = "REQUEST_MSG"
    sequence = "SEQUENCE_MSG"
    retransmit = "RETRANSMIT"

class Request:
    def __init__(self, method_name:str, args: dict) -> None:
        self.method = method_name
        self.args = args

class SequenceMsg:
    def __init__(self, gid, reqid, aru):
        self.gid = gid
        self.reqid = reqid
        self.aru = []
    def __repr__(self) -> str:
        return f"gid = {self.gid}, request = {self.reqid}"
    
class RequestMsg:
    def __init__(self, pid, lsn, req: Request):
        self.id = (pid,lsn)
        self.request = req
        self.metadata = None
    def __repr__(self) -> str:
        return f"pid = {self.id}, method = {self.request.method}"

class Member:

    nmembers = 0
    nextk = -1
    pid = -1
    lsn = -1
    aru = []
    my_aru = -1 # used to keep track of request messages received upto global_id aru  

    # gid to request id
    seq_to_reqid= {}
    # pid to dictionary of lsn:req
    request_hist = {0:{},1:{},2: {},3: {},4: {}}

    is_my_turn = False
    helper = None
    execute_q = {}
    RETURN_GRPC = {}

    #unsure 
    missing = []
    highestexecuted = -1
    wait_q = {"req":{},"seq":[]} # messages to retransmit

    def __init__(self, addr, pid):
        self.host, port = addr.split(":")
        self.port = int(port)+1
        

        self.__members = os.getenv('CUSTOMER_SERVERS').strip().split("\n")
        Member.nmembers = len(self.__members)
        self.__members = [ ((mem.split("-")[1]).split(":")[0],int((mem.split("-")[1]).split(":")[1])+1) for mem in self.__members]
        self.initiate_UDP()
        Member.aru = [-1 for m in range(Member.nmembers)]
        Member.pid = int(pid)
        Member.nextk = Member.pid%Member.nmembers
        Member.helper = Helper(Member.pid)

        if Member.pid==0:
            Member.is_my_turn = True

    def initiate_UDP(self):
        
        self.skt = socket.socket(socket.AF_INET, # Internet
                    socket.SOCK_DGRAM) # UDP
        self.skt.bind((self.host,self.port))
        thread = threading.Thread(target = self.receive_msgs)
        thread.start()
        
    
    def broadcast(self,msg):
        for mem in self.__members:
            # print("sending",msg,"to ", mem)
            try:
                x = pickle.dumps(msg)
            except Exception as e:
                print(e)
            # print("sanity please", len(x))
            self.skt.sendto(pickle.dumps(msg),mem)

    
    def send_request_msg(self, request: Request):
        Member.lsn+=1
        lsn = Member.lsn
        new_request = RequestMsg( Member.pid, Member.lsn, request)
        msg = self.create_msg(Types.request, new_request)
        Member.request_hist[Member.pid][Member.lsn] = request
        self.broadcast(msg)
        Member.RETURN_GRPC[lsn] = False
        while True:
            if Member.RETURN_GRPC[lsn]:
                del Member.RETURN_GRPC[lsn]
                return lsn
            time.sleep(1)

    def status(self):
        print("Me aru = ", Member.my_aru)
        print("All aru = ", Member.aru)
        print("My requests = \n", Member.request_hist)
        print("My sequences = \n", Member.sequence_hist)

    def receive_msgs(self):
        print("waiting to receive on...", self.host, self.port)
        while True:
            data, addr = self.skt.recvfrom(2048)
            msg = pickle.loads(data)
            print("New group message: ",msg)
            self.status()
            if msg["type"] == Types.request:
                self.handleRequestMsg(msg["payload"])
            elif msg["type"] == Types.sequence:
                self.handleSequenceMsg(msg["payload"])
            elif msg["type"] == Types.retransmit:
                self.handleRetransmitMsg(msg["payload"])
            else:
                continue

    
    def create_msg(self, type, payload):
        # print("created msg")
        return { "type": type, "payload":payload}
    

    def handleSequenceMsg(self, msg: SequenceMsg):
        gid = msg.gid
        # msg will have global id, and request id 

        if not Member.is_my_turn:
            Member.is_my_turn = Member.nextk==gid+1 and Member.nextk%Member.nmembers == Member.pid
        
        Member.seq_to_reqid[gid] = msg.reqid
        print("updated received sequences: ", Member.seq_to_reqid)
        # be prepared to send the next Sequence message
        
        # sequence wait list
        waitlist = Member.wait_q["seq"]    
        
        # if were waiting for this sequence message -- we have it now, remove it from retransmit queue 
        if gid in waitlist:
            waitlist.pop(gid)
    
        # for any messages between aru and this sequence gid ( we know we already have received upto aru for sure)
        for id in range(Member.my_aru+1, gid):
            # send sequence retransmits
            if id not in waitlist:
                waitlist.append(gid)
                #send retransmit
                # self.handleRetransmit(type,list(waitlist.keys()))

        pid,lsn = msg.reqid
        if lsn in Member.request_hist[pid].keys():
            print("can update my_aru? ", Member.my_aru, gid)
            if Member.my_aru == gid-1:
                print("updated")
                Member.my_aru = gid
            Member.request_hist[pid][lsn]
            print("found request already")
            request = Member.request_hist[pid][lsn]
            print("Sequence mapped to Request = ", Member.request_hist[pid])
            Member.execute_q[gid] = request
            self.handleExecute()
    
        else:
            msg = {"type": Types.request, "request_id":(pid, lsn)}
            msg = self.create_msg(Types.retransmit, msg)
            Member.request_hist[Member.pid][0]+=[Member.lsn]
            Member.request_hist[Member.pid][1]+=[msg]
            self.broadcast(msg)

            
    
    def handleExecute(self):
        Member.execute_q = dict(sorted(Member.execute_q.items()))
        print("Execute queue sorted: ",Member.execute_q)
        for gid in Member.execute_q:
            pid,lsn = Member.seq_to_reqid[gid]
            call = Member.execute_q[gid]
            if pid == Member.pid:
                print("GRPC return required")
                newid = Member.helper.by_name(call.method, call.args)
                Member.RETURN_GRPC[lsn] = newid 
            else:
                print("No GRPC execution")
                Member.helper.by_name(call.method, call.args)
        
        Member.execute_q={}
                
          
    def checkConditions(self, req_id):        
        if Member.my_aru!=Member.nextk-1:
            print("condition failed:  aru   => ", Member.my_aru, Member.nextk)
            return False
        
        for gid in range(Member.nextk):
            pid,lsn = Member.seq_to_reqid[gid]
            if not (Member.request_hist[pid])[lsn]:
                print("Condition failed -- : No correspoinding request msg")
                return False
        
        # naive way to check if all the lsns for pid have been received.
        for lsn in range(req_id[1]):
            lsns_received = Member.request_hist[req_id[0]].keys()
            if lsn not in lsns_received:
                print("Condition failed -- : Not received all requests from pid")
                return False

        return True
    
    def handleRequestMsg(self, msg:RequestMsg):
        pid, lsn = msg.id
        pid = int(pid)
        request_id = (pid,lsn)

        # Part 1 -- check for sequence message

        # #check if you have a sqn msg with associated request id
        # if msg["header"] in Member.req_to_seq:
        #     gid = Member.req_to_seq[msg["header"]]
        #     # move message to execute queue.
        #     Member.execute_q[gid]=msg["call"]
        #     # also update highest received number -- if applicable
        #     if Member.my_aru == gid-1:
        #         Member.my_aru=gid
        #     # pop sequence message from any queue
            
        #     pass
        # else:
        #     # add to request queue -- no retransmit for sequence message because you dont know the gid
        #     Member.wait_q["req"][msg["header"]]=msg["call"]


        # Part 2 -- check if you need to send a sequence message
            
        # If it's my turn for creating request message -- 
        # check all three conditions to create a sequence message until satisfied or do retransmit.
        print("checking sequence conditions: ", Member.nextk, Member.pid)
        if Member.is_my_turn and self.checkConditions(msg.id):

            aru = Member.aru
            aru[Member.pid] = Member.my_aru # update metadata

            # create sequence message
            seqmsg = SequenceMsg(gid=Member.nextk, reqid=msg.id,aru=aru)
            seqmsg = self.create_msg(Types.sequence, seqmsg)
            self.broadcast(seqmsg)

            # debug
            print("*****************************")
            print("SQN MSG SENT: ", seqmsg)
            print("*****************************")
            # update nextk to next value
            Member.nextk = Member.nextk + Member.nmembers

        # common action
        if pid!=Member.pid:
            (Member.request_hist[pid])[lsn]= msg.request

        print("Updated Requests History")


    
    def check_pid(self, pid, lsn):
        for n in range(lsn):
            lsns = Member.request_hist[pid]
            if n not in lsns:
                return False
        return True
    
    
    def handleRetransmit(self,msg):

        if msg["type"] == Types.sequence:
            for id in msg["gids"]:
                if id%Member.nmembers==Member.pid:
                    aru = Member.aru
                    aru[Member.pid] = Member.my_aru
                    # msg = Member.sequence_hist[id]
                    msg = {"gid":Member.nextk,"request_id":msg["header"], "aru" :aru}
                    msg = self.create_msg(Types.sequence, msg)
                    self.broadcast(msg)
        
        if msg["type"] == Types.request:
            pid,lsn = msg["request_id"]
            if pid==Member.pid:
                if lsn in Member.request_hist[pid]:
                    i = Member.request_hist[pid][0].index(lsn)
                    if i>-1:
                        request = Member.request_hist[pid][1][i]
                        data = {"header":(Member.pid, lsn), "call":request}
                        msg = self.create_msg(Types.request, data)
                        Member.request_hist[Member.pid][0]+=[Member.lsn]
                        Member.request_hist[Member.pid][1]+=[msg]
                        self.broadcast(msg)
                        


                    

