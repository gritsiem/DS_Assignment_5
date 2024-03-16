from concurrent import futures
import grpc
import products_pb2
import products_pb2_grpc
from products_db_model import ProductsDatabase

products_db = ProductsDatabase()

class ProductsDbService(products_pb2_grpc.ProductsServicer):
    def SearchProduct(self, request, context):
        item_category = request.item_category
        keywords = request.keywords
        response = products_db.search_products(item_category, keywords)
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

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=20))
    products_pb2_grpc.add_ProductsServicer_to_server(ProductsDbService(), server)
    server.add_insecure_port('localhost:5080')
    server.start()
    print("Server started at localhost:5080")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()