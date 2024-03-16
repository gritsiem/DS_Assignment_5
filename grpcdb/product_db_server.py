import psycopg2
from concurrent import futures
import time
import pickle
import os
from dotenv import load_dotenv


import grpc
import products_pb2 as pb2
import products_pb2_grpc as pb2grpc

from ast import literal_eval
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
class ProductsDB:
    count=0
    def __init__(self):
        '''
        Initializes for binding server to port and keeps track of active connections over all clients 
        '''
        self.HOST = "localhost"
        self.PORT = 5080
        self.ADDRESS = (self.HOST, self.PORT)
        self.loadDB()

    def loadDB(self):
        pw = os.getenv('PASSWORD')
        self.connection = psycopg2.connect(f"dbname='products_db' user='postgres' host='localhost' password='{pw}'")
        self.cursor = self.connection.cursor()

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS product (
                id SERIAL PRIMARY KEY,
                item_name VARCHAR(32),
                seller_id INTEGER,
                item_category INTEGER CHECK (item_category >= 0 AND item_category <= 9),
                keywords VARCHAR(8) [],  
                condition VARCHAR(10) CHECK (condition IN ('New', 'Used')),
                sale_price DECIMAL,
                quantity INTEGER,
                thumbs_up_count INTEGER DEFAULT 0,
                thumbs_down_count INTEGER DEFAULT 0,
                CHECK (array_length(keywords, 1) <= 5)
            );''')

    def printTable(self,table):
        for row in table:
            print(row)
    
    def AddSellerProduct(self, request, context):
        # sellerid, name, category, condition, price, quantity, keywords
        keywords = list_from_repeated(request.keywords)
        try:
            print("inserting")
            self.cursor.execute("INSERT INTO product(seller_id, item_name , item_category, condition, sale_price, quantity, keywords) VALUES \
                                (%s, %s, %s,%s,%s,%s, %s) returning id",(request.seller_id, request.name, request.category, request.condition, request.price, request.quantity, keywords))
            self.connection.commit() 
        except Exception as e:
            print("Error: AddSellerProduct -- ",e)
            return -1
        prodid = self.cursor.fetchone()[0]
        response = pb2.generalResponse()
        response.msg = str(prodid)
        return response

    
    def EditSellerProduct(self, request,context):
        # prodid, price, sellerid
        try:
            self.cursor.execute("UPDATE product SET sale_price = %s WHERE id = %s AND seller_id= %s",(request.price, request.prodid, request.seller_id))
            self.connection.commit()
        except Exception as e:
            print("Error: EditSellerProduct -- ",e)
            return -1

        response = pb2.generalResponse()
        
        res = self.cursor.rowcount
        if(res == 0):
            response.msg = str(-1)
            return response
        
        response.msg = str(request.prodid)
        return response
    
    def RemoveSellerProduct(self, request,context):
        # prodid, seller_id
        try:
            self.cursor.execute("DELETE FROM product WHERE id = %s AND seller_id= %s",(request.prodid, request.seller_id))
            self.connection.commit()
        except Exception as e:
            print("Error: RemoveSellerProduct -- ",e)
            return -1
        
        response = pb2.generalResponse()

        res = self.cursor.rowcount
        if(res == 0):
            response.msg = str(-1)
            return response
        
        response.msg = str(request.prodid)
        return response
        
    def GetSellerProducts(self, request,context):
        # sellerid
        products = []
        response = pb2.generalResponse()
        try:
            self.cursor.execute("SELECT id, item_name, item_category, condition, sale_price, quantity FROM product WHERE seller_id = %s", (request.seller_id,))
            products = self.cursor.fetchall()
            self.connection.commit()
        except:
            response.msg = str([])
            return response

        response.msg = str(products)
        return response 
    
    def GetSellerRatings(self,request,context):
        # sellerid
        try:
        # print("seller id", sellerid)
            self.cursor.execute("SELECT SUM(thumbs_up_count), SUM(thumbs_down_count) FROM product WHERE seller_id = %s", (request.seller_id,))
            feedback = self.cursor.fetchone()
            self.connection.commit()
        except Exception as e:
            print("Error: GetSellerRatings -- ",e)
            return -1
        response = pb2.generalResponse()
        response.msg = str(feedback)
        return response

def list_from_repeated(field):
        return [val for val in field]


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=200))
    pb2grpc.add_ProductsServicer_to_server(ProductsDB(),server)
    server.add_insecure_port("localhost:5080")
    
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()