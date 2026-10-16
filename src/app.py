from __future__ import annotations

from decimal import Decimal
from typing import List, Optional

from .models import Address, Cart, MenuItem, Order, Restaurant
from .services import CheckoutService, DeliveryTracker, PaymentGateway, RestaurantCatalog


class FoodOrderingApp:
    def __init__(self) -> None:
        self.catalog = RestaurantCatalog()
        self.cart = Cart()
        self.orders: List[Order] = []
        self.tracker = DeliveryTracker()
        self.current_restaurant: Optional[Restaurant] = None

    def seed_demo_data(self) -> None:
        sushi = Restaurant(
            name="Sushi Place",
            cuisine="Japanese",
            rating=4.8,
            estimated_delivery_time_min=20,
            distance_km=1.2,
            delivery_radius_km=5,
            is_open=True,
        )
        sushi.add_item(MenuItem("Salmon Roll", "Fresh salmon and rice", Decimal("10.00"), "Sushi", ["contains fish"], restaurant_name="Sushi Place", image_url="salmon-roll.jpg", available=True))
        sushi.add_item(MenuItem("Avocado Roll", "Creamy avocado roll", Decimal("9.50"), "Sushi", ["contains sesame"], restaurant_name="Sushi Place", image_url="avocado-roll.jpg", available=True))

        pizza = Restaurant(
            name="Pizza Corner",
            cuisine="Italian",
            rating=4.7,
            estimated_delivery_time_min=25,
            distance_km=2.4,
            delivery_radius_km=6,
            is_open=True,
        )
        pizza.add_item(MenuItem("Margherita", "Classic tomato basil pizza", Decimal("14.00"), "Pizza", ["contains gluten"], restaurant_name="Pizza Corner", image_url="margherita.jpg", available=True))

        self.catalog.add_restaurant(sushi)
        self.catalog.add_restaurant(pizza)

    def search_restaurants(self, latitude: float, longitude: float, cuisine: Optional[str] = None) -> List[Restaurant]:
        return self.catalog.search(latitude=latitude, longitude=longitude, cuisine=cuisine)

    def browse_restaurant(self, restaurant_name: str) -> Restaurant:
        restaurant = self.catalog.get_by_name(restaurant_name)
        self.current_restaurant = restaurant
        return restaurant

    def add_to_cart(self, item_name: str) -> str:
        if self.current_restaurant is None:
            raise ValueError("No restaurant selected.")

        item = self.current_restaurant.get_item(item_name)
        if item is None:
            raise ValueError(f"Item '{item_name}' was not found in the menu.")

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

        if not CheckoutService.can_checkout(self.cart, self.current_restaurant):
            raise ValueError("The cart should belong to the selected restaurant.")

        if not CheckoutService.validate_address(address, self.current_restaurant):
            raise ValueError("Outside delivery area")

        order = Order(
            order_number="ORD-1001",
            restaurant_name=self.current_restaurant.name,
            items=list(self.cart.items.values()),
            address=address,
            subtotal=self.cart.subtotal,
            estimated_delivery_time_min=self.current_restaurant.estimated_delivery_time_min,
        )
        self.orders.append(order)
        return order

    def submit_payment(self, card_number: str, order: Order, is_duplicate: bool = False) -> dict:
        response = PaymentGateway.process_payment(card_number, order.total, is_duplicate=is_duplicate)
        if not response.authorized:
            return {"authorized": False, "message": response.message, "status": response.status}

        order.confirm()
        return {"authorized": True, "message": "Payment approved.", "status": order.status}

    def track_order(self, order: Order) -> List[str]:
        return self.tracker.progress(order)


if __name__ == "__main__":
    app = FoodOrderingApp()
    app.seed_demo_data()
    restaurants = app.search_restaurants(40.4168, -3.7038)
    print([restaurant.name for restaurant in restaurants])
    app.browse_restaurant("Sushi Place")
    app.add_to_cart("Salmon Roll")
    order = app.checkout(Address("Main Street 12", "Madrid", "28001"))
    print(app.submit_payment("4111111111111111", order))
    print(app.track_order(order))
