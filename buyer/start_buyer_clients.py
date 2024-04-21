import multiprocessing
import subprocess
# import time

def start_client_process(client_id):
    try:
        print(f"Client {client_id} is starting.")

        # command = ['gnome-terminal', '--', 'python3', 'buyer_client.py', str(client_id)]
        # command = ['xterm', '-e', f'python3 buyer_client.py {client_id}']
        # subprocess.Popen(command)
        command = f'''
        tell application "Terminal"
            do script "python3 Projects/DistSystems/DS_Assignment_4/buyer/buyer_client.py {client_id}"
        end tell
        '''
        subprocess.run(['osascript', '-e', command])

        # time.sleep(5)
        # print(f"Client {client_id} completed its work.")
    except Exception as e:
        print(f"Client {client_id} encountered an error: {e}")

if __name__ == "__main__":
    number_of_clients = 3
    processes = [multiprocessing.Process(target=start_client_process, args=(i,)) for i in range(number_of_clients)]

    for process in processes:
        process.start()

    for process in processes:
        process.join()

    # print("All clients have completed their operations")
