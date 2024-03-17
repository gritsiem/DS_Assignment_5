# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: products.proto
# Protobuf Python Version: 4.25.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0eproducts.proto\x12\x08products\"\x81\x02\n\x12ProductItemMessage\x12\x11\n\tseller_id\x18\x01 \x01(\x05\x12\x13\n\x06prodid\x18\x02 \x01(\x05H\x00\x88\x01\x01\x12\x11\n\x04name\x18\x03 \x01(\tH\x01\x88\x01\x01\x12\x15\n\x08\x63\x61tegory\x18\x04 \x01(\x05H\x02\x88\x01\x01\x12\x16\n\tcondition\x18\x05 \x01(\tH\x03\x88\x01\x01\x12\x12\n\x05price\x18\x06 \x01(\x02H\x04\x88\x01\x01\x12\x15\n\x08quantity\x18\x07 \x01(\x05H\x05\x88\x01\x01\x12\x10\n\x08keywords\x18\x08 \x03(\tB\t\n\x07_prodidB\x07\n\x05_nameB\x0b\n\t_categoryB\x0c\n\n_conditionB\x08\n\x06_priceB\x0b\n\t_quantity\"E\n\x13ProductsListMessage\x12.\n\x08products\x18\x01 \x03(\x0b\x32\x1c.products.ProductItemMessage\"\x1e\n\x0fgeneralResponse\x12\x0b\n\x03msg\x18\x01 \x01(\t\"G\n\x1cSearchProductsRequestMessage\x12\x15\n\ritem_category\x18\x01 \x01(\t\x12\x10\n\x08keywords\x18\x02 \x03(\t\"\xd1\x01\n\x07Product\x12\n\n\x02id\x18\x01 \x01(\x05\x12\x11\n\titem_name\x18\x02 \x01(\t\x12\x11\n\tseller_id\x18\x03 \x01(\x05\x12\x15\n\ritem_category\x18\x04 \x01(\x05\x12\x10\n\x08keywords\x18\x05 \x03(\t\x12\x11\n\tcondition\x18\x06 \x01(\t\x12\x12\n\nsale_price\x18\x07 \x01(\t\x12\x10\n\x08quantity\x18\x08 \x01(\x05\x12\x17\n\x0fthumbs_up_count\x18\t \x01(\x05\x12\x19\n\x11thumbs_down_count\x18\n \x01(\x05\"D\n\x1dSearchProductsResponseMessage\x12#\n\x08products\x18\x01 \x03(\x0b\x32\x11.products.Product2\xfe\x03\n\x08Products\x12M\n\x10\x41\x64\x64SellerProduct\x12\x1c.products.ProductItemMessage\x1a\x19.products.generalResponse\"\x00\x12N\n\x11\x45\x64itSellerProduct\x12\x1c.products.ProductItemMessage\x1a\x19.products.generalResponse\"\x00\x12N\n\x11GetSellerProducts\x12\x1c.products.ProductItemMessage\x1a\x19.products.generalResponse\"\x00\x12P\n\x13RemoveSellerProduct\x12\x1c.products.ProductItemMessage\x1a\x19.products.generalResponse\"\x00\x12M\n\x10GetSellerRatings\x12\x1c.products.ProductItemMessage\x1a\x19.products.generalResponse\"\x00\x12\x62\n\rSearchProduct\x12&.products.SearchProductsRequestMessage\x1a\'.products.SearchProductsResponseMessage\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'products_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_PRODUCTITEMMESSAGE']._serialized_start=29
  _globals['_PRODUCTITEMMESSAGE']._serialized_end=286
  _globals['_PRODUCTSLISTMESSAGE']._serialized_start=288
  _globals['_PRODUCTSLISTMESSAGE']._serialized_end=357
  _globals['_GENERALRESPONSE']._serialized_start=359
  _globals['_GENERALRESPONSE']._serialized_end=389
  _globals['_SEARCHPRODUCTSREQUESTMESSAGE']._serialized_start=391
  _globals['_SEARCHPRODUCTSREQUESTMESSAGE']._serialized_end=462
  _globals['_PRODUCT']._serialized_start=465
  _globals['_PRODUCT']._serialized_end=674
  _globals['_SEARCHPRODUCTSRESPONSEMESSAGE']._serialized_start=676
  _globals['_SEARCHPRODUCTSRESPONSEMESSAGE']._serialized_end=744
  _globals['_PRODUCTS']._serialized_start=747
  _globals['_PRODUCTS']._serialized_end=1257
# @@protoc_insertion_point(module_scope)
