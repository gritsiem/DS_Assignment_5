from concurrent import futures
import time
import sys
import os


import grpc
import customers_pb2 as pb2
import customers_pb2_grpc as pb2grpc

from helper import Helper
from group_communicator import Request, Member
'''
File to run server for seller in the E-Market application
Server
- uses multi-threading to accept multiple clients
- connects clients with the server interface of the application which connects to the DB
- also calculates statistics and logs them:
    - Average response time for 10 function calls
    - Average throughput for a 1000 function calls
'''


class CustomerDB(pb2grpc.CustomersServicer):
    def __init__(self,addr,pid):
        '''
        Initializes for binding server to port and keeps track of active connections over all clients 
        '''
        self.__local_sequence_number = 0
        self.helper = Helper(pid)
        self.member = Member(addr, pid)

    def RegisterSellerDB(self, request, context):
        # un, pw
        # newid = self.helper._registerSellerDB(request)
        req = Request("RegisterSellerDB", request)
        newid = self.member.send_request_msg(req)

        response = pb2.generalResponse() 
        response.msg = str(newid)  
        return response
    
        
    def GetUserDB(self, request, context):
        # un, password (optional)
        user = None
        x = self.helper._gettUserDB(request)
        if x!=-1:
            user=x
        response = pb2.generalResponse() 
        response.msg = str(user)  
        return response
    
    
    def UpdateSellerFeedback(self, request, context):
        # seller_id,tu,td
        # self.helper._updateSellerFeedback(request)
        req = Request("UpdateSellerFeedback", request)
        newid = self.member.send_request_msg(req)
        response = pb2.generalResponse() 
        response.msg = str(1) 
        return response


def serve(addr=None,id=None):

    # server = grpc.server(futures.ThreadPoolExecutor(max_workers=200), interceptors=(OrderInterceptor(addr,id),))
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=200))
    pb2grpc.add_CustomersServicer_to_server(CustomerDB(addr,id),server)
    server.add_insecure_port(addr)
    
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    # get server-id, hostname, port from group starter
    if(len(sys.argv)==3):
        serve(sys.argv[2], sys.argv[1])
    else:
        serve("localhost:6080", 0)
        
    