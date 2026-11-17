from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from time import monotonic

from behave import given, then, when

from src.app import FoodOrderingApp
from src.models import Address
from src.services import LocationPermissionError, MenuLoadError


def _create_paid_order(context):
    context.app.browse_restaurant("Sushi Place")
    context.app.add_to_cart("Salmon Roll")
    order = context.app.checkout(Address("Main Street 12", "Madrid", "28001"))
    context.app.submit_payment("4111111111111111", order)
    context.order = order


def _session_file(context):
    if not hasattr(context, "session_directory"):
        context.session_directory = TemporaryDirectory()
    return Path(context.session_directory.name) / "session.json"


@given("the customer has added an item to the cart in the current session")
def customer_has_added_item_this_session(context):
    context.app.browse_restaurant("Sushi Place")
    context.app.add_to_cart("Salmon Roll")
    context.saved_cart = {
        name: entry.quantity for name, entry in context.app.cart.items.items()
    }


@when("the customer reloads the page")
def customer_reloads_page(context):
    path = _session_file(context)
    context.app.save_session(path)
    context.reloaded_app = FoodOrderingApp()
    context.reloaded_app.seed_demo_data()
    context.reloaded_app.load_session(path)


@then("the cart still shows the same items and quantities")
def cart_is_restored_after_reload(context):
    assert {
        name: entry.quantity for name, entry in context.reloaded_app.cart.items.items()
    } == context.saved_cart


@given("the customer has reached the checkout screen")
def customer_reached_checkout(context):
    context.app.browse_restaurant("Sushi Place")
    context.app.add_to_cart("Salmon Roll")


@when("an item in the cart is marked unavailable by the backend")
def cart_item_marked_unavailable(context):
    context.app.cart.items["Salmon Roll"].item.available = False


@when("the customer attempts to confirm the order")
def customer_attempts_to_confirm_order(context):
    try:
        context.order = context.app.checkout(
            Address("Main Street 12", "Madrid", "28001")
        )
    except ValueError as error:
        context.checkout_error = str(error)


@then("the customer is notified before payment")
def customer_is_notified_item_unavailable(context):
    assert context.checkout_error
    assert "unavailable" in context.checkout_error.lower()
    assert context.order is None


@then("the customer must remove or replace the item before proceeding")
def unavailable_item_must_be_removed(context):
    assert context.app.cart.items["Salmon Roll"].item.available is False
    assert context.app.orders == []


@given('the restaurant "{restaurant}" has an active menu with categories')
def restaurant_has_active_menu(context, restaurant):
    context.restaurant = context.app.browse_restaurant(restaurant)
    assert context.restaurant.is_open
    assert context.restaurant.menu


@when('the customer selects "{restaurant}" from the results')
def customer_selects_restaurant(context, restaurant):
    context.app.browse_restaurant(restaurant)
    context.menu = context.app.load_menu()


@then("the menu loads showing categories, item names, prices, and images")
def menu_contains_display_details(context):
    assert context.menu
    assert all(
        item.category == category and item.name and item.price >= 0 and item.image_url
        for category, items in context.menu.items()
        for item in items
    )


@given("a restaurant is outside its operating hours")
def restaurant_outside_hours(context):
    context.restaurant = context.app.catalog.get_by_name("Sushi Place")
    context.restaurant.is_open = False


@when("the customer selects that restaurant")
def customer_selects_closed_restaurant(context):
    context.app.browse_restaurant(context.restaurant.name)
    context.menu = context.app.load_menu()


@then("the menu is viewable in browse-only mode")
def menu_shown_browse_only(context):
    assert context.menu
    assert all(not item.available for items in context.menu.values() for item in items)


@then("items are marked unavailable")
def closed_restaurant_items_unavailable(context):
    assert all(not item.available for items in context.menu.values() for item in items)


@then('"{action}" is not allowed on any item')
def adding_item_is_blocked(context, action):
    item = next(iter(context.restaurant.all_items()))
    try:
        context.app.add_to_cart(item.name)
    except ValueError as error:
        context.menu_action_error = str(error)
    assert context.menu_action_error
    assert "unavailable" in context.menu_action_error.lower()
    assert context.app.cart.is_empty


@given("the menu service is unreachable")
def menu_service_is_unreachable(context):
    context.app.menu_service_available = False


@when("the customer selects a restaurant")
def customer_selects_restaurant_with_menu_failure(context):
    context.app.browse_restaurant("Sushi Place")
    context.menu_load_started = monotonic()
    try:
        context.app.load_menu()
    except MenuLoadError as error:
        context.menu_error = str(error)
    context.menu_load_elapsed = monotonic() - context.menu_load_started


@then("the app shows a clear error message with a retry option")
def menu_failure_has_retry_message(context):
    assert "retry" in context.menu_error.lower()
    assert context.app.last_menu_error == context.menu_error


@then("the app does not hang indefinitely")
def menu_failure_returns_promptly(context):
    assert context.menu_load_elapsed < 1


