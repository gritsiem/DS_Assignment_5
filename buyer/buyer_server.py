import socket
import threading
import time
from flask import Flask, request, Response, jsonify
import os
import json
from products_db_model import ProductsDatabase
from customers_db_model import CustomersDatabase
from dotenv import load_dotenv
from zeep import Client
import sys

import grpc
import customers_pb2_grpc
import customers_pb2
import products_pb2_grpc
import products_pb2

load_dotenv()

app = Flask(__name__)

customers_db = CustomersDatabase()
products_db = ProductsDatabase('products_db')

def get_customers_stub():
    return customers_pb2_grpc.CustomersStub(grpc.insecure_channel('localhost:5070'))

def get_products_stub():
    # return products_pb2_grpc.ProductsStub(grpc.insecure_channel('localhost:5080'))
    return products_pb2_grpc.ProductsStub(grpc.insecure_channel('localhost:6000'))

def create_account_with_grpc(username, password, name):
    stub = get_customers_stub()
    request = customers_pb2.CreateAccountRequestMessage(username=username, password=password, name=name)
    response = stub.CreateAccount(request)
    return response

@app.route('/createaccount', methods = ['POST'])
def handle_create_account():
    data = request.json
    username = data['username']
    password = data['password']
    name = data['name']
    # result = customers_db.create_account(username, password, name)
    result = create_account_with_grpc(username, password, name).msg
    if "Account created successfully" in result:
        return jsonify({"message": result}), 200
    else:
        return jsonify({"message": result}), 401

def login_with_grpc(username, password):
    login_stub = get_customers_stub()
    login_request = customers_pb2.LoginRequestMessage(username=username, password=password)
    response = login_stub.Login(login_request)
    return response

def get_buyer_id_with_grpc(username):
    stub = get_customers_stub()
    request = customers_pb2.GetBuyerIdRequestMessage(username=username)
    response = stub.GetBuyerId(request)
    return response

def set_login_state_with_grpc(buyer_id, state):
    stub = get_customers_stub()
    request = customers_pb2.SetLoginStateRequestMessage(buyer_id=buyer_id, state = state)
    response = stub.SetLoginState(request)
    return response

@app.route('/login', methods = ['POST'])
def handle_login():
    data = request.json
    username = data['username']
    password = data['password']
    result = login_with_grpc(username, password).msg
    print(f"Login result in server: {result}")
    if "Login successful" in result:
        buyer_id = get_buyer_id_with_grpc(username).buyer_id
        print(f"Buyer Id in server: {buyer_id}")
        set_login_state_with_grpc(buyer_id, True)
        return jsonify({"message": result, "buyer_id": buyer_id}), 200
    else:
        return jsonify({"message": result}), 401

def search_product_with_grpc(item_category, keywords):
    stub = get_products_stub()
    request = products_pb2.SearchProductsRequestMessage(item_category=item_category, keywords= keywords)
    response = stub.SearchProduct(request)
    return response

@app.route('/search', methods = ['POST'])
def handle_search():
    print("In search fn in server...")
    data = request.json
    item_category = data['item_category']
    keywords = data['keywords']
    print(f"Keywords in server: {keywords}")
    result = search_product_with_grpc(item_category, [keywords])
    print(f"Search Result at server: {result}")
    products_list = []
    for product in result.products:
        keywords_list = list(product.keywords)
        product_dict = {
            "id": product.id,
            "item_name": product.item_name,
            "seller_id": product.seller_id,
            "keywords": keywords_list, 
            "condition": product.condition,
            "sale_price": product.sale_price,
            "quantity": product.quantity,
            "thumbs_up_count": product.thumbs_up_count,
            "thumbs_down_count": product.thumbs_down_count
        }
        products_list.append(product_dict)
    
    return jsonify(products_list)

def add_to_cart_with_grpc(buyer_id, product_id, quantity):
    stub = get_customers_stub()
    request = customers_pb2.AddToCartRequestMessage(buyer_id=buyer_id, product_id=product_id, quantity=quantity)
    response = stub.AddToCart(request).msg
    return response

