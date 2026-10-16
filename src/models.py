from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, List, Optional


@dataclass
class Address:
    street: str
    city: str
    postal_code: str
    country: str = "Spain"

    def as_dict(self) -> dict:
        return {
            "street": self.street,
            "city": self.city,
            "postal_code": self.postal_code,
            "country": self.country,
        }


@dataclass
class MenuItem:
    name: str
    description: str
    price: Decimal
    category: str
    allergens: List[str] = field(default_factory=list)
    restaurant_name: str = ""
    image_url: Optional[str] = None
    available: bool = True

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "price": str(self.price),
            "category": self.category,
            "allergens": self.allergens,
            "restaurant_name": self.restaurant_name,
            "image_url": self.image_url,
            "available": self.available,
        }


@dataclass
class Restaurant:
    name: str
    cuisine: str
    rating: float
    estimated_delivery_time_min: int
    distance_km: float
    delivery_radius_km: float = 5.0
    is_open: bool = True
    menu: Dict[str, List[MenuItem]] = field(default_factory=dict)

    def add_item(self, item: MenuItem) -> None:
        item.restaurant_name = self.name
        self.menu.setdefault(item.category, []).append(item)

    def all_items(self) -> List[MenuItem]:
        items: List[MenuItem] = []
        for category_items in self.menu.values():
            items.extend(category_items)
        return items

    def get_item(self, item_name: str) -> Optional[MenuItem]:
        for item in self.all_items():
            if item.name == item_name:
                return item
        return None

    def is_menu_viewable(self) -> bool:
        return self.is_open or True


@dataclass
class CartItem:
    item: MenuItem
    quantity: int = 1

    @property
    def line_total(self) -> Decimal:
        return self.item.price * Decimal(self.quantity)


@dataclass
class Cart:
    items: Dict[str, CartItem] = field(default_factory=dict)
    restaurant_name: Optional[str] = None

    def add_item(self, item: MenuItem, quantity: int = 1) -> None:
        if not item.available:
            raise ValueError(f"{item.name} is currently unavailable.")

        if self.items and self.restaurant_name and self.restaurant_name != item.restaurant_name:
            raise ValueError("Start a new cart to order from another restaurant.")

        self.restaurant_name = item.restaurant_name or self.restaurant_name
        current = self.items.get(item.name)
        if current is None:
            self.items[item.name] = CartItem(item=item, quantity=0)
        self.items[item.name].quantity += quantity

    def update_quantity(self, item_name: str, quantity: int) -> None:
        if quantity <= 0:
            self.items.pop(item_name, None)
            if not self.items:
                self.restaurant_name = None
            return

        item = self.items[item_name].item
        self.items[item_name].quantity = quantity

    def remove_item(self, item_name: str) -> None:
        self.items.pop(item_name, None)
        if not self.items:
            self.restaurant_name = None

    @property
    def subtotal(self) -> Decimal:
        return sum((entry.line_total for entry in self.items.values()), Decimal("0.00"))

    @property
    def is_empty(self) -> bool:
        return len(self.items) == 0

    def clear(self) -> None:
        self.items.clear()
        self.restaurant_name = None


@dataclass
class PaymentResult:
    authorized: bool
    status: str
    message: str
    charge_id: Optional[str] = None


@dataclass
class Order:
    order_number: str
    restaurant_name: str
    items: List[CartItem]
    address: Address
    subtotal: Decimal
    delivery_fee: Decimal = Decimal("3.50")
    total: Decimal = Decimal("0.00")
    status: str = "pending"
    payment_status: str = "pending"
    estimated_delivery_time_min: int = 30

    def __post_init__(self) -> None:
        self.total = self.subtotal + self.delivery_fee

    def confirm(self) -> None:
        self.status = "confirmed"
        self.payment_status = "paid"

    def to_dict(self) -> dict:
        return {
            "order_number": self.order_number,
            "restaurant_name": self.restaurant_name,
            "items": [{"name": item.item.name, "quantity": item.quantity, "price": str(item.item.price)} for item in self.items],
            "address": self.address.as_dict(),
            "subtotal": str(self.subtotal),
            "delivery_fee": str(self.delivery_fee),
            "total": str(self.total),
            "status": self.status,
            "payment_status": self.payment_status,
            "estimated_delivery_time_min": self.estimated_delivery_time_min,
        }
