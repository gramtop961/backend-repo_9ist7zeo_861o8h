"""
Database Schemas for Florist E-commerce

Each Pydantic model represents a MongoDB collection. The collection name is the
lowercased class name. For example: Product -> "product", Order -> "order".
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class Product(BaseModel):
    """
    Products available in the florist store
    Collection name: "product"
    """
    title: str = Field(..., description="Product title, e.g., 'Rose Bouquet'")
    description: Optional[str] = Field(None, description="Detailed description")
    price: float = Field(..., ge=0, description="Price in USD")
    category: str = Field(..., description="Category such as 'Bouquets', 'Plants', 'Gifts'")
    image_url: Optional[str] = Field(None, description="Primary product image URL")
    tags: List[str] = Field(default_factory=list, description="Searchable tags, e.g., ['roses', 'anniversary']")
    in_stock: bool = Field(True, description="Whether the item is currently in stock")


class OrderItem(BaseModel):
    product_id: str = Field(..., description="Referenced product _id as string")
    title: str = Field(..., description="Snapshot of product title at order time")
    price: float = Field(..., ge=0, description="Unit price at order time")
    quantity: int = Field(..., ge=1, description="Quantity ordered")
    image_url: Optional[str] = None


class CustomerInfo(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    postal_code: str


class Order(BaseModel):
    """
    Customer orders
    Collection name: "order"
    """
    items: List[OrderItem]
    customer: CustomerInfo
    notes: Optional[str] = None
    status: str = Field("pending", description="Order status: pending, confirmed, delivered, cancelled")
    subtotal: float = Field(..., ge=0)
    delivery_fee: float = Field(0, ge=0)
    total: float = Field(..., ge=0)