@app.route('/additem', methods = ['POST'])
def handle_add_to_cart():
    data = request.json
    buyer_id = data['buyer_id']
    product_id = int(data['product_id'])
    quantity = int(data['quantity'])
    # result = customers_db.add_to_cart(buyer_id, product_id, quantity)
    result = add_to_cart_with_grpc(buyer_id, product_id, quantity)
    if "Item is added to the cart successfully" in result:
        return jsonify({"message": result}), 200
    else:
        return jsonify({"message": "Error adding an item to the cart"}), 401

def remove_item_from_cart_with_grpc(buyer_id, product_id, quantity):
    stub = get_customers_stub()
    request = customers_pb2.RemoveFromCartRequestMessage(buyer_id=buyer_id, product_id=product_id, quantity=quantity)
    response = stub.RemoveItemFromCart(request).msg
    return response

@app.route('/removeitem', methods = ['POST'])
def handle_remove_item_from_cart():
    data = request.json
    buyer_id = data['buyer_id']
    product_id = int(data['product_id'])
    quantity = int(data['quantity'])
    # result = customers_db.remove_item_from_cart(buyer_id, product_id, quantity)
    result = remove_item_from_cart_with_grpc(buyer_id, product_id, quantity)
    if "Item removed from cart" in result:
        return jsonify({"message": result}), 200
    else:
        return jsonify({"message": result}), 401

def clear_cart_with_grpc(buyer_id):
    stub = get_customers_stub()
    request = customers_pb2.ClearCartRequestMessage(buyer_id=buyer_id)
    response = stub.ClearCart(request).msg
    return response

@app.route('/clearcart', methods = ['POST'])
def handle_clear_cart():
    data = request.json
    buyer_id = data['buyer_id']
    # result = customers_db.clear_cart(buyer_id)
    result = clear_cart_with_grpc(buyer_id)
    if "Cart cleared" in result:
        return jsonify({"message": result}), 200
    else:
        return jsonify({"message": result}), 401

def display_cart_with_grpc(buyer_id):
    stub = get_customers_stub()
    request = customers_pb2.DisplayCartRequestMessage(buyer_id=buyer_id)
    response = stub.DisplayCart(request)
    print(f"Display Cart response at grpc client: {response}")
    return [(item.product_id, item.quantity) for item in response.cart_items]

def get_product_details_with_grpc(product_id):
    stub = get_products_stub()
    request = products_pb2.GetProductDetailsRequestMessage(product_id = product_id)
    response = stub.GetProductDetails(request)
    if response:  
        return {
            "name": response.item_name,
            "price": response.sale_price
        }
    return None

@app.route('/displaycart', methods = ['GET'])
def handle_display_cart():
    data = request.json
    buyer_id = data['buyer_id']
    # cart_items = customers_db.display_cart(buyer_id)
    response = display_cart_with_grpc(buyer_id)
    if not response:
        return jsonify({"message": "Your cart is empty"}), 200
    cart_display = []
    for product_id, quantity in response:
        product_detail = get_product_details_with_grpc(product_id)
        if product_detail:
            item_name = product_detail['name']
            sale_price = product_detail['price']
            cart_display.append(f"Product: {item_name}, Quantity: {quantity}, Unit Price: {sale_price}, Total price: {sale_price*quantity}")
    formatted_cart = "\n".join(f"{index + 1}. {item}" for index, item in enumerate(cart_display))
    if formatted_cart:
        return jsonify({"message": formatted_cart}), 200
    else:
        return jsonify({"message": "Error retrieving cart items"}), 401

@app.route('/sellerrating', methods = ['GET'])
def handle_get_seller_rating():
    data = request.json
    seller_id = data['seller_id']
    rating = customers_db.get_seller_rating(seller_id)
    if rating is not None:
        result = f"Seller Rating: Thumbs Up Count - {rating[0][0]}, Thumbs Down Count - {rating[0][1]}"
        return jsonify({"message": result}), 200
    else:
        return jsonify({"message": "Error getting seller rating"}), 401
    