@given('the item "{item_name}" has allergen metadata set')
def item_has_allergen_metadata(context, item_name):
    context.app.browse_restaurant("Sushi Place")
    context.menu_item = context.app.get_menu_item_details(item_name)
    assert context.menu_item.allergens


@when('the customer taps on "{item_name}"')
def customer_views_menu_item(context, item_name):
    context.item_details = context.app.get_menu_item_details(item_name)


@then("the detail view shows the description and price")
def item_detail_has_description_and_price(context):
    assert context.item_details.description
    assert context.item_details.price > 0


@then('allergen tags such as "{allergen}" are displayed')
def item_detail_displays_allergens(context, allergen):
    assert allergen in context.item_details.allergens


@given("an active order exists for the customer")
def active_order_exists(context):
    _create_paid_order(context)
    context.app.save_session(_session_file(context))


@when("the customer closes and reopens the app")
def customer_reopens_app(context):
    context.restarted_app = FoodOrderingApp()
    context.restarted_app.seed_demo_data()
    context.restarted_app.load_session(_session_file(context))


@then("the tracking screen reloads the current status correctly")
def tracking_status_reloaded(context):
    context.reloaded_order = context.restarted_app.orders[-1]
    context.reloaded_tracking = context.restarted_app.tracking_details(
        context.reloaded_order
    )
    assert context.reloaded_tracking["status"] == "Preparing"


@then("the status is not a stale or cached value")
def tracking_status_current(context):
    assert context.reloaded_tracking["status"] == (
        context.restarted_app.tracker.current_status(context.reloaded_order)
    )


@given("the courier's GPS signal is lost temporarily")
def courier_gps_temporarily_lost(context):
    _create_paid_order(context)
    context.app.gps_available = False


@then("the app shows the last known location with a timestamp")
def last_known_courier_location_is_shown(context):
    location = context.tracking_details["location"]
    assert location["latitude"] is not None
    assert location["longitude"] is not None
    datetime.fromisoformat(location["updated_at"])
    assert context.tracking_details["location_is_stale"]


@then("the map does not break or the app does not crash")
def tracking_fallback_is_valid(context):
    assert context.tracking_details["status"]
    assert context.tracking_details["location"]


@given("the order has been successfully placed")
def order_successfully_placed(context):
    _create_paid_order(context)


@when("up to 2 minutes have passed")
def confirmation_notification_window_passed(context):
    context.notification_checked = context.order.confirmation_notification_sent


@then("the customer receives a confirmation email or push notification")
def confirmation_notification_was_sent(context):
    assert context.notification_checked


@given("the restaurant has not accepted the order within the SLA window")
def restaurant_has_not_acknowledged_order(context):
    _create_paid_order(context)
    context.order.restaurant_acknowledged = False


@when("the SLA window elapses")
def restaurant_acknowledgement_sla_elapses(context):
    context.app.notify_restaurant_delay(context.order)


@then("the customer is notified of the delay")
def customer_is_notified_of_delay(context):
    assert context.order.delay_notification_sent


@then("a support or cancellation option is surfaced")
def support_or_cancel_option_is_available(context):
    assert context.order.support_or_cancellation_available


@given("the payment provider is simulating a timeout")
def payment_provider_simulates_timeout(context):
    context.app.browse_restaurant("Sushi Place")
    context.app.add_to_cart("Salmon Roll")
    context.order = context.app.checkout(Address("Main Street 12", "Madrid", "28001"))
    context.app.payment_gateway.simulate_next_timeout = True
    context.card_number = "4111111111111111"


@then("the system does not double-charge the customer on retry")
def payment_retry_is_idempotent(context):
    assert context.payment_result["status"] == "checking"
    resolved = context.app.resolve_payment(context.order)
    retry = context.app.submit_payment(context.card_number, context.order)
    assert resolved["authorized"]
    assert retry["status"] == "duplicate"
    assert context.order.payment_status == "paid"


@then('the customer sees a "checking payment status" message until resolved')
def payment_timeout_explains_pending_status(context):
    assert "checking payment status" in context.payment_result["message"].lower()


@given("no restaurants are within 50km of the customer location")
def no_restaurants_within_radius(context):
    for restaurant in context.app.catalog.restaurants:
        restaurant.distance_km = 60


@when("the customer performs a search")
def customer_searches_without_location(context):
    context.results = context.app.search_restaurants(40.4168, -3.7038)


@then('an empty-state message "{message}" is shown')
def restaurant_search_empty_state(context, message):
    assert not context.results
    assert context.app.search_message == message


@then("no error or blank screen is displayed")
def restaurant_search_has_safe_empty_state(context):
    assert context.app.search_message


@given("the customer has denied location permission")
def customer_denies_location_permission(context):
    context.location_permission_granted = False


@when("the customer attempts a search")
def customer_searches_without_permission(context):
    try:
        context.app.search_restaurants(None, None)
    except LocationPermissionError as error:
        context.location_error = str(error)


@then("the app prompts for a manual address or to enable location")
def location_permission_has_manual_fallback(context):
    assert "manual address" in context.app.search_message.lower()


@then("the app does not crash")
def location_permission_error_is_handled(context):
    assert context.location_error
