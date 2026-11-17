from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, List, Optional

from .models import Address, Cart, Order, PaymentResult, Restaurant


class LocationPermissionError(RuntimeError):
    pass


class RestaurantNotFoundError(RuntimeError):
    pass


class PaymentDeclinedError(RuntimeError):
    pass


class MenuLoadError(RuntimeError):
    pass


@dataclass
class RestaurantCatalog:
    restaurants: List[Restaurant] = field(default_factory=list)

    def add_restaurant(self, restaurant: Restaurant) -> None:
        self.restaurants.append(restaurant)

    def search(
        self,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        cuisine: Optional[str] = None,
        radius_km: Optional[float] = 50.0,
    ) -> List[Restaurant]:
        if latitude is None or longitude is None:
            raise LocationPermissionError(
                "Location permission is required to find nearby restaurants."
            )
        if radius_km is not None and radius_km < 0:
            raise ValueError("Search radius cannot be negative.")

        candidates = list(self.restaurants)
        if cuisine:
            candidates = [r for r in candidates if r.cuisine.lower() == cuisine.lower()]
        if radius_km is not None:
            candidates = [r for r in candidates if r.distance_km <= radius_km]

        return sorted(candidates, key=lambda r: r.distance_km)

    def get_by_name(self, name: str) -> Restaurant:
        for restaurant in self.restaurants:
            if restaurant.name.lower() == name.lower():
                return restaurant
        raise RestaurantNotFoundError(f"Restaurant '{name}' was not found.")


class CheckoutService:
    @staticmethod
    def validate_address(address: Address, restaurant: Restaurant) -> bool:
        if (
            not address.street.strip()
            or not address.city.strip()
            or not address.postal_code.strip()
        ):
            return False
        distance = address.distance_from_restaurant_km
        return distance is None or (
            distance >= 0 and distance <= restaurant.delivery_radius_km
        )

    @staticmethod
    def can_checkout(cart: Cart, restaurant: Restaurant) -> bool:
        return (
            not cart.is_empty
            and cart.restaurant_name == restaurant.name
            and all(entry.item.available for entry in cart.items.values())
        )


class PaymentGateway:
    def __init__(self) -> None:
        self._payments: Dict[str, PaymentResult] = {}
        self._timed_out_payments: Dict[str, PaymentResult] = {}
        self.simulate_next_timeout = False

    @staticmethod
    def process_payment(
        card_number: str,
        total: Decimal,
        is_duplicate: bool = False,
    ) -> PaymentResult:
        if not card_number or len(card_number.replace(" ", "")) < 12:
            return PaymentResult(False, "invalid", "Card number format is invalid.")

        if is_duplicate:
            return PaymentResult(
                False, "duplicate", "This payment was already submitted."
            )

        if total <= Decimal("0"):
            return PaymentResult(
                False, "declined", "Order total must be greater than zero."
            )

        if card_number.replace(" ", "").endswith("0002"):
            return PaymentResult(False, "declined", "Insufficient funds.")

        return PaymentResult(
            True, "authorized", "Payment approved.", charge_id="charge_12345"
        )

    def submit_payment(
        self,
        card_number: str,
        total: Decimal,
        payment_id: str,
        is_duplicate: bool = False,
    ) -> PaymentResult:
        existing = self._payments.get(payment_id)
        if existing is not None:
            return PaymentResult(
                False, "duplicate", "This payment was already submitted."
            )

        if payment_id in self._timed_out_payments:
            return self.resolve_payment(payment_id)

        result = self.process_payment(card_number, total, is_duplicate)
        if not result.authorized:
            return result

        if self.simulate_next_timeout:
            self.simulate_next_timeout = False
            result = PaymentResult(
                True,
                "authorized",
                "Payment approved.",
                charge_id=f"charge_{payment_id}",
            )
            self._timed_out_payments[payment_id] = result
            return PaymentResult(
                False,
                "checking",
                "Checking payment status. Please wait before retrying.",
            )

        result = PaymentResult(
            True,
            "authorized",
            "Payment approved.",
            charge_id=f"charge_{payment_id}",
        )
        self._payments[payment_id] = result
        return result

    def resolve_payment(self, payment_id: str) -> PaymentResult:
        result = self._timed_out_payments.pop(payment_id, None)
        if result is None:
            return PaymentResult(
                False, "not_found", "No pending payment was found for this order."
            )
        self._payments[payment_id] = result
        return result

    def export_state(self) -> dict:
        def serialize(result: PaymentResult) -> dict:
            return {
                "authorized": result.authorized,
                "status": result.status,
                "message": result.message,
                "charge_id": result.charge_id,
            }

        return {
            "payments": {
                payment_id: serialize(result)
                for payment_id, result in self._payments.items()
            },
            "timed_out_payments": {
                payment_id: serialize(result)
                for payment_id, result in self._timed_out_payments.items()
            },
        }

    def restore_state(self, data: dict) -> None:
        def deserialize(result: dict) -> PaymentResult:
            return PaymentResult(
                authorized=bool(result["authorized"]),
                status=str(result["status"]),
                message=str(result["message"]),
                charge_id=result.get("charge_id"),
            )

        self._payments = {
            payment_id: deserialize(result)
            for payment_id, result in data.get("payments", {}).items()
        }
        self._timed_out_payments = {
            payment_id: deserialize(result)
            for payment_id, result in data.get("timed_out_payments", {}).items()
        }


class DeliveryTracker:
    def __init__(self) -> None:
        self.statuses = ["Preparing", "Out for delivery", "Delivered"]
        self._last_known_locations: Dict[str, dict] = {}

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

    def tracking_details(self, order: Order, gps_available: bool = True) -> dict:
        if gps_available:
            self._last_known_locations[order.order_number] = {
                "latitude": 40.4168,
                "longitude": -3.7038,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        else:
            self._last_known_locations.setdefault(
                order.order_number,
                {
                    "latitude": 40.4168,
                    "longitude": -3.7038,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                },
            )
        return {
            "status": self.current_status(order),
            "location": dict(self._last_known_locations[order.order_number]),
            "location_is_stale": not gps_available,
        }

    def export_state(self) -> dict:
        return {
            order_number: dict(location)
            for order_number, location in self._last_known_locations.items()
        }

    def restore_state(self, data: dict) -> None:
        self._last_known_locations = {
            order_number: dict(location) for order_number, location in data.items()
        }
