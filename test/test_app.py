from decimal import Decimal

import pytest

from src.app import FoodOrderingApp
from src.models import Address


@pytest.fixture
def app() -> FoodOrderingApp:
    application = FoodOrderingApp()
    application.seed_demo_data()
    return application


def test_search_restaurants_returns_nearest_first_and_filters_cuisine(
    app: FoodOrderingApp,
) -> None:
    restaurants = app.search_restaurants(40.4168, -3.7038, cuisine="italian")

    assert [restaurant.name for restaurant in restaurants] == ["Pizza Corner"]


def test_add_to_cart_requires_selected_restaurant(app: FoodOrderingApp) -> None:
    with pytest.raises(ValueError, match="No restaurant selected"):
        app.add_to_cart("Salmon Roll")


def test_add_to_cart_returns_confirmation_and_updates_total(
    app: FoodOrderingApp,
) -> None:
    app.browse_restaurant("Sushi Place")

    result = app.add_to_cart("Salmon Roll")

    assert result == "Salmon Roll added to cart."
    assert app.cart_total() == Decimal("10.00")


def test_add_to_cart_rejects_unknown_menu_item(app: FoodOrderingApp) -> None:
    app.browse_restaurant("Sushi Place")

    with pytest.raises(ValueError, match="was not found in the menu"):
        app.add_to_cart("Unknown item")


def test_checkout_rejects_empty_cart(app: FoodOrderingApp) -> None:
    app.browse_restaurant("Sushi Place")

    with pytest.raises(ValueError, match="empty cart"):
        app.checkout(Address("Main Street 12", "Madrid", "28001"))


def test_checkout_creates_order_with_itemized_total(app: FoodOrderingApp) -> None:
    app.browse_restaurant("Sushi Place")
    app.add_to_cart("Salmon Roll")
    app.update_cart_quantity("Salmon Roll", 2)

    order = app.checkout(Address("Main Street 12", "Madrid", "28001"))

    assert order.order_number == "ORD-1001"
    assert order.restaurant_name == "Sushi Place"
    assert order.subtotal == Decimal("20.00")
    assert order.total == Decimal("23.50")
    assert order.items[0].quantity == 2
    assert app.orders == [order]


def test_checkout_rejects_cart_for_different_selected_restaurant(
    app: FoodOrderingApp,
) -> None:
    app.browse_restaurant("Sushi Place")
    app.add_to_cart("Salmon Roll")
    app.browse_restaurant("Pizza Corner")

    with pytest.raises(ValueError, match="cart should belong"):
        app.checkout(Address("Main Street 12", "Madrid", "28001"))


def test_successful_payment_confirms_order(app: FoodOrderingApp) -> None:
    app.browse_restaurant("Sushi Place")
    app.add_to_cart("Salmon Roll")
    order = app.checkout(Address("Main Street 12", "Madrid", "28001"))

    result = app.submit_payment("4111111111111111", order)

    assert result == {
        "authorized": True,
        "message": "Payment approved.",
        "status": "confirmed",
    }
    assert order.payment_status == "paid"


@pytest.mark.parametrize(
    ("card_number", "is_duplicate", "expected_status"),
    [
        ("1234", False, "invalid"),
        ("4111111111111111", True, "duplicate"),
    ],
)
def test_rejected_payment_does_not_confirm_order(
    app: FoodOrderingApp,
    card_number: str,
    is_duplicate: bool,
    expected_status: str,
) -> None:
    app.browse_restaurant("Sushi Place")
    app.add_to_cart("Salmon Roll")
    order = app.checkout(Address("Main Street 12", "Madrid", "28001"))

    result = app.submit_payment(card_number, order, is_duplicate=is_duplicate)

    assert result["authorized"] is False
    assert result["status"] == expected_status
    assert order.status == "pending"
    assert order.payment_status == "pending"
