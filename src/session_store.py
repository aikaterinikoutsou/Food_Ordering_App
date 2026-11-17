"""JSON persistence for the local application session."""

import json
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from .models import Address, Cart, CartItem, Order, Restaurant
from .services import RestaurantCatalog


@dataclass
class SessionSnapshot:
    current_restaurant: Restaurant | None
    cart: Cart
    orders: list[Order]
    payment_state: dict
    tracking_locations: dict


class SessionStore:
    def save(
        self,
        path: str | Path,
        current_restaurant: Restaurant | None,
        cart: Cart,
        orders: list[Order],
        payment_state: dict,
        tracking_locations: dict,
    ) -> None:
        data = {
            "selected_restaurant": (
                current_restaurant.name if current_restaurant else None
            ),
            "cart": [
                {"item": name, "quantity": entry.quantity}
                for name, entry in cart.items.items()
            ],
            "orders": [self._serialize_order(order) for order in orders],
            "payments": payment_state,
            "tracking_locations": tracking_locations,
        }
        session_path = Path(path)
        session_path.parent.mkdir(parents=True, exist_ok=True)
        session_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def load(
        self, path: str | Path, catalog: RestaurantCatalog
    ) -> SessionSnapshot | None:
        session_path = Path(path)
        if not session_path.exists():
            return None

        data = json.loads(session_path.read_text(encoding="utf-8"))
        restaurant_name = data.get("selected_restaurant")
        current_restaurant = (
            catalog.get_by_name(restaurant_name) if restaurant_name else None
        )

        cart = Cart()
        for entry in data.get("cart", []):
            if current_restaurant is None:
                raise ValueError("Saved cart is missing its restaurant.")
            item = current_restaurant.get_item(entry["item"])
            if item is None:
                raise ValueError(f"Saved menu item '{entry['item']}' no longer exists.")
            cart.add_item(item, quantity=int(entry["quantity"]))

        orders = [
            self._deserialize_order(order_data, catalog)
            for order_data in data.get("orders", [])
        ]
        return SessionSnapshot(
            current_restaurant=current_restaurant,
            cart=cart,
            orders=orders,
            payment_state=data.get("payments", {}),
            tracking_locations=data.get("tracking_locations", {}),
        )

    @staticmethod
    def _serialize_order(order: Order) -> dict:
        return {
            "order_number": order.order_number,
            "restaurant_name": order.restaurant_name,
            "items": [
                {"name": entry.item.name, "quantity": entry.quantity}
                for entry in order.items
            ],
            "address": {
                "street": order.address.street,
                "city": order.address.city,
                "postal_code": order.address.postal_code,
                "country": order.address.country,
                "distance_from_restaurant_km": (
                    order.address.distance_from_restaurant_km
                ),
            },
            "subtotal": str(order.subtotal),
            "delivery_fee": str(order.delivery_fee),
            "status": order.status,
            "payment_status": order.payment_status,
            "estimated_delivery_time_min": order.estimated_delivery_time_min,
            "confirmation_notification_sent": (order.confirmation_notification_sent),
            "restaurant_acknowledged": order.restaurant_acknowledged,
            "support_or_cancellation_available": (
                order.support_or_cancellation_available
            ),
            "delay_notification_sent": order.delay_notification_sent,
        }

    @staticmethod
    def _deserialize_order(data: dict, catalog: RestaurantCatalog) -> Order:
        restaurant = catalog.get_by_name(data["restaurant_name"])
        items = []
        for entry in data["items"]:
            item = restaurant.get_item(entry["name"])
            if item is None:
                raise ValueError(f"Saved menu item '{entry['name']}' no longer exists.")
            items.append(CartItem(item=item, quantity=int(entry["quantity"])))

        address_data = data["address"]
        address = Address(
            street=address_data["street"],
            city=address_data["city"],
            postal_code=address_data["postal_code"],
            country=address_data.get("country", "Spain"),
            distance_from_restaurant_km=address_data.get("distance_from_restaurant_km"),
        )
        order = Order(
            order_number=data["order_number"],
            restaurant_name=restaurant.name,
            items=items,
            address=address,
            subtotal=Decimal(data["subtotal"]),
            delivery_fee=Decimal(data.get("delivery_fee", "3.50")),
            estimated_delivery_time_min=int(
                data.get("estimated_delivery_time_min", 30)
            ),
        )
        order.status = data.get("status", "pending")
        order.payment_status = data.get("payment_status", "pending")
        order.confirmation_notification_sent = data.get(
            "confirmation_notification_sent", False
        )
        order.restaurant_acknowledged = data.get("restaurant_acknowledged", True)
        order.support_or_cancellation_available = data.get(
            "support_or_cancellation_available", False
        )
        order.delay_notification_sent = data.get("delay_notification_sent", False)
        return order
