import argparse
import threading
import os

def start_client(i):
    print("Client: ", i)
    os.system('start /wait cmd /K "python seller/seller_client".py')
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_clients", "-n", required=True, help="Number of clients to start", type=int)
    args = parser.parse_args()

    number_of_clients = args.num_clients

    for i in range(0,number_of_clients):
        thread = threading.Thread(target = start_client, args=(i,))
        thread.start()
        