def purchase_items(buyer_id):
    try:
        ordered_items = customers_db.get_purchased_items(buyer_id)
        if not ordered_items:
            return "No purchase was made."
            
        cart_display = []
        for product_id, quantity in ordered_items:
            product_detail = products_db.get_product_details(product_id)
            if product_detail:
                item_name = product_detail[product_id]['name']
                sale_price = product_detail[product_id]['price']
                cart_display.append(f"Product Id: {product_id}, Name: {item_name}, Quantity: {quantity}, Unit Price: {sale_price}, Total price: {sale_price*quantity}")

        formatted_cart = "\n".join(f"{index + 1}. {item}" for index, item in enumerate(cart_display))
        return formatted_cart
    except Exception as e:
        print(f"Error sending purchased items: {e}")

@app.route('/purchasehistory', methods = ['GET'])
def handle_purchase_history():
    data = request.json
    buyer_id = data['buyer_id']
    ordered_items = purchase_items(buyer_id)
    if ordered_items:
        return jsonify({"message": ordered_items}), 200
    else:
        return jsonify({"message": "Error retrieving purchase history"}), 401  

def has_provided_feedback_with_grpc(buyer_id, product_id):
    stub = get_customers_stub()
    request = customers_pb2.HasProvidedFeedbackRequestMessage(buyer_id = buyer_id, product_id = product_id) 
    response = stub.HasProvidedFeedback(request).has_provided
    print("Has Provided Feedback response from grpc: ", response)
    return response

def update_customer_feedback_with_grpc(buyer_id, product_id):
    stub = get_customers_stub()
    request = customers_pb2.UpdateProvideFeedbackRequestMessage(buyer_id = buyer_id, product_id = product_id) 
    response = stub.UpdateCustomerProvideFeedback(request).msg
    print("Update Provide Feedback response from grpc: ", response)
    return response

def update_feedback_with_grpc(product_id, feedback_type):
    stub = get_products_stub()
    request = products_pb2.UpdateFeedbackRequestMessage(product_id = product_id, feedback_type = feedback_type)
    response = stub.UpdateFeedback(request).msg
    print("Update Product Feedback response from grpc: ", response)
    return response

def get_seller_id_with_grpc(product_id):
    stub = get_products_stub()
    request = products_pb2.GetSellerIdRequestMessage(product_id = product_id)
    response = stub.GetSellerId(request).seller_id
    print("Seller Id response from grpc: ", response)
    return response

def update_seller_feedback_with_grpc(seller_id, feedback_type):
    stub = get_customers_stub()
    request = customers_pb2.UpdateSellerFeedbackRequestMessage(seller_id = seller_id, feedback_type = feedback_type) 
    response = stub.UpdateSellerFeedbackFromBuyer(request)
    print("Update Seller Feedback response from grpc: ", response)
    return response

@app.route('/provide_feedback', methods = ['POST'])
def handle_provide_feedback():
    data = request.json
    buyer_id = int(data['buyer_id'])
    product_id = int(data['product_id'])
    feedback_type = int(data['feedback_type'])
    print(f"[SERVER] BuyerId: {buyer_id}, product_id: {product_id}, feedback_type: {feedback_type}")

    feedback_provided = has_provided_feedback_with_grpc(buyer_id, product_id)
    # print("Feedback provided: ", feedback_provided)
    if feedback_provided:
        return jsonify({"message": "Feedback already provided for this product."}), 400
    
    cart_item_update_result  = update_customer_feedback_with_grpc(buyer_id, product_id)
    feedback_result = update_feedback_with_grpc(product_id, feedback_type)

    seller_id = get_seller_id_with_grpc(product_id)
    seller_update_result = update_seller_feedback_with_grpc(seller_id, feedback_type)

    if feedback_result and cart_item_update_result and seller_update_result:
        return jsonify({"message": "Feedback updated successfully."}), 200
    else:
        return jsonify({"error": "Failed to update feedback."}), 500

@app.route('/makepurchase', methods = ['POST'])
def handle_make_purchase():
    data = request.json
    print(f"Data in server..: {data}")
    buyer_id = data['buyer_id']
    name = data['name']
    credit_card_number = data['credit_card_number']
    expiration_date = data['expiration_date']
    soap_client = Client('http://localhost:8000/?wsdl')
    response = soap_client.service.make_purchase(id=buyer_id, name = name, credit_card_number=credit_card_number, expiration_date=expiration_date)

    # response = spyne_application.make_purchase(buyer_id, credit_card_number, expiration_date)
    print(f"Make Purchase Response: {response}")
    if response:
        return jsonify({"message": response}), 200
    else:
        return jsonify({"message": "Error making the payment"}), 401  

