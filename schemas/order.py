from typing import Optional, List
from pydantic import BaseModel

class ShippingAddress(BaseModel):
    address1: Optional[str]
    address2: Optional[str]
    city: Optional[str]
    province: Optional[str]
    postal_code: Optional[str]
    country: Optional[str]

class LineItem(BaseModel):
    id: str
    price: float
    vendor: str
    quantity: int

class OrderBase(BaseModel):
    order_id: str
    store_id: str
    shopify_app: Optional[str] = None
    order_name: str
    order_date: Optional[str] = None
    currency_code: str
    total_amount: float
    products: List[LineItem]
    order_notes: Optional[str] = None
    source_name: Optional[str] = None
    app_used: Optional[bool] = False
    referring_site: Optional[str] = None
    address: Optional[ShippingAddress] = None
    diamonds_price: Optional[float] = None

class OrderCreate(OrderBase):
    line_items: Optional[List[LineItem]] = []
    shipping_address: Optional[ShippingAddress] = None
