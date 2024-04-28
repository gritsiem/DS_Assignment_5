from helper import Helper

from dotenv import load_dotenv
import os
import socket
import pickle
import threading
import time
import sys

load_dotenv()

class Types:
    request = "REQUEST_MSG"
    sequence = "SEQUENCE_MSG"
    retransmit = "RETRANSMIT"
    join = "JOIN_MSG"

class Timeouts:
    TOKEN_TIMEOUT = 0.8
    JOIN_TIMEOUT = 0.5


class Request:
    def __init__(self, method_name:str, args: dict) -> None:
        self.method = method_name
        self.args = args

class SequenceMsg:
    def __init__(self, gid, reqid, aru):
        self.gid = gid
        self.reqid = reqid
        self.aru = aru
    def __repr__(self) -> str:
        return f"gid = {self.gid}, request = {self.reqid}, aru = {self.aru}"
    
class RequestMsg:
    def __init__(self, pid, lsn, req: Request):
        self.id = (pid,lsn)
        self.request = req
        self.metadata = None
    def __repr__(self) -> str:
        return f"pid = {self.id}, method = {self.request.method}"

class JOIN_MESSAGE:
    def __init__(self, pid, proc_set, fail_set):
        self.pid = pid
        self.proc_set = proc_set
        self.fail_set = fail_set

class COMMIT_MESSAGE:
    def __init__(self):
        self.updated_members = []

class TIMEOUTS:
    join = 3

class STATES:
    join = "JOIN"
    operational = "OPERATIONAL"

