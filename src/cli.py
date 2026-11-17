"""Interactive terminal interface for the food-ordering application."""

from pathlib import Path

from .application import FoodOrderingApp
from .models import Address
from .services import LocationPermissionError, MenuLoadError


def run_cli() -> None:
    app = FoodOrderingApp()
    app.seed_demo_data()
    session_file = Path.home() / ".food_ordering_app" / "session.json"
    app.load_session(session_file)
    print("Food Ordering App")
    while True:
        print("\n1. Find restaurants  2. Browse menu  3. View cart")
        print("4. Checkout  5. Track latest order  0. Save and exit")
        choice = input("> ").strip()
        try:
            if choice == "1":
                _search_restaurants(app)
            elif choice == "2":
                _browse_menu(app)
            elif choice == "3":
                _manage_cart(app)
            elif choice == "4":
                _checkout(app)
            elif choice == "5":
                _track_latest_order(app)
            elif choice == "0":
                app.save_session(session_file)
                print("Session saved.")
                return
            else:
                print("Choose one of the listed options.")
        except (ValueError, MenuLoadError, LocationPermissionError) as error:
            print(f"Unable to complete that action: {error}")


def _search_restaurants(app: FoodOrderingApp) -> None:
    cuisine = input("Cuisine filter (blank for all): ").strip() or None
    restaurants = app.search_restaurants(40.4168, -3.7038, cuisine=cuisine)
    if not restaurants:
        print(app.search_message)
    for restaurant in restaurants:
        print(
            f"{restaurant.name} ({restaurant.cuisine}) - "
            f"{restaurant.distance_km:.1f} km, "
            f"{restaurant.rating:.1f} stars, "
            f"{restaurant.estimated_delivery_time_min} min"
        )


def _browse_menu(app: FoodOrderingApp) -> None:
    name = input("Restaurant name: ").strip()
    try:
        menu = app.load_menu(name)
    except MenuLoadError as error:
        print(error)
        if input("Retry menu load? (y/n): ").strip().lower() != "y":
            return
        menu = app.retry_menu()
    for category, items in menu.items():
        print(f"\n{category}")
        for item in items:
            availability = "" if item.available else " (unavailable)"
            allergens = ", ".join(item.allergens) or "none"
            print(
                f"{item.name}: €{item.price:.2f}{availability}\n"
                f"  {item.description}\n"
                f"  Allergens: {allergens}"
            )
    item_name = input("Item to add (blank to return): ").strip()
    if item_name:
        details = app.get_menu_item_details(item_name)
        print(
            f"{details.description}; allergens: "
            f"{', '.join(details.allergens) or 'none'}"
        )
        print(app.add_to_cart(item_name))


def _manage_cart(app: FoodOrderingApp) -> None:
    for name, entry in app.cart.items.items():
        print(f"{name} x{entry.quantity} - €{entry.line_total:.2f}")
    print(f"Subtotal: €{app.cart_total():.2f}")
    item_name = input("Item to change quantity (blank to return): ").strip()
    if item_name:
        quantity = int(input("New quantity (0 removes item): ").strip())
        app.update_cart_quantity(item_name, quantity)


def _checkout(app: FoodOrderingApp) -> None:
    if app.current_restaurant is None:
        print("Browse a restaurant before checkout.")
        return
    street = input("Street: ").strip()
    city = input("City: ").strip()
    postal_code = input("Postal code: ").strip()
    distance_text = input("Distance from restaurant in km (blank if unknown): ").strip()
    address = Address(
        street=street,
        city=city,
        postal_code=postal_code,
        distance_from_restaurant_km=float(distance_text) if distance_text else None,
    )
    order = app.checkout(address)
    print(
        f"{order.order_number}: €{order.total:.2f} (delivery €{order.delivery_fee:.2f})"
    )
    card_number = input("Card number (demo only): ").strip()
    result = app.submit_payment(card_number, order)
    print(result["message"])
    if result["status"] == "checking":
        result = app.resolve_payment(order)
        print(result["message"])
    elif result["status"] in {"declined", "invalid"}:
        retry_card = input(
            "Enter another card number to retry, or leave blank: "
        ).strip()
        if retry_card:
            result = app.submit_payment(retry_card, order)
            print(result["message"])


def _track_latest_order(app: FoodOrderingApp) -> None:
    if not app.orders:
        print("There are no orders to track.")
        return
    order = app.orders[-1]
    details = app.tracking_details(order)
    print(f"{order.order_number}: {details['status']}")
    print(f"Last location: {details['location']}")
