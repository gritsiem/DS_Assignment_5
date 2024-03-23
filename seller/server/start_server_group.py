import threading
import subprocess
import os
from dotenv import load_dotenv

load_dotenv()

SELLER_IPS = os.getenv('SELLER_SERVERS').strip().split("\n")
        

def start_group(ip):
    # os.system(f'start /wait cmd /K "python seller/seller_client {host} {port}".py')
    # os.system(f'cmd /K "python seller/server/seller_server_restful.py {host} {port}"')
    while True:
        try:
            host,port = ip.split(":")
            cmd = f"python seller/server/seller_server_restful.py {host} {port}".split()
            subprocess.run(cmd, check = True, shell=True)
        except Exception as e: # except subprocess.CalledProcessError:
            print (f"[{ip}]: ERROR -- ", e)
            print("Restarting server...")

if __name__ == "__main__":

    for ip in SELLER_IPS:
        thread = threading.Thread(target = start_group, args=(ip,))
        thread.start()
        