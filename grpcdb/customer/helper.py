from dotenv import load_dotenv
import psycopg2
import os

load_dotenv()


class Helper:
    def __init__(self, pid):
        self.loadDB(pid)

    def by_name(self, method_name, request):
        if method_name.find("RegisterSellerDB")!=-1:
            return self._registerSellerDB(request)
        if method_name.find("UpdateSellerFeedback")!=-1:
            return self._updateSellerFeedback(request)
    def loadDB(self,pid):
        pw = os.getenv('PASSWORD')
        self.connection = psycopg2.connect(f"dbname='customers_db{pid}' user='postgres' host='localhost' password='{pw}'")
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
    def _registerSellerDB(self,request):
        try:
            self.cursor.execute("INSERT INTO seller (username, password) VALUES \
                    (%s, %s) returning id",(request.username, request.password))
            newid = self.cursor.fetchone()[0]
        except Exception as e:
            print("Error: RegisterCustomerDB -- ",e)
            return -1

        print("last row id",newid)
        self.connection.commit()

        return newid
    def _gettUserDB(self, request):
        # un, password (optional)
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
        return user
    def _updateSellerFeedback(self, request):
        self.cursor.execute("UPDATE seller SET thumbs_up_count = %s, thumbs_down_count = %s WHERE id = %s",(request.tu,request.td, request.seller_id))