@app.route('/logout', methods = ['POST'])
def handle_logout():
    data = request.json
    buyer_id = data['buyer_id']
    result = customers_db.set_login_state(buyer_id, False)
    if "Update successful" in result:
        return jsonify({"message": "Logout successful"}), 200
    else:
        return jsonify({"message": "Logout failed"}), 401  
    
    # def handle_inactivity(self, buyer_id, conn):
    #     print("Handling inactivity...")
    #     self.handle_logout(buyer_id, conn)


    # def handle_client(self, conn, addr):
    #     print(f"[NEW CONNECTION] {addr} connected.")
    #     connected = True

    #     inactivityTimer = time.time()

    #     while connected:
    #         try:
    #             msg_length = conn.recv(self.HEADER).decode(self.FORMAT)
    #             if msg_length:
    #                 msg_length = int(msg_length)
    #                 msg = conn.recv(msg_length).decode(self.FORMAT)
    #                 print(f"Message in [Server]: {msg}")

    #                 # inactivity check
    #                 previoustime = inactivityTimer
    #                 inactivityTimer = time.time()
                    
    #                 if msg.startswith("CREATE_ACCOUNT"):
    #                     _, username, password, name = msg.split()
    #                     self.handle_create_account(username, password, name, conn)
    #                 elif msg.startswith("LOGIN"):
    #                     _, username, password = msg.split()
    #                     self.handle_login(username, password, conn)
    #                 elif(inactivityTimer - previoustime > 20):
    #                     print("Should log out now")
    #                     self.handle_inactivity(msg.split()[1], conn)
    #                 elif msg.startswith("SEARCH"):
    #                     msg_split = msg.split()
    #                     item_category = msg_split[1]
    #                     keywords = msg_split[2:]
    #                     # print(f"Item_category: {item_category} and Keywords: {keywords}")
    #                     self.handle_search(item_category, keywords, conn)
    #                 elif msg.startswith("ADD_TO_CART"):
    #                     _, buyer_id, product_id, quantity = msg.split()
    #                     self.handle_add_to_cart(buyer_id, product_id, quantity, conn)
    #                 elif msg.startswith("REMOVE_ITEM_FROM_CART"):
    #                     _, buyer_id, product_id, quantity = msg.split()
    #                     self.handle_remove_item_from_cart(buyer_id, product_id, quantity, conn)
    #                 elif msg.startswith("CLEAR_CART"):
    #                     buyer_id = msg.split("CLEAR_CART ")[1]
    #                     self.handle_clear_cart(buyer_id, conn)
    #                 elif msg.startswith("DISPLAY_CART"):
    #                     buyer_id = msg.split("DISPLAY_CART ")[1]
    #                     self.handle_display_cart(buyer_id, conn)
    #                 elif msg.startswith("GET_SELLER_RATING"):
    #                     seller_id = msg.split("GET_SELLER_RATING ")[1]
    #                     self.handle_get_seller_rating(seller_id, conn)
    #                 elif msg.startswith("PURCHASE_HISTORY"):
    #                     buyer_id = msg.split("PURCHASE_HISTORY ")[1]
    #                     self.handle_purchase_history(buyer_id, conn)
    #                 elif msg.startswith("PROVIDE_FEEDBACK"):
    #                     buyer_id = msg.split("PROVIDE_FEEDBACK ")[1]
    #                     self.handle_provide_feedback(buyer_id, conn)
    #                 elif msg.startswith("LOGOUT"):
    #                     _, buyer_id = msg.split()
    #                     self.handle_logout(buyer_id, conn)
    #                 elif msg == self.DISCONNECT_MSG:
    #                     print("[In server] Disconnecting...")
    #                     connected = False
    #                 print(f'[{addr}] {msg}')
    #         except Exception as e:
    #             print(f"An error occurred: {e}")
    #             connected = False 

    #     conn.close()

if __name__ == "__main__":
    print("Server system argument: ", sys.argv)
    if len(sys.argv) > 2:
        app.run(host=sys.argv[1], port=int(sys.argv[2]), debug=True)
    else:
        app.run(host = "0.0.0.0", port=int(os.getenv("PORT")), debug=True)
    
