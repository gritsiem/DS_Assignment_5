'''
Client side of the seller functionality of the E-Market application
Client can 
- start connection to the seller server.
- receive messages from the server
- send messages to server
- Additionally an option to generate client side inputs automatically / use actual user input
'''
import random
import os
import requests
import time
import threading
from dotenv import load_dotenv

load_dotenv()
class Client():
    __servers = os.getenv('SELLER_SERVERS').strip().split("\n")
        
    def __init__(self):
        self.__server = random.choice(Client.__servers)
        self.__home = "http://"+ self.__server
        print("Connecting to ", self.__home)
        self.__URLS= {'home':self.__home,
            'login': self.__home+'/login',
            'register': self.__home+'/register',
            'products': self.__home+'/products',   
            'ratings': self.__home+'/ratings',         
            'logout': self.__home+'/logout',         
        }

        self.__current_function = None
        self.__ERRORS={
            'BAD_CHOICE': "Please choose one of the given options"
        }
        self.currentError = None
        self.__token=None
        self.active = True
        s = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries = 5)
        s.mount("http://",adapter)
        # self.inactivityThread = threading.Thread(target = self.sessionTimer)
        self.handleSession()
        # self.inactivityThread.start()
        
    def sessionTimer(self):
        time.sleep(300)
        print("Loggin out due to inactivity...")
        self.__token = None
        self.__current_function==None
        pass
    def login(self):
        un = input("Please enter username: ")
        pw = input("Please enter password: ")
        # un = "user1"
        # pw = "userone"
        resp = requests.post(self.__URLS["login"], data={"username":un, "password":pw})
        resp = resp.json()
        self.loggedIn = True
        self.__token= (resp['data'])["token"]
        return resp["msg"]

    def register(self):
        isValid = False
        while not isValid:
            un = input("Enter username (32 letters max): ")
            pw = input("Enter password (6 letters minimum): ")

            if(len(un.strip())<=32 and len(pw.strip())>=6):
                isValid = True
            
            if not isValid:
                print("Please enter valid username and password")

        resp = requests.post(self.__URLS["register"], data={"username":un, "password":pw})
        resp = resp.json()
        self.__token= (resp['data'])["token"]
        return resp["msg"]

    def getProducts(self):
        resp = None
        resp = requests.get(self.__URLS["products"], data={"token" : self.__token})
        # print("Error is here")
        return resp.json()["msg"] if resp else " "

    def addProduct(self):
        isValid = False

        while not isValid:
            name = input("You are adding a new product. Please enter the following:\n" + "Name of the product (32 characters): ")
            cat = input("Category ( Choose a value 0-9 ): ")
            condition = input("Condition ( 1 - New or 2 - Used ): ")
            price = input("Price: ")
            quantity = input("Quantity: ")
            keywords = input("At most 5, seperated by commas: ")
            keywords = keywords.split(",")

            validationMsg = ""
            isValid = True
            if len(name)>32:
                isValid = False
                validationMsg += "Name is too long\n"

            try:
                cat = int(cat)
            except:
                isValid = False
                validationMsg += "Category has to be a number\n"
            else:
                if cat<0 and cat>9:
                        isValid = False
                        validationMsg += "Category has to be a number between 0 and 9\n"

            try:
                condition = int(condition)
            except:
                isValid = False
                validationMsg += "Condition has to be number 1 or 2\n"
            else:
                if condition!=1 and condition!=2:
                    isValid = False
                    validationMsg += "Condition should be either 1 or 2\n"

            
            try:
                price = float(price)
            except:
                isValid = False
                validationMsg += "Price should be a number\n"
            try:
                quantity = int(quantity)
            except:
                isValid = False
                validationMsg += "Quantity should be a number\n"

            if(len(keywords)>5):
                isValid = False
                validationMsg += "You can only put 5 keywords.\n"
            for kw in keywords:
                if len(kw)>8:
                    isValid = False
                    validationMsg += "Please keep keywords length to 8 characters.\n"
                    break
            if not isValid:
                print("Please correct the following problems:\n", validationMsg)
   
        condition = 'New' if int(condition) ==1 else "Used" 
        newProduct = {
           "name":name, "category":cat,"condition":condition,"price":price,"quantity":quantity, "keywords" : keywords
        }
        keywords = ",".join(keywords)
        resp = requests.post(self.__URLS["products"], data={"token" : self.__token,  "name":name, "category":cat,"condition":condition,"price":price,"quantity":quantity, "keywords" : keywords })
        print(resp)
        return resp.json()["msg"]
        
    def editProduct(self):
        
        isValid = False

        while not isValid:
            productid = input("To edit a product, please enter the following:\nID of the product: ")
            price = input("Updated Price: ")

            isValid = True
            validationMsg = ""
            try:
                productid = int(productid)
            except:
                isValid = False
                validationMsg += "ProductId should be a number\n"
            try:
                price = float(price)
            except:
                isValid = False
                validationMsg += "Price should be a number\n"

            if not isValid:
                print("Please correct the following problems:\n", validationMsg)
        resp = requests.put(f"{self.__URLS['products']}/{productid}", data={"token" : self.__token, "price":price})
        print(resp)
        return resp.json()["msg"]

    def removeProduct(self):
        isValid = False

        while not isValid:
            productid = input("To remove a product, please enter the ID of the product: ")

            isValid = True
            validationMsg = ""
            try:
                productid = int(productid)
            except:
                isValid = False
                validationMsg += "ProductId should be a number\n"
            if not isValid:
                print(validationMsg)

        resp = requests.delete(f"{self.__URLS['products']}/{productid}", data={"token" : self.__token})
        print(resp)
        return resp.json()["msg"]
    
    def getRatings(self):
        resp = requests.get(self.__URLS["ratings"], data={"token" : self.__token})
        return resp.json()["msg"]
    def logout(self):
        self.__token = None
        self.__current_function=None
        print("User logged out")
        return requests.get(self.__URLS["logout"])
    
    def home(self):
        return requests.get(self.__URLS["home"])
    
    def sendRequest(self, fn=None):
        if self.__current_function==None:
            return self.home()
        
        return self.__current_function()
    
    def getAction(self,msg):
        self.currentError = None
        if self.__current_function==None:
            if(msg!=str(1) and msg!=str(2) and msg!=str(3)):
                self.currentError = self.__ERRORS["BAD_CHOICE"]
                return -1
            if (msg==str(1)):
                self.__current_function=self.login
            if (msg==str(2)):
                self.__current_function=self.register
            if (msg==str(3)):
                self.active=False
                print("Exiting...")
        if self.__token:
            print("here", msg)
            match msg:
                case "1":
                   self.__current_function=self.getProducts 
                case "2":
                   self.__current_function=self.addProduct
                case "3":
                   self.__current_function=self.editProduct
                case "4":
                   self.__current_function=self.removeProduct 
                case "5":
                   self.__current_function=self.getRatings 
                case "6":
                   self.__current_function=self.logout 
                case _:
                    self.currentError = self.__ERRORS["BAD_CHOICE"]
                    return -1

        return 0

    def printError(self):
        print(self.currentError)

    def updateServer(self):
        newserver = Client.__servers[:]
        newserver.remove(self.__server)
        newip = random.choice(newserver)
        self.__home = "http://"+ newip

        self.__URLS= {'home':self.__home,
            'login': self.__home+'/login',
            'register': self.__home+'/register',
            'products': self.__home+'/products',   
            'ratings': self.__home+'/ratings',         
            'logout': self.__home+'/logout',         
        }
        self.__current_function = None

        print("Now connected to :", newip)
    
    def handleSession(self):
        while self.active:
            try:
                response = self.sendRequest()
            except  requests.ConnectionError:
                self.updateServer()
                continue

            # print("after")
            if type(response) is str:
                print(response)
            else:
                print(response.text)
            
            msg = input()  
            x = self.getAction(msg)

            while self.currentError != None:
                if(x==-1):
                    self.printError()
                msg = input()  
                x = self.getAction(msg)





# when running from console
if __name__ == "__main__":
    conn = Client()