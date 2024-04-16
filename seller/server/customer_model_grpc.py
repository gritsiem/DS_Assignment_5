import customers_pb2_grpc as pb2grpc
import customers_pb2 as pb2

import time
import grpc
import os
from ast import literal_eval


class CustomerInterfaceGRPC:
    def __init__(self):
        '''
        Initializes required parameters for socket connection and also begins communication. 
        '''
        self._PORT = "6080"
        self._SERVER = "localhost"
        self._ADDRESS = self._SERVER+":"+self._PORT
        self.__stub = None
        self.inititate_connection()

    def inititate_connection(self):
        self.channel = grpc.insecure_channel(self._ADDRESS,options=(('grpc.enable_http_proxy',0),))
        self.__stub = pb2grpc.CustomersStub(self.channel)

    def registerSeller(self, un, pw):
        try:
            registerRequest = pb2.UserCredentialsMessage(username=un, password = pw)
            response = self.__stub.RegisterSellerDB(registerRequest)
        except Exception as e:
            print(e)
            return -1

        # print("last row id",response)
        return response.msg
    
        
    def getUser(self, un, pw=None):
        user = None
        try:
            request = pb2.UserCredentialsMessage( username=un, password = pw)
            response = self.__stub.GetUserDB(request)
        except Exception as e:
            print(e)
            return -1
        user = literal_eval(response.msg)
        return user
    
    def updateFeedback(self, seller_id,tu,td):
        # msg = f"UPDATEBYCOL;seller;thumbs_up_count,thumbs_down_count;{tu},{td};id;{seller_id}"
        updateRequest = pb2.SellerFeedbackMessage(tu = tu,td = td, seller_id=seller_id)
        response = self.__stub.UpdateSellerFeedback(updateRequest)
        # return didUpdate
        return response.msg
    

if __name__ == "__main__":
    client = CustomerInterfaceGRPC()
    print(client.registerSeller("user1","userone"))
    # print(client.updateFeedback(3,3,4))
    print("seller db client started..")
    # print(client.getUser("user1"))
