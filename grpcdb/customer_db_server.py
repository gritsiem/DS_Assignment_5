from concurrent import futures
import time
import pickle
import os
from dotenv import load_dotenv
import psycopg2

import grpc
import customers_pb2 as pb2
import customers_pb2_grpc as pb2grpc

'''
File to run server for seller in the E-Market application
Server
- uses multi-threading to accept multiple clients
- connects clients with the server interface of the application which connects to the DB
- also calculates statistics and logs them:
    - Average response time for 10 function calls
    - Average throughput for a 1000 function calls
'''
load_dotenv()
class CustomerDB(pb2grpc.CustomersServicer):
    def __init__(self):
        '''
        Initializes for binding server to port and keeps track of active connections over all clients 
        '''
        self.HOST = "localhost"
        self.PORT = 6080
        self.ADDRESS = (self.HOST, self.PORT)
        self.loadDB()

    def loadDB(self):
        pw = os.getenv('PASSWORD')
        self.connection = psycopg2.connect(f"dbname='customers_db' user='postgres' host='localhost' password='{pw}'")
        self.cursor = self.connection.cursor()
        try:
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS seller (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(32) NOT NULL,
                    password VARCHAR(12) CHECK(char_length(password) BETWEEN 6 and 12),
                    thumbs_up_count INTEGER DEFAULT 0,
                    thumbs_down_count INTEGER DEFAULT 0,
                    items_sold INTEGER DEFAULT 0
                );''')
        except Exception as e:
            print("creation error", e)
        self.connection.commit()
        print("DB server started")

    def RegisterSellerDB(self, request, context):
        # un, pw
        try:
            self.cursor.execute("INSERT INTO seller (username, password) VALUES \
                    (%s, %s) returning id",(request.username, request.password))
            newid = self.cursor.fetchone()[0]
        except Exception as e:
            print("Error: RegisterCustomerDB -- ",e)
            return -1

        print("last row id",newid)
        self.connection.commit()

        response = pb2.generalResponse() 
        response.msg = str(newid)  
        return response
    
        
    def GetUserDB(self, request, context):
        # un, password (optional)
        user = None
        try:
            if request.password:
                self.cursor.execute("SELECT id, username, password FROM seller WHERE username = %s AND password = %s",(request.username, request.password))
                user = self.cursor.fetchone()
            else:
                self.cursor.execute("SELECT id, username, password FROM seller WHERE username = %s",(request.username, ))
                user = self.cursor.fetchone()       
        except Exception as e:
            print("Error in grpc customer DB server: ",e)
            return -1
        response = pb2.generalResponse() 
        response.msg = str(user)  
        return response
    
    
    def UpdateSellerFeedback(self, request, context):
        # seller_id,tu,td
        self.cursor.execute("UPDATE seller SET thumbs_up_count = %s, thumbs_down_count = %s WHERE id = %s",(request.tu,request.td, request.seller_id))
        response = pb2.generalResponse() 
        response.msg = str(1) 
        return response


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=200))
    pb2grpc.add_CustomersServicer_to_server(CustomerDB(),server)
    server.add_insecure_port("localhost:6080")
    
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()