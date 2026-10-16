from decimal import Decimal

import pytest

from src.models import (
    Address,
    Cart,
    CartItem,
    MenuItem,
    Order,
    Restaurant,
)
from src.services import LocationPermissionError, RestaurantCatalog, RestaurantNotFoundError


def make_item(
    name: str = "Salmon Roll",
    price: str = "10.00",
    restaurant_name: str = "Sushi Place",
    available: bool = True,
) -> MenuItem:
    return MenuItem(
        name=name,
        description="Fresh salmon and rice",
        price=Decimal(price),
        category="Sushi",
        restaurant_name=restaurant_name,
        available=available,
    )


def make_restaurant(name: str, cuisine: str, distance: float) -> Restaurant:
    return Restaurant(
        name=name,
        cuisine=cuisine,
        rating=4.5,
        estimated_delivery_time_min=25,
        distance_km=distance,
    )


def test_address_serializes_fields_and_default_country() -> None:
    address = Address("Main Street 12", "Madrid", "28001")

    assert address.as_dict() == {
        "street": "Main Street 12",
        "city": "Madrid",
        "postal_code": "28001",
        "country": "Spain",
    }


def test_menu_item_serializes_decimal_price_as_string() -> None:
    item = make_item()

    assert item.to_dict() == {
        "name": "Salmon Roll",
        "description": "Fresh salmon and rice",
        "price": "10.00",
        "category": "Sushi",
        "allergens": [],
        "restaurant_name": "Sushi Place",
        "image_url": None,
        "available": True,
    }


def test_restaurant_add_item_sets_restaurant_and_supports_lookup() -> None:
    restaurant = make_restaurant("Sushi Place", "Japanese", 1.2)
    item = make_item(restaurant_name="")

    restaurant.add_item(item)

    assert item.restaurant_name == "Sushi Place"
    assert restaurant.all_items() == [item]
    assert restaurant.get_item("Salmon Roll") is item
    assert restaurant.get_item("Missing item") is None


def test_cart_adds_quantities_and_calculates_subtotal() -> None:
    cart = Cart()
    item = make_item()

    cart.add_item(item)
    cart.add_item(item, quantity=2)

    assert cart.items["Salmon Roll"].quantity == 3
    assert cart.restaurant_name == "Sushi Place"
    assert cart.subtotal == Decimal("30.00")
    assert not cart.is_empty


def test_cart_rejects_unavailable_item() -> None:
    cart = Cart()

    with pytest.raises(ValueError, match="currently unavailable"):
        cart.add_item(make_item(available=False))

    assert cart.is_empty


def test_cart_rejects_items_from_another_restaurant() -> None:
    cart = Cart()
    cart.add_item(make_item())

    with pytest.raises(ValueError, match="Start a new cart"):
        cart.add_item(make_item("Margherita", "14.00", "Pizza Corner"))

    assert list(cart.items) == ["Salmon Roll"]


def test_setting_quantity_to_zero_removes_item_and_clears_restaurant() -> None:
    cart = Cart()
    cart.add_item(make_item())

    cart.update_quantity("Salmon Roll", 0)

    assert cart.is_empty
    assert cart.subtotal == Decimal("0.00")
    assert cart.restaurant_name is None


def test_remove_item_clears_restaurant_when_cart_becomes_empty() -> None:
    cart = Cart()
    cart.add_item(make_item())

    cart.remove_item("Salmon Roll")

    assert cart.is_empty
    assert cart.restaurant_name is None


def test_order_calculates_total_and_confirmation_statuses() -> None:
    cart_item = CartItem(make_item(), quantity=2)
    order = Order(
        order_number="ORD-1001",
        restaurant_name="Sushi Place",
        items=[cart_item],
        address=Address("Main Street 12", "Madrid", "28001"),
        subtotal=Decimal("20.00"),
    )

    assert order.total == Decimal("23.50")
    order.confirm()
    assert order.status == "confirmed"
    assert order.payment_status == "paid"


def test_restaurant_catalog_requires_location() -> None:
    catalog = RestaurantCatalog()

    with pytest.raises(LocationPermissionError, match="Location permission"):
        catalog.search()


def test_restaurant_catalog_searches_by_cuisine_and_distance() -> None:
    catalog = RestaurantCatalog(
        restaurants=[
            make_restaurant("Sushi Place", "Japanese", 1.2),
            make_restaurant("Far Sushi", "Japanese", 4.0),
            make_restaurant("Pizza Corner", "Italian", 2.4),
        ]
    )

    results = catalog.search(40.4, -3.7, cuisine="jApAnEsE")

    assert [restaurant.name for restaurant in results] == [
        "Sushi Place",
        "Far Sushi",
    ]


def test_restaurant_catalog_raises_for_unknown_restaurant() -> None:
    catalog = RestaurantCatalog()

    with pytest.raises(RestaurantNotFoundError, match="was not found"):
        catalog.get_by_name("Unknown")
