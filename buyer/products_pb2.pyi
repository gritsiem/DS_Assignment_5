from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ProductItemMessage(_message.Message):
    __slots__ = ("seller_id", "prodid", "name", "category", "condition", "price", "quantity", "keywords")
    SELLER_ID_FIELD_NUMBER: _ClassVar[int]
    PRODID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    CONDITION_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    KEYWORDS_FIELD_NUMBER: _ClassVar[int]
    seller_id: int
    prodid: int
    name: str
    category: int
    condition: str
    price: float
    quantity: int
    keywords: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, seller_id: _Optional[int] = ..., prodid: _Optional[int] = ..., name: _Optional[str] = ..., category: _Optional[int] = ..., condition: _Optional[str] = ..., price: _Optional[float] = ..., quantity: _Optional[int] = ..., keywords: _Optional[_Iterable[str]] = ...) -> None: ...

class ProductsListMessage(_message.Message):
    __slots__ = ("products",)
    PRODUCTS_FIELD_NUMBER: _ClassVar[int]
    products: _containers.RepeatedCompositeFieldContainer[ProductItemMessage]
    def __init__(self, products: _Optional[_Iterable[_Union[ProductItemMessage, _Mapping]]] = ...) -> None: ...

class generalResponse(_message.Message):
    __slots__ = ("msg",)
    MSG_FIELD_NUMBER: _ClassVar[int]
    msg: str
    def __init__(self, msg: _Optional[str] = ...) -> None: ...

class SearchProductsRequestMessage(_message.Message):
    __slots__ = ("item_category", "keywords")
    ITEM_CATEGORY_FIELD_NUMBER: _ClassVar[int]
    KEYWORDS_FIELD_NUMBER: _ClassVar[int]
    item_category: str
    keywords: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, item_category: _Optional[str] = ..., keywords: _Optional[_Iterable[str]] = ...) -> None: ...

class Product(_message.Message):
    __slots__ = ("id", "item_name", "seller_id", "item_category", "keywords", "condition", "sale_price", "quantity", "thumbs_up_count", "thumbs_down_count")
    ID_FIELD_NUMBER: _ClassVar[int]
    ITEM_NAME_FIELD_NUMBER: _ClassVar[int]
    SELLER_ID_FIELD_NUMBER: _ClassVar[int]
    ITEM_CATEGORY_FIELD_NUMBER: _ClassVar[int]
    KEYWORDS_FIELD_NUMBER: _ClassVar[int]
    CONDITION_FIELD_NUMBER: _ClassVar[int]
    SALE_PRICE_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    THUMBS_UP_COUNT_FIELD_NUMBER: _ClassVar[int]
    THUMBS_DOWN_COUNT_FIELD_NUMBER: _ClassVar[int]
    id: int
    item_name: str
    seller_id: int
    item_category: int
    keywords: _containers.RepeatedScalarFieldContainer[str]
    condition: str
    sale_price: str
    quantity: int
    thumbs_up_count: int
    thumbs_down_count: int
    def __init__(self, id: _Optional[int] = ..., item_name: _Optional[str] = ..., seller_id: _Optional[int] = ..., item_category: _Optional[int] = ..., keywords: _Optional[_Iterable[str]] = ..., condition: _Optional[str] = ..., sale_price: _Optional[str] = ..., quantity: _Optional[int] = ..., thumbs_up_count: _Optional[int] = ..., thumbs_down_count: _Optional[int] = ...) -> None: ...

class SearchProductsResponseMessage(_message.Message):
    __slots__ = ("products",)
    PRODUCTS_FIELD_NUMBER: _ClassVar[int]
    products: _containers.RepeatedCompositeFieldContainer[Product]
    def __init__(self, products: _Optional[_Iterable[_Union[Product, _Mapping]]] = ...) -> None: ...

class GetProductDetailsRequestMessage(_message.Message):
    __slots__ = ("product_id",)
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    product_id: int
    def __init__(self, product_id: _Optional[int] = ...) -> None: ...

class GetProductDetailsResponseMessage(_message.Message):
    __slots__ = ("item_name", "sale_price")
    ITEM_NAME_FIELD_NUMBER: _ClassVar[int]
    SALE_PRICE_FIELD_NUMBER: _ClassVar[int]
    item_name: str
    sale_price: str
    def __init__(self, item_name: _Optional[str] = ..., sale_price: _Optional[str] = ...) -> None: ...

class UpdateFeedbackRequestMessage(_message.Message):
    __slots__ = ("product_id", "feedback_type")
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    FEEDBACK_TYPE_FIELD_NUMBER: _ClassVar[int]
    product_id: int
    feedback_type: int
    def __init__(self, product_id: _Optional[int] = ..., feedback_type: _Optional[int] = ...) -> None: ...

class GetSellerIdRequestMessage(_message.Message):
    __slots__ = ("product_id",)
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    product_id: int
    def __init__(self, product_id: _Optional[int] = ...) -> None: ...

class GetSellerIdResponseMessage(_message.Message):
    __slots__ = ("seller_id",)
    SELLER_ID_FIELD_NUMBER: _ClassVar[int]
    seller_id: int
    def __init__(self, seller_id: _Optional[int] = ...) -> None: ...
