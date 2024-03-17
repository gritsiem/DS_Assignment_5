import products_pb2_grpc as pb2grpc
import products_pb2 as pb2

import time
import grpc
import os
from ast import literal_eval


class ProductInterfaceGRPC:
    counter = 0
    def __init__(self):
        '''
        Initializes required parameters for socket connection and also begins communication. 
        '''
        self._PORT = "5080"
        self._SERVER = "localhost"
        self._ADDRESS = self._SERVER+":"+self._PORT
        self.__stub = None
        self.inititate_connection()

    def inititate_connection(self):
        self.channel = grpc.insecure_channel(self._ADDRESS,options=(('grpc.enable_http_proxy',0),))
        self.__stub = pb2grpc.ProductsStub(self.channel)
        ProductInterfaceGRPC.counter+=1
        print(ProductInterfaceGRPC.counter)

    def addProduct(self, sellerid, name, category, condition, price, quantity, keywords):
        insertRequest = pb2.ProductItemMessage(seller_id= sellerid,name = name, category = category,  condition = condition,  price = price,  quantity = quantity,  keywords = keywords)
        response = self.__stub.AddSellerProduct(insertRequest)
        return response.msg
    
    def editProduct(self, prodid, price, sellerid):
        try:
            editRequest = pb2.ProductItemMessage(seller_id = sellerid, prodid = prodid, price = price)
            response = self.__stub.EditSellerProduct(editRequest)     
        except Exception as e:
            print("exception", e)
            return -1
        
        if(response.msg == "-1"):
            return -1
        return response.msg
    
    def removeProduct(self, prodid, seller_id):
        # newid = uuid.uuid1()
        try:
            deleteRequest = pb2.ProductItemMessage(prodid = prodid, seller_id = seller_id)
            response = self.__stub.RemoveSellerProduct(deleteRequest)     
            print("ID: ",response)
            # self.table.append({"id": newid, "username": un,"password":pw})
        except Exception as e:
            print("exception")
            return -1
        if int(response.msg) == -1:
            return -1
        return prodid
    

        
    def getProducts(self, sellerid):
        # print(ProductInterfaceGRPC.counter)
        products = []
        #try:
        getProductsRequest = pb2.ProductItemMessage(seller_id = sellerid)
        response = self.__stub.GetSellerProducts(getProductsRequest)     
        # Fetch all
        # print("whoop ",products.msg)
        products = literal_eval(response.msg)
        return products 
    
    def getRatings(self,sellerid):
        try:
            # print("seller id", sellerid)
            getRatingsRequest = pb2.ProductItemMessage(seller_id=sellerid)
            response = self.__stub.GetSellerRatings(getRatingsRequest)     
            # Fetch all
            feedbacks = response.msg
        except Exception as e:
            print(e)
            return -1
        thumbsups, thumbsdowns = literal_eval(feedbacks)

        return thumbsups, thumbsdowns
    def close_conn(self):
        # self.channel.close()
        pass

if __name__ == "__main__":
    client = ProductInterfaceGRPC()
    # print(client.addProduct(2, "randomproduct", 9, "New", 100.00, 3, ['random',"rand"]))
    # print(client.editProduct(2,25.00,4))
    # print(client.getProducts(1))
    # print(client.removeProduct(9,2))
    print(client.getRatings(3))