import argparse
import threading
import os
from dotenv import load_dotenv

load_dotenv()

SELLER_IPS = os.getenv('SELLER_SERVERS').strip().split("\n")
        

def start_group(ip):
    # print("Server started on: ", i)
    host,port = ip.split(":")
    # os.system(f'start /wait cmd /K "python seller/seller_client {host} {port}".py')
    os.system(f'cmd /K "python seller/server/seller_server_restful.py {host} {port}"')

if __name__ == "__main__":

    for ip in SELLER_IPS:
        thread = threading.Thread(target = start_group, args=(ip,))
        thread.start()
        