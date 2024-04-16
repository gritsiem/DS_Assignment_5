# DS_Assignment_4

## Description
This project builds on the E-commerce [full stack project](https://github.com/gritsiem/DS_Assignment_2).

In this setup, we focus on creating and managing replicas of our existing server-side components. We replicate the REST servers and DBs for our application and manage them using group communication protocols based on TOTEM and Raft.
### Architecture
There are 7 components: 
- 2 clients: Seller and Buyer
    There can be any number of client running.
- 2 REST servers: Seller and Buyer 

    There are 4 replicas of each seller and buyer server. These are stateless servers, therefore we do not manage their replication. We just make sure that the clients randomly connect to only one of these servers.

    Servers will keep restarting if they crash. Client will reconnect to a different server in case it faces a connection error.  
- 2 GRPC exposed PostgreSQL DBs: Customers and Products
  Both the Customers and Products DB have 5 replicas
- A mock payment SOAP server

Each client is connected to a server by randomly picking one of the available servers. All the buyer servers are connected to the SOAP server.  

### Database Group Communication
For Customer Database, rotating sequencer atomic broadcast protocol is used for the group communication. 

For Products Database, PySyncObj is used for the group communication. PySyncObj is one of the open-source implementation of the Raft in Python.  
#### Assumptions

## How to Set Up 
### Local setup (have one machine for all components)
#### Seller side
Clone project and go to root directory in the command line.

Start a server group. For changing the ports, change the "SELLER_SERVERS" environment variable. ([See example](./dotenv_example.txt))
```
python seller/server/start_server_group.py
```
Use the client scripts to start "n" number of clients. Each client randomly chooses one of the seller servers to connect to.
```
python seller/start_clients.py -n 1
```

### CloudLab Setup
#### Seller side
The exact configuration changes depending on how you structure the network. However, the following guidelines hold
1. Upload the ```root/seller/server``` folder in all intended servers. Get the IP addresses for each. Update the IP addresses in the .env file.
2. Replicate the .env file in each seller client machine and then start the client from the terminal using:
```
python seller/seller_client.py
```


#### To do
- handle execute - include pid, and if pid = self pid then continue execution?
- figure out data structures - request, sequence queues + histories - request to queue mapping
- figure out metadata - aru i guess --------- dang it
