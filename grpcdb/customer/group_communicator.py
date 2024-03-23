from helper import Helper

from dotenv import load_dotenv
import os
import socket
import pickle
import threading


load_dotenv()

class Types:
    request = "REQUEST_MSG"
    sequence = "SEQUENCE_MSG"
    retransmit = "RETRANSMIT"

class SequenceMsg:
    def __init__(self, gid, reqid, aru):
        self.gid = gid
        self.reqid = reqid
        self.aru = []

class Member:
    pid = -1
    lsn = -1
    aru = [-1,-1,-1,-1,-1]
    my_aru = -1 # used to keep track of request messages received upto global_id aru  
    highestexecuted = -1
    missing = []
    request_hist = {0:[[],[]],1:[[],[]],2: [[],[]],3: [[],[]],4: [[],[]]}
    sequence_hist = {}

    # messages to retransmit
    wait_q = {"req":{},"seq":[]}

    # have mapping of request ids to sequence message and vice versa
    seq_to_req= {}
    req_to_seq= {}
    helper = None
    my_turn = False
    execute_q = {}



    def __init__(self, addr, pid):
        self.host, port = addr.split(":")
        self.port = int(port)+1
        

        self.__members = os.getenv('CUSTOMER_SERVERS').strip().split("\n")
        Member.nmembers = len(self.__members)
        self.__members = [ ((mem.split("-")[1]).split(":")[0],int((mem.split("-")[1]).split(":")[1])+1) for mem in self.__members]

        self.initiate_UDP()
        Member.pid = int(pid)
        Member.nextk = Member.pid%Member.nmembers
        if Member.pid == 0:
            Member.my_turn=True

        Member.helper = Helper(Member.pid)

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

    
    def send_request_msg(self,request):
        Member.lsn+=1
        data = {"header":(Member.pid, Member.lsn), "call":request}
        msg = self.create_msg(Types.request, data)
        Member.request_hist[Member.pid][0]+=[Member.lsn]
        Member.request_hist[Member.pid][1]+=[data["call"]]
        self.broadcast(msg)

    def status(self):
        print("Me aru = ", Member.my_aru)
        print("All aru = ", Member.aru)
        print("My requests = \n", Member.request_hist)
        print("My sequences = \n", Member.sequence_hist)

    def receive_msgs(self):
        print("waiting to receive on...", self.host, self.port)
        print("current request queue ==\n", Member.request_hist)
        while True:
            data, addr = self.skt.recvfrom(2048)
            msg = pickle.loads(data)
            print(msg)
            self.status()
            if msg["type"] == Types.request:
                print("Message gateway: ",msg)
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
    

    def handleSequenceMsg(self, data):
        gid = data["gid"] 
        # data will have global id, and request id 
        # Member.sequence_hist += [gid]
        Member.sequence_hist[gid]= data["request_id"]
        print("updated received sequences: ", Member.sequence_hist)
        # be prepared to send the next Sequence message
        if gid == Member.nextk-1:
            Member.nextk += Member.nmembers
            Member.my_turn = True
        
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

        pid,lsn = data["request_id"]
        if lsn in Member.request_hist[pid][0]:
            if Member.my_aru == gid-1:
                Member.my_aru = gid
            i = Member.request_hist[pid][0].index(lsn)
            print("found request already at index: ",i)
            request = Member.request_hist[pid][1][i]
            print("Request = ", Member.request_hist[pid])
            Member.execute_q[gid] = request
            self.handleExecute()
    
        else:
            data = {"type": Types.request, "request_id":(pid, lsn)}
            msg = self.create_msg(Types.retransmit, data)
            Member.request_hist[Member.pid][0]+=[Member.lsn]
            Member.request_hist[Member.pid][1]+=[msg]
            self.broadcast(msg)

            
    
    def handleExecute(self):
        Member.execute_q = dict(sorted(Member.execute_q.items()))
        print("Execute queue sorted: ",Member.execute_q)
        for gid in Member.execute_q:
            call = Member.execute_q[gid]
            print
            Member.helper.by_name(call["method"], call["args"])
                
          
    
    def handleRequestMsg(self, msg):
        pid, lsn = msg["header"]
        pid = int(pid)
        request_id = (pid,lsn)
        print(pid, type(pid),lsn,type(lsn))
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
            
        # If all gids uptil k are in the queue
        if Member.my_turn: # my_turn is set to true if you have received all pairs of sequence+request messages
            if self.check_pid(pid,lsn):
                aru = Member.aru
                aru[Member.pid] = Member.my_aru
                seqmsg = {"gid":Member.nextk,"request_id":msg["header"], "aru" :aru}
                seqmsg = self.create_msg(Types.sequence, seqmsg)
                self.broadcast(seqmsg)

        # common actions
        if pid!=Member.pid:
            Member.request_hist[pid][0].append(lsn)
            Member.request_hist[pid][1].append(msg["call"])
        print("updated requests",Member.request_hist)


    
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
                    msg = Member.sequence_hist[id]
                    msg = {"gid":Member.nextk,"request_id":msg["header"], "aru" :aru}
                    msg = self.create_msg(Types.sequence, msg)
                    self.broadcast(msg)
        
        if msg["type"] == Types.request:
            pid,lsn = msg["request_id"]
            if pid==Member.pid:
                if lsn in Member.request_hist[pid][0]:
                    i = Member.request_hist[pid][0].index(lsn)
                    if i>-1:
                        request = Member.request_hist[pid][1][i]
                        data = {"header":(Member.pid, lsn), "call":request}
                        msg = self.create_msg(Types.request, data)
                        Member.request_hist[Member.pid][0]+=[Member.lsn]
                        Member.request_hist[Member.pid][1]+=[msg]
                        self.broadcast(msg)
                        


                    

