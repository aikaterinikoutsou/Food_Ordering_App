from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Optional

from .models import Address, Cart, MenuItem, Order, PaymentResult, Restaurant


class LocationPermissionError(RuntimeError):
    pass


class RestaurantNotFoundError(RuntimeError):
    pass


class PaymentDeclinedError(RuntimeError):
    pass


@dataclass
class RestaurantCatalog:
    restaurants: List[Restaurant] = field(default_factory=list)

    def add_restaurant(self, restaurant: Restaurant) -> None:
        self.restaurants.append(restaurant)

    def search(self, latitude: Optional[float] = None, longitude: Optional[float] = None, cuisine: Optional[str] = None) -> List[Restaurant]:
        if latitude is None or longitude is None:
            raise LocationPermissionError("Location permission is required to find nearby restaurants.")

        candidates = list(self.restaurants)
        if cuisine:
            candidates = [r for r in candidates if r.cuisine.lower() == cuisine.lower()]

        return sorted(candidates, key=lambda r: r.distance_km)

    def get_by_name(self, name: str) -> Restaurant:
        for restaurant in self.restaurants:
            if restaurant.name.lower() == name.lower():
                return restaurant
        raise RestaurantNotFoundError(f"Restaurant '{name}' was not found.")


class CheckoutService:
    @staticmethod
    def validate_address(address: Address, restaurant: Restaurant) -> bool:
        return True

    @staticmethod
    def can_checkout(cart: Cart, restaurant: Restaurant) -> bool:
        return not cart.is_empty and (cart.restaurant_name == restaurant.name)


class PaymentGateway:
    @staticmethod
    def process_payment(card_number: str, total: Decimal, is_duplicate: bool = False) -> PaymentResult:
        if not card_number or len(card_number.replace(" ", "")) < 12:
            return PaymentResult(False, "invalid", "Card number format is invalid.")

        if is_duplicate:
            return PaymentResult(False, "duplicate", "This payment was already submitted.")

        if total <= Decimal("0"):
            return PaymentResult(False, "declined", "Order total must be greater than zero.")

        return PaymentResult(True, "authorized", "Payment approved.", charge_id="charge_12345")


class DeliveryTracker:
    def __init__(self) -> None:
        self.statuses = ["Preparing", "Out for delivery", "Delivered"]

    def current_status(self, order: Order) -> str:
        if order.status == "confirmed":
            return "Preparing"
        if order.status == "out_for_delivery":
            return "Out for delivery"
        if order.status == "delivered":
            return "Delivered"
        return "Preparing"

    def progress(self, order: Order) -> List[str]:
        return self.statuses
