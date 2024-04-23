from pysyncobj import SyncObj, replicated
from products_db_model import ProductsDatabase

class ReplicatedProductsDatabase(SyncObj):
    def __init__(self, selfAddress, partnerAddresses, db_name):
        print(f"Intializing the instance in the replicated class: {selfAddress} {partnerAddresses} {db_name}")
        super(ReplicatedProductsDatabase, self).__init__(selfAddress, partnerAddresses)
        self.products_db = ProductsDatabase(db_name)  # Use existing class

    @replicated
    def update_feedback(self, product_id, feedback_type):
        print("Update feedback request intiated in the replicated class.....")
        # return self.products_db.update_feedback(product_id, feedback_type)
        return "Feedback - modified"

    def get_seller_id(self, product_id):
        # Non-replicated method, used for read-only access
        return self.products_db.get_seller_id(product_id)

    def get_product_details(self, product_id):
        return self.products_db.get_product_details(product_id)
    
    def close(self):
        self.products_db.close()




