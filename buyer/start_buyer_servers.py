import subprocess
import os
from dotenv import load_dotenv
import time

load_dotenv()

BUYER_IPS = os.getenv('BUYER_SERVERS').strip().split("\n")
        
# processes = []
processes = {}

def start_server(host, port):
    try:
        process = subprocess.Popen(['python', 'buyer_server.py', host, str(port)])
        print(f"Started buyer_server on {host}:{port}")
        return process
    except Exception as e:
        print(f"[{host}:{port}] ERROR -- ", e)

def get_host_and_port():
    for ip in BUYER_IPS:
        host,port = ip.split(":")
        process = start_server(host, port)
        # processes.append(process)
        processes[ip] = process

def monitor_and_restart_and_terminate():
    try:
        while True:
            for key, process in list(processes.items()):
                if process.poll() is not None: 
                    print(f"Server {key} has stopped. Restarting...")
                    host, port = key.split(':')
                    processes[key] = start_server(host, port)  # Restart the server
            time.sleep(10)  #Checks every 10 seconds
    except KeyboardInterrupt:
        # Handle Ctrl-C to terminate all processes
        for key, process in list(processes.items()):
            process.terminate()
            process.wait()
        print("Terminated all buyer server instances")

if __name__ == "__main__":
    get_host_and_port()
    monitor_and_restart_and_terminate()
    # try:
    #     for process in processes:
    #         process.wait()
    # except KeyboardInterrupt:
    # # Handle Ctrl-C to terminate all processes
    #     for process in processes:
    #         process.terminate()
    #         process.wait()
    # print("Terminated all buyer server instances.")
   
        