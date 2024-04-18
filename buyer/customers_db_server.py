from concurrent import futures
import grpc
import customers_pb2
import customers_pb2_grpc
from customers_db_model import CustomersDatabase

customers_db = CustomersDatabase()

class CustomersDbService(customers_pb2_grpc.CustomersServicer):
    def CreateAccount(self, request, context):
        username = request.username
        password = request.password
        name = request.name
        response = customers_db.create_account(username, password, name)
        return customers_pb2.generalResponse(msg = response)

    def Login(self, request, context):
        username = request.username
        password = request.password
        response = customers_db.login(username, password)
        return customers_pb2.generalResponse(msg = response)
    
    def GetBuyerId(self, request, context):
        username = request.username
        response = customers_db.get_buyer_id(username)
        # print(f"GetBuyerId Response at gRPC server: {response}")
        return customers_pb2.GetBuyerIdResponseMessage(buyer_id = response)
    
    def SetLoginState(self, request, context):
        buyer_id = request.buyer_id
        state = request.state
        response = customers_db.set_login_state(buyer_id, state)
        return customers_pb2.generalResponse(msg = response)
    
    def AddToCart(self, request, context):
        buyer_id = request.buyer_id
        product_id = request.product_id
        quantity = request.quantity
        response = customers_db.add_to_cart(buyer_id, product_id, quantity)
        return customers_pb2.generalResponse(msg = response)
    
    def RemoveItemFromCart(self, request, context):
        buyer_id = request.buyer_id
        product_id = request.product_id
        quantity = request.quantity
        response = customers_db.remove_item_from_cart(buyer_id, product_id, quantity)
        return customers_pb2.generalResponse(msg = response)
    
    def ClearCart(self, request, context):
        buyer_id = request.buyer_id
        response = customers_db.clear_cart(buyer_id)
        return customers_pb2.generalResponse(msg = response)
    
    def DisplayCart(self, request, context):
        buyer_id = request.buyer_id
        response = customers_db.display_cart(buyer_id)
        print(f"Display Cart Response at gRPC server: {response}")
        cart_items_list = []
        for cart_item in response:
            cart_items_list.append(customers_pb2.CartItem(product_id=cart_item[0],
                quantity=cart_item[1]
            )
        )
        return customers_pb2.DisplayCartResponseMessage(cart_items = cart_items_list)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=20))
    customers_pb2_grpc.add_CustomersServicer_to_server(CustomersDbService(), server)
    # server.add_insecure_port('[::]:50052')
    server.add_insecure_port('localhost:5070')
    server.start()
    print("Server started at localhost:5070")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()