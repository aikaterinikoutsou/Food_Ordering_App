from decimal import Decimal
from pathlib import Path

import pytest

from src.app import FoodOrderingApp, run_cli
from src.models import Address
from src.services import LocationPermissionError, MenuLoadError, PaymentGateway


@pytest.fixture
def app() -> FoodOrderingApp:
    application = FoodOrderingApp()
    application.seed_demo_data()
    return application


def test_search_reports_no_nearby_restaurants_and_missing_location(app) -> None:
    for restaurant in app.catalog.restaurants:
        restaurant.distance_km = 60

    assert app.search_restaurants(40.4, -3.7) == []
    assert app.search_message == "No restaurants found nearby"

    with pytest.raises(LocationPermissionError):
        app.search_restaurants(None, None)
    assert "manual address" in app.search_message.lower()


def test_closed_restaurant_menu_is_browse_only_without_mutating_menu(app) -> None:
    restaurant = app.browse_restaurant("Sushi Place")
    restaurant.is_open = False

    menu = app.load_menu()

    assert all(not item.available for items in menu.values() for item in items)
    assert restaurant.get_item("Salmon Roll").available
    with pytest.raises(ValueError, match="currently unavailable"):
        app.add_to_cart("Salmon Roll")


def test_menu_timeout_has_retryable_error(app) -> None:
    app.menu_service_available = False
    app.browse_restaurant("Sushi Place")

    with pytest.raises(MenuLoadError, match="retry"):
        app.load_menu()

    app.menu_service_available = True
    assert app.retry_menu()


def test_payment_gateway_keeps_its_stateless_compatibility_api() -> None:
    result = PaymentGateway.process_payment(
        "4111111111111111",
        Decimal("10.00"),
    )

    assert result.authorized
    assert result.status == "authorized"


def test_checkout_rejects_unavailable_items_and_out_of_zone_addresses(app) -> None:
    app.browse_restaurant("Sushi Place")
    app.add_to_cart("Salmon Roll")
    app.cart.items["Salmon Roll"].item.available = False

    with pytest.raises(ValueError, match="currently unavailable"):
        app.checkout(Address("Main Street 12", "Madrid", "28001"))
    assert app.orders == []

    app.cart.items["Salmon Roll"].item.available = True
    with pytest.raises(ValueError, match="Outside delivery area"):
        app.checkout(
            Address(
                "10km away",
                "Madrid",
                "28001",
                distance_from_restaurant_km=10,
            )
        )


def test_order_uses_cart_snapshot_and_successful_payment_clears_cart(app) -> None:
    app.browse_restaurant("Sushi Place")
    app.add_to_cart("Salmon Roll")
    order = app.checkout(Address("Main Street 12", "Madrid", "28001"))
    app.update_cart_quantity("Salmon Roll", 3)

    assert order.items[0].quantity == 1
    assert app.submit_payment("4111111111111111", order)["authorized"]
    assert app.cart.is_empty


def test_session_restores_cart_orders_and_idempotent_payment_state(
    app, tmp_path
) -> None:
    app.browse_restaurant("Sushi Place")
    app.add_to_cart("Salmon Roll")
    order = app.checkout(Address("Main Street 12", "Madrid", "28001"))
    app.payment_gateway.simulate_next_timeout = True
    pending = app.submit_payment("4111111111111111", order)
    assert pending["status"] == "checking"

    session_file = tmp_path / "session.json"
    app.save_session(session_file)
    restored = FoodOrderingApp()
    restored.seed_demo_data()

    assert restored.load_session(session_file)
    assert restored.cart.items["Salmon Roll"].quantity == 1
    restored_order = restored.orders[0]
    assert restored_order.payment_status == "checking"
    assert restored.resolve_payment(restored_order)["authorized"]
    assert restored.submit_payment("4111111111111111", restored_order)["status"] == (
        "duplicate"
    )


def test_confirmation_and_delivery_fallback_are_available(app) -> None:
    app.browse_restaurant("Sushi Place")
    app.add_to_cart("Salmon Roll")
    order = app.checkout(Address("Main Street 12", "Madrid", "28001"))
    assert app.submit_payment("4111111111111111", order)["authorized"]
    assert order.confirmation_notification_sent

    order.restaurant_acknowledged = False
    app.notify_restaurant_delay(order)
    assert order.delay_notification_sent
    assert order.support_or_cancellation_available

    last_known = app.tracking_details(order)["location"]
    app.gps_available = False
    details = app.tracking_details(order)
    assert details["status"] == "Preparing"
    assert details["location"] == last_known
    assert details["location_is_stale"]


def test_cli_completes_demo_order(monkeypatch, tmp_path, capsys) -> None:
    choices = iter(
        [
            "1",
            "",
            "2",
            "Sushi Place",
            "Salmon Roll",
            "3",
            "",
            "4",
            "Main Street 12",
            "Madrid",
            "28001",
            "1.2",
            "4111111111111111",
            "5",
            "0",
        ]
    )
    monkeypatch.setattr("builtins.input", lambda _prompt: next(choices))
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    run_cli()

    output = capsys.readouterr().out
    assert "Payment approved." in output
    assert "ORD-1001" in output
    assert (tmp_path / ".food_ordering_app" / "session.json").exists()
