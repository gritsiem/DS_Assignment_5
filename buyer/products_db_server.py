from concurrent import futures
import grpc
import sys
import products_pb2
import products_pb2_grpc
from products_db_model import ProductsDatabase
from products_db_replication import ReplicatedProductsDatabase

# products_db = ProductsDatabase()

class ProductsDbService(products_pb2_grpc.ProductsServicer):
    def __init__(self, replicated_db):
        self.replicated_db = replicated_db

    def SearchProduct(self, request, context):
        item_category = request.item_category
        keywords = request.keywords
        # response = products_db.search_products(item_category, keywords)
        response = self.replicated_db.search_products(item_category, keywords)
        print(f"Search response at grpc server: {response}")
        products_list = []
        for product in response:
            products_list.append(products_pb2.Product(id=product[0],item_name=product[1],
                seller_id=product[2],
                item_category=product[3],
                keywords=product[4],
                condition=product[5],
                sale_price=str(product[6]), 
                quantity=product[7],
                thumbs_up_count=product[8],
                thumbs_down_count=product[9]
            )
        )
        return products_pb2.SearchProductsResponseMessage(products = products_list)
    
    def GetProductDetails(self, request, context):
        product_id = request.product_id
        # response = products_db.get_product_details(product_id)
        response = self.replicated_db.get_product_details(product_id)
        print(f"Search response at grpc server: {response}")
        item_name = response[1]['name']
        sale_price = str(response[1]['price'])
        print(f"Item Name: ", item_name)
        print(f"Sale Price: ", sale_price)
        return products_pb2.GetProductDetailsResponseMessage(item_name = item_name, sale_price = sale_price)
    
    def UpdateFeedback(self, request, context):
        product_id = request.product_id
        feedback_type = request.feedback_type
        print(f"Feedback in the grpc db server: {type(feedback_type)} {feedback_type}")
        print(f"Product Id in the grpc db server: {type(product_id)} {product_id}")
        # response = products_db.update_feedback(product_id, feedback_type)
        try:
            response = self.replicated_db.update_feedback(product_id, feedback_type)
            print("Response for update product feedback in the db server: ", response)
            return products_pb2.generalResponse(msg = response)
        except Exception as e:
            print(f"Exception in UpdateFeedback: {str(e)}")
            return products_pb2.generalResponse(msg="Exception occurred: " + str(e))
    
    def GetSellerId(self, request, context):
        product_id = request.product_id
        # response = products_db.get_seller_id(product_id)
        response = self.replicated_db.get_seller_id(product_id)
        print("Response for seller id in the db server: ", response)
        return products_pb2.GetSellerIdResponseMessage(seller_id = response)
        
def serve():
    if len(sys.argv) != 4:
        print("Usage: python3 products_db_server.py selfAddress partnerAddresses db_name")
        sys.exit(1)

    selfAddress = sys.argv[1]
    partnerAddresses = sys.argv[2].split(',')
    db_name = sys.argv[3]

    replicated_db = ReplicatedProductsDatabase(selfAddress, partnerAddresses, db_name)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=20))
    # products_pb2_grpc.add_ProductsServicer_to_server(ProductsDbService(), server)
    products_pb2_grpc.add_ProductsServicer_to_server(ProductsDbService(replicated_db), server)
    # server.add_insecure_port('localhost:5080')
    server.add_insecure_port(selfAddress)
    server.start()
    # print("Server started at localhost:5080")
    print(f"Server started at {selfAddress}")
    server.wait_for_termination()

if __name__ == '__main__':
    serve() 