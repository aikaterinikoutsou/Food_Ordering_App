"""Application workflows for food ordering."""

from decimal import Decimal
from pathlib import Path
from typing import Optional

from .demo_data import create_demo_restaurants
from .models import Address, Cart, CartItem, MenuItem, Order, Restaurant
from .services import (
    CheckoutService,
    DeliveryTracker,
    LocationPermissionError,
    MenuLoadError,
    PaymentGateway,
    RestaurantCatalog,
)
from .session_store import SessionStore


class FoodOrderingApp:
    def __init__(self) -> None:
        self.catalog = RestaurantCatalog()
        self.cart = Cart()
        self.orders: list[Order] = []
        self.tracker = DeliveryTracker()
        self.current_restaurant: Optional[Restaurant] = None
        self.payment_gateway = PaymentGateway()
        self.session_store = SessionStore()
        self.menu_service_available = True
        self.last_menu_error: Optional[str] = None
        self.search_message = ""
        self.gps_available = True

    def seed_demo_data(self) -> None:
        self.catalog.restaurants.clear()
        for restaurant in create_demo_restaurants():
            self.catalog.add_restaurant(restaurant)

    def search_restaurants(
        self,
        latitude: Optional[float],
        longitude: Optional[float],
        cuisine: Optional[str] = None,
        radius_km: Optional[float] = 50.0,
    ) -> list[Restaurant]:
        try:
            results = self.catalog.search(
                latitude=latitude,
                longitude=longitude,
                cuisine=cuisine,
                radius_km=radius_km,
            )
        except LocationPermissionError:
            self.search_message = (
                "Enable location services or provide a manual address to search."
            )
            raise
        self.search_message = "" if results else "No restaurants found nearby"
        return results

    def browse_restaurant(self, restaurant_name: str) -> Restaurant:
        restaurant = self.catalog.get_by_name(restaurant_name)
        self.current_restaurant = restaurant
        return restaurant

    def load_menu(self, restaurant_name: Optional[str] = None) -> dict:
        if restaurant_name is not None:
            self.browse_restaurant(restaurant_name)
        if self.current_restaurant is None:
            raise ValueError("A restaurant must be selected before loading its menu.")
        if not self.menu_service_available:
            self.last_menu_error = "Menu service is unavailable. Please retry."
            raise MenuLoadError(self.last_menu_error)
        self.last_menu_error = None
        return self.current_restaurant.menu_for_browsing()

    def retry_menu(self) -> dict:
        return self.load_menu()

    def get_menu_item_details(self, item_name: str) -> MenuItem:
        if self.current_restaurant is None:
            raise ValueError(
                "A restaurant must be selected before viewing item details."
            )
        item = self.current_restaurant.get_item(item_name)
        if item is None:
            raise ValueError(f"Item '{item_name}' was not found in the menu.")
        return item

    def add_to_cart(self, item_name: str) -> str:
        if self.current_restaurant is None:
            raise ValueError("No restaurant selected.")
        item = self.current_restaurant.get_item(item_name)
        if item is None:
            raise ValueError(f"Item '{item_name}' was not found in the menu.")
        if not self.current_restaurant.is_open:
            raise ValueError(f"{item_name} is currently unavailable.")
        self.cart.add_item(item)
        return f"{item_name} added to cart."

    def update_cart_quantity(self, item_name: str, quantity: int) -> None:
        if item_name not in self.cart.items:
            raise ValueError(f"Item '{item_name}' is not present in the cart.")
        self.cart.update_quantity(item_name, quantity)

    def cart_total(self) -> Decimal:
        return self.cart.subtotal

    def checkout(self, address: Address) -> Order:
        if self.current_restaurant is None:
            raise ValueError("A restaurant must be selected before checkout.")
        if self.cart.is_empty:
            raise ValueError("Checkout is not available for an empty cart.")
        if any(not entry.item.available for entry in self.cart.items.values()):
            raise ValueError(
                "An item in your cart is currently unavailable. "
                "Remove or replace it before proceeding."
            )
        if not CheckoutService.can_checkout(self.cart, self.current_restaurant):
            raise ValueError("The cart should belong to the selected restaurant.")
        if not CheckoutService.validate_address(address, self.current_restaurant):
            raise ValueError("Outside delivery area")

        order = Order(
            order_number=f"ORD-{1001 + len(self.orders)}",
            restaurant_name=self.current_restaurant.name,
            items=[
                CartItem(item=entry.item, quantity=entry.quantity)
                for entry in self.cart.items.values()
            ],
            address=address,
            subtotal=self.cart.subtotal,
            estimated_delivery_time_min=(
                self.current_restaurant.estimated_delivery_time_min
            ),
        )
        self.orders.append(order)
        return order

    def submit_payment(
        self, card_number: str, order: Order, is_duplicate: bool = False
    ) -> dict:
        if order.payment_status == "paid":
            return {
                "authorized": False,
                "message": "This payment was already submitted.",
                "status": "duplicate",
            }
        response = self.payment_gateway.submit_payment(
            card_number,
            order.total,
            payment_id=order.order_number,
            is_duplicate=is_duplicate,
        )
        if response.status == "checking":
            order.payment_status = "checking"
        if not response.authorized:
            return {
                "authorized": False,
                "message": response.message,
                "status": response.status,
            }
        order.confirm()
        self.cart.clear()
        self.send_confirmation_notification(order)
        return {
            "authorized": True,
            "message": "Payment approved.",
            "status": order.status,
        }

    def resolve_payment(self, order: Order) -> dict:
        response = self.payment_gateway.resolve_payment(order.order_number)
        if response.authorized:
            order.confirm()
            self.cart.clear()
            self.send_confirmation_notification(order)
        return {
            "authorized": response.authorized,
            "message": response.message,
            "status": response.status,
        }

    def send_confirmation_notification(self, order: Order) -> None:
        order.confirmation_notification_sent = True

    def notify_restaurant_delay(self, order: Order) -> None:
        if not order.restaurant_acknowledged:
            order.delay_notification_sent = True
            order.support_or_cancellation_available = True

    def track_order(self, order: Order) -> list[str]:
        return self.tracker.progress(order)

    def tracking_details(self, order: Order) -> dict:
        return self.tracker.tracking_details(order, gps_available=self.gps_available)

    def save_session(self, path: str | Path) -> None:
        self.session_store.save(
            path=path,
            current_restaurant=self.current_restaurant,
            cart=self.cart,
            orders=self.orders,
            payment_state=self.payment_gateway.export_state(),
            tracking_locations=self.tracker.export_state(),
        )

    def load_session(self, path: str | Path) -> bool:
        snapshot = self.session_store.load(path, self.catalog)
        if snapshot is None:
            return False
        self.current_restaurant = snapshot.current_restaurant
        self.cart = snapshot.cart
        self.orders = snapshot.orders
        self.payment_gateway.restore_state(snapshot.payment_state)
        self.tracker.restore_state(snapshot.tracking_locations)
        return True
