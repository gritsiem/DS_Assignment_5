from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class generalResponse(_message.Message):
    __slots__ = ("msg",)
    MSG_FIELD_NUMBER: _ClassVar[int]
    msg: str
    def __init__(self, msg: _Optional[str] = ...) -> None: ...

class CreateAccountRequestMessage(_message.Message):
    __slots__ = ("username", "password", "name")
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    username: str
    password: str
    name: str
    def __init__(self, username: _Optional[str] = ..., password: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...

class LoginRequestMessage(_message.Message):
    __slots__ = ("username", "password")
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    username: str
    password: str
    def __init__(self, username: _Optional[str] = ..., password: _Optional[str] = ...) -> None: ...

class SearchProductMessage(_message.Message):
    __slots__ = ("item_category", "keywords")
    ITEM_CATEGORY_FIELD_NUMBER: _ClassVar[int]
    KEYWORDS_FIELD_NUMBER: _ClassVar[int]
    item_category: int
    keywords: str
    def __init__(self, item_category: _Optional[int] = ..., keywords: _Optional[str] = ...) -> None: ...

class AddToCartRequestMessage(_message.Message):
    __slots__ = ("buyer_id", "product_id", "quantity")
    BUYER_ID_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    buyer_id: int
    product_id: int
    quantity: int
    def __init__(self, buyer_id: _Optional[int] = ..., product_id: _Optional[int] = ..., quantity: _Optional[int] = ...) -> None: ...

class RemoveFromCartRequestMessage(_message.Message):
    __slots__ = ("buyer_id", "product_id", "quantity")
    BUYER_ID_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    buyer_id: int
    product_id: int
    quantity: int
    def __init__(self, buyer_id: _Optional[int] = ..., product_id: _Optional[int] = ..., quantity: _Optional[int] = ...) -> None: ...

class ClearCartRequestMessage(_message.Message):
    __slots__ = ("buyer_id",)
    BUYER_ID_FIELD_NUMBER: _ClassVar[int]
    buyer_id: int
    def __init__(self, buyer_id: _Optional[int] = ...) -> None: ...

class DisplayCartRequestMessage(_message.Message):
    __slots__ = ("buyer_id",)
    BUYER_ID_FIELD_NUMBER: _ClassVar[int]
    buyer_id: int
    def __init__(self, buyer_id: _Optional[int] = ...) -> None: ...

class MakePurchaseMessage(_message.Message):
    __slots__ = ("buyer_id", "credit_card")
    BUYER_ID_FIELD_NUMBER: _ClassVar[int]
    CREDIT_CARD_FIELD_NUMBER: _ClassVar[int]
    buyer_id: int
    credit_card: str
    def __init__(self, buyer_id: _Optional[int] = ..., credit_card: _Optional[str] = ...) -> None: ...

class PurchaseHistoryMessage(_message.Message):
    __slots__ = ("buyer_id",)
    BUYER_ID_FIELD_NUMBER: _ClassVar[int]
    buyer_id: int
    def __init__(self, buyer_id: _Optional[int] = ...) -> None: ...

class ProvideFeedbackMessage(_message.Message):
    __slots__ = ("buyer_id", "product_id", "feedback_type")
    BUYER_ID_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    FEEDBACK_TYPE_FIELD_NUMBER: _ClassVar[int]
    buyer_id: int
    product_id: int
    feedback_type: str
    def __init__(self, buyer_id: _Optional[int] = ..., product_id: _Optional[int] = ..., feedback_type: _Optional[str] = ...) -> None: ...

class GetSellerRatingMessage(_message.Message):
    __slots__ = ("seller_id",)
    SELLER_ID_FIELD_NUMBER: _ClassVar[int]
    seller_id: int
    def __init__(self, seller_id: _Optional[int] = ...) -> None: ...

class LogoutMessage(_message.Message):
    __slots__ = ("buyer_id",)
    BUYER_ID_FIELD_NUMBER: _ClassVar[int]
    buyer_id: int
    def __init__(self, buyer_id: _Optional[int] = ...) -> None: ...

class GetBuyerIdRequestMessage(_message.Message):
    __slots__ = ("username",)
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    username: str
    def __init__(self, username: _Optional[str] = ...) -> None: ...

class GetBuyerIdResponseMessage(_message.Message):
    __slots__ = ("buyer_id",)
    BUYER_ID_FIELD_NUMBER: _ClassVar[int]
    buyer_id: int
    def __init__(self, buyer_id: _Optional[int] = ...) -> None: ...

class SetLoginStateRequestMessage(_message.Message):
    __slots__ = ("buyer_id", "state")
    BUYER_ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    buyer_id: int
    state: bool
    def __init__(self, buyer_id: _Optional[int] = ..., state: bool = ...) -> None: ...

class CartItem(_message.Message):
    __slots__ = ("product_id", "quantity")
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    product_id: int
    quantity: int
    def __init__(self, product_id: _Optional[int] = ..., quantity: _Optional[int] = ...) -> None: ...

class DisplayCartResponseMessage(_message.Message):
    __slots__ = ("cart_items",)
    CART_ITEMS_FIELD_NUMBER: _ClassVar[int]
    cart_items: _containers.RepeatedCompositeFieldContainer[CartItem]
    def __init__(self, cart_items: _Optional[_Iterable[_Union[CartItem, _Mapping]]] = ...) -> None: ...

class HasProvidedFeedbackRequestMessage(_message.Message):
    __slots__ = ("buyer_id", "product_id")
    BUYER_ID_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    buyer_id: int
    product_id: int
    def __init__(self, buyer_id: _Optional[int] = ..., product_id: _Optional[int] = ...) -> None: ...

class HasProvidedFeedbackResponseMessage(_message.Message):
    __slots__ = ("has_provided",)
    HAS_PROVIDED_FIELD_NUMBER: _ClassVar[int]
    has_provided: bool
    def __init__(self, has_provided: bool = ...) -> None: ...

class UpdateProvideFeedbackRequestMessage(_message.Message):
    __slots__ = ("buyer_id", "product_id")
    BUYER_ID_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    buyer_id: int
    product_id: int
    def __init__(self, buyer_id: _Optional[int] = ..., product_id: _Optional[int] = ...) -> None: ...

class UpdateSellerFeedbackRequestMessage(_message.Message):
    __slots__ = ("seller_id", "feedback_type")
    SELLER_ID_FIELD_NUMBER: _ClassVar[int]
    FEEDBACK_TYPE_FIELD_NUMBER: _ClassVar[int]
    seller_id: int
    feedback_type: int
    def __init__(self, seller_id: _Optional[int] = ..., feedback_type: _Optional[int] = ...) -> None: ...

class UserCredentialsMessage(_message.Message):
    __slots__ = ("username", "password")
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    username: str
    password: str
    def __init__(self, username: _Optional[str] = ..., password: _Optional[str] = ...) -> None: ...

class SellerFeedbackMessage(_message.Message):
    __slots__ = ("seller_id", "tu", "td")
    SELLER_ID_FIELD_NUMBER: _ClassVar[int]
    TU_FIELD_NUMBER: _ClassVar[int]
    TD_FIELD_NUMBER: _ClassVar[int]
    seller_id: int
    tu: int
    td: int
    def __init__(self, seller_id: _Optional[int] = ..., tu: _Optional[int] = ..., td: _Optional[int] = ...) -> None: ...