class Member:

    nmembers = 0
    pids = set()
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

    #member protocol
    STATE = STATES.join

    def __init__(self, addr, pid):
        self.host, port = addr.split(":")
        self.port = int(port)+1
        Member.pid = int(pid)

        self.__members = os.getenv('CUSTOMER_SERVERS').strip().split("\n")
        Member.nmembers = len(self.__members)
        self.__members = [ ((mem.split("-")[1]).split(":")[0],int((mem.split("-")[1]).split(":")[1])+1) for mem in self.__members]
        self.initiate_UDP()
        
        Member.config = [(pid,self.host,self.port)]
        self.send_join(Member.config,[])
        # self.initiate_join_state()

        Member.aru = [-1 for m in range(Member.nmembers)]
        Member.nextk = Member.pid%Member.nmembers
        Member.helper = Helper(Member.pid)

        if Member.pid==0:
            Member.is_my_turn = True

        Member.receive_thread = threading.Thread(target = self.receive_msgs)
        Member.receive_thread.start()    
        
    def initiate_UDP(self):
        
        self.skt = socket.socket(socket.AF_INET, # Internet
                    socket.SOCK_DGRAM) # UDP
        # self.skt.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        self.skt.bind((self.host,self.port))

    def initiate_join_state(self, new_joinmsg=None):
        
        self.skt.settimeout(TIMEOUTS.join)
        Member.STATE = STATES.join 
        p = list(Member.config)
        f = list()
        is_equal = [0,0,0,0,0]
        while True:
            if not new_joinmsg:
                try:
                    data, addr = self.skt.recvfrom(320)
                    msg = pickle.loads(data)
                except ConnectionResetError:
                    continue
                except TimeoutError:
                    break
                if msg["type"] == Types.join:
                    joinmsg:JOIN_MESSAGE = msg['payload']
            else:
                joinmsg = new_joinmsg
                new_joinmsg = None
                print("stuck new msg here")
            print("Received join from PID: ", joinmsg.pid)
            print("pids = ", Member.pids)
            # print("[debug] ", sys.getsizeof(joinmsg.proc_set[0]))
            Member.pids.add(joinmsg.pid)
            print("p = ", p, " received proc_seet = ", joinmsg.proc_set, p==joinmsg.proc_set)

            if set(joinmsg.proc_set)!=set(p) or set(joinmsg.fail_set)!=set(f):
                p = set(p) | set(joinmsg.proc_set)
                p=list(p)
                f = set(f) | set(joinmsg.fail_set)
                f=list(f)
                self.send_join(p,f)
                print("updated proc set = ", p)
                
            is_equal[joinmsg.pid] = 1
            print("isequal --> " ,is_equal)
            if sum(is_equal)==len(Member.pids):
                break
            time.sleep(1)
        Member.config = p
        print("Final configuration: ", Member.config)
        Member.STATE = STATES.operational
        self.skt.settimeout(None)


    def send_join(self, p, f): 
        msg = JOIN_MESSAGE(pid = Member.pid,proc_set=p,fail_set=f)
        msg = self.create_msg(type=Types.join, payload=msg)
        print("Broadcasting Join Message")
        for mem in self.__members:
            try:
                self.skt.sendto(pickle.dumps(msg),mem)
            except Exception as e:
                print("error",e)
            # print("sanity please", len(x))
            
        
    def broadcast(self,msg):
        for mem in Member.config:
            # print("sending",msg,"to ", mem)
            try:
                x = pickle.dumps(msg)
            except Exception as e:
                print(e)
            # print("sanity please", len(x))
            self.skt.sendto(pickle.dumps(msg),mem)

    
    def send_request_msg(self, request: Request):
        if Member.STATE == STATES.join:
            return -1
        Member.lsn+=1
        lsn = Member.lsn
        new_request = RequestMsg( Member.pid, Member.lsn, request)
        msg = self.create_msg(Types.request, new_request)

        Member.request_hist[Member.pid][Member.lsn] = request

        self.broadcast(msg)

        Member.RETURN_GRPC[lsn] = False
        while True:
            if Member.RETURN_GRPC[lsn]:
                resp = Member.RETURN_GRPC[lsn]
                del Member.RETURN_GRPC[lsn]
                return resp
            time.sleep(1)

    def status(self):
        print("Me aru = ", Member.my_aru)
        print("All aru = ", Member.aru)
        print("My requests = \n", Member.request_hist)
        print("My sequences = \n", Member.seq_to_reqid)

    def receive_msgs(self):
        print("waiting to receive on...", self.host, self.port)
        while True:
            try: 
                data, addr = self.skt.recvfrom(2048)
            except ConnectionResetError:
                continue
            msg = pickle.loads(data)
            print("New group message: ",msg)
            # self.status()
            if msg["type"] == Types.request:
                self.handleRequestMsg(msg["payload"])
            elif msg["type"] == Types.sequence:
                self.handleSequenceMsg(msg["payload"])
            elif msg["type"] == Types.retransmit:
                self.handleRetransmitMsg(msg["payload"])
            elif msg["type"] == Types.join:
                joinmsg:JOIN_MESSAGE = msg['payload']
                if joinmsg.pid in Member.pids:
                    continue
                print("Current configuration: ", Member.pids)
                self.initiate_join_state(joinmsg)
                print("completed JOIN Protocol\n\n")
            else:
                continue

    
    def create_msg(self, type, payload):
        # print("created msg")
        return { "type": type, "payload":payload}
    
    def updateAru(self, newaru):
        temp=[]
        print("new_aru", newaru)
        for x,y in zip(Member.aru, newaru):
            temp.append(max(x,y))
        Member.aru = temp

    def handleSequenceMsg(self, msg: SequenceMsg):
        # msg will have global id, request id, and aru 
        gid = msg.gid
        self.updateAru(msg.aru)

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

    def canExecute(self, gid):
        print("Testing execution conditions: ", Member.aru, gid)
        majority = (Member.nmembers/2)+1
        received = [1 for value in Member.aru if value >= gid]
        if sum(received)>= majority:
            print(sum(received))
            return True
        return False
     
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

        Member.execute_q = {}
     
    def handleExecute2(self):
        Member.execute_q = dict(sorted(Member.execute_q.items()))
        print("Execute queue sorted: ",Member.execute_q)

        keys_to_pop = []
        for gid in Member.execute_q:
            print("Execute GID?", gid)
            # ensure majority of members have received the sequence message or move to the next GID
            if not self.canExecute(gid):
                print("NO!")
                continue

            pid,lsn = Member.seq_to_reqid[gid]
            call = Member.execute_q[gid]
            if pid == Member.pid:
                print("GRPC return required")
                newid = Member.helper.by_name(call.method, call.args)
                Member.RETURN_GRPC[lsn] = newid 
            else:
                print("No GRPC execution")
                Member.helper.by_name(call.method, call.args)
            
            keys_to_pop.append(gid)

        for key in keys_to_pop:
            del Member.execute_q[key]
     
          
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
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n", aru, "\n```````````````````")
            aru[Member.pid] = Member.my_aru # update metadata
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n", aru, "\n```````````````````")
            # create sequence message
            seqmsg = SequenceMsg(gid=Member.nextk, reqid=msg.id, aru=aru)
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
                        


                    

