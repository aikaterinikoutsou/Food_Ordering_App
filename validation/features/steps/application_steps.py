from decimal import Decimal

from behave import given, then, when

from src.app import FoodOrderingApp
from src.models import Address


def _start_app(context):
    context.app = FoodOrderingApp()
    context.app.seed_demo_data()
    context.order = None
    context.checkout_error = None
    context.payment_result = None
    context.total_history = []


def _add_salmon_roll(context, quantity=1):
    context.app.browse_restaurant("Sushi Place")
    for _ in range(quantity):
        context.app.add_to_cart("Salmon Roll")


def _record_cart_total(context):
    context.total_history.append(context.app.cart_total())


def _create_order(context):
    _start_app(context)
    _add_salmon_roll(context)
    context.order = context.app.checkout(
        Address("Main Street 12", "Madrid", "28001")
    )


@given("the customer has opened the app")
def customer_has_opened_app(context):
    _start_app(context)


@given('the meal "{meal}" is available')
def meal_is_available(context, meal):
    _start_app(context)
    context.app.browse_restaurant("Sushi Place")
    item = context.app.current_restaurant.get_item(meal)
    assert item is not None
    item.available = True
    context.meal = meal


@given('the meal "{meal}" is marked unavailable')
def meal_is_unavailable(context, meal):
    meal_is_available(context, meal)
    context.app.current_restaurant.get_item(meal).available = False


@when('the customer taps "Add to cart" on "{meal}"')
def customer_adds_meal(context, meal):
    context.app.add_to_cart(meal)
    _record_cart_total(context)


@when('the customer attempts to add "{meal}" to the cart')
def customer_attempts_to_add_meal(context, meal):
    try:
        context.app.add_to_cart(meal)
    except ValueError as error:
        context.message = str(error)


@then('"{meal}" appears in the cart with quantity {quantity:d}')
def meal_appears_with_quantity(context, meal, quantity):
    assert context.app.cart.items[meal].quantity == quantity


@then("the cart total is updated to include it")
def cart_total_includes_added_meal(context):
    assert context.app.cart_total() == Decimal("10.00")
    assert context.total_history[-1] == context.app.cart_total()


@then("the item is not added to the cart")
def item_is_not_added(context):
    assert context.app.cart.is_empty


@then("the customer sees a message that it is currently unavailable")
def unavailable_message_is_shown(context):
    assert "currently unavailable" in context.message


@given('"{meal}" is already in the cart with quantity {quantity:d}')
def meal_is_already_in_cart(context, meal, quantity):
    meal_is_available(context, meal)
    context.app.add_to_cart(meal)
    context.app.update_cart_quantity(meal, quantity)
    _record_cart_total(context)


@when("the customer increases the quantity by {amount:d}")
def customer_increases_quantity(context, amount):
    meal = context.meal
    current = context.app.cart.items[meal].quantity
    context.app.update_cart_quantity(meal, current + amount)
    _record_cart_total(context)


@when("the customer decreases the quantity by {amount:d}")
def customer_decreases_quantity(context, amount):
    meal = context.meal
    current = context.app.cart.items[meal].quantity
    context.app.update_cart_quantity(meal, current - amount)
    _record_cart_total(context)


@then('the cart shows "{meal}" with quantity {quantity:d}')
def cart_shows_quantity(context, meal, quantity):
    assert context.app.cart.items[meal].quantity == quantity


@then("the cart total is recalculated automatically after each change")
def cart_total_recalculated_after_each_change(context):
    assert len(context.total_history) >= 3
    assert context.total_history[-2] != context.total_history[-3]
    assert context.total_history[-1] != context.total_history[-2]
    assert context.total_history[-1] == context.app.cart_total()


@given('"{meal}" is the only item in the cart with quantity {quantity:d}')
def meal_is_only_cart_item(context, meal, quantity):
    meal_is_already_in_cart(context, meal, quantity)


@when("the customer decreases the quantity to {quantity:d}")
def customer_sets_quantity(context, quantity):
    context.app.update_cart_quantity(context.meal, quantity)


@then('"{meal}" is removed from the cart entirely')
def meal_is_removed(context, meal):
    assert meal not in context.app.cart.items


@then("the cart total updates to zero")
def cart_total_is_zero(context):
    assert context.app.cart_total() == Decimal("0.00")


@given('the cart contains an item from "{restaurant}"')
def cart_has_item_from_restaurant(context, restaurant):
    _start_app(context)
    context.app.browse_restaurant(restaurant)
    item_name = "Salmon Roll" if restaurant == "Sushi Place" else "Margherita"
    context.app.add_to_cart(item_name)
    context.original_cart = dict(context.app.cart.items)


@when('the customer attempts to add an item from "{restaurant}"')
def customer_adds_item_from_another_restaurant(context, restaurant):
    context.app.browse_restaurant(restaurant)
    item_name = "Salmon Roll" if restaurant == "Sushi Place" else "Margherita"
    try:
        context.app.add_to_cart(item_name)
    except ValueError as error:
        context.message = str(error)
        context.action_blocked = True


@then("the app blocks the action")
def cross_restaurant_action_is_blocked(context):
    assert context.action_blocked
    assert "new cart" in context.message.lower()


@then("the existing cart remains unchanged")
def existing_cart_remains_unchanged(context):
    assert context.app.cart.items == context.original_cart


@given("the customer has granted location permissions")
def customer_granted_location(context):
    context.location_granted = True


@given("the demo restaurants are available")
def demo_restaurants_are_available(context):
    assert len(context.app.catalog.restaurants) >= 2


@when("the customer performs a search with the default location")
def customer_searches_default_location(context):
    context.results = context.app.search_restaurants(40.4168, -3.7038)


@then("the results list shows restaurants sorted by distance")
def results_are_sorted_by_distance(context):
    distances = [restaurant.distance_km for restaurant in context.results]
    assert distances == sorted(distances)


@then("each result has a name, rating, and estimated delivery time")
def each_result_has_summary_fields(context):
    assert context.results
    assert all(
        restaurant.name
        and restaurant.rating is not None
        and restaurant.estimated_delivery_time_min > 0
        for restaurant in context.results
    )


@given("search results include at least 2 cuisine types")
def results_include_multiple_cuisines(context):
    context.results = context.app.search_restaurants(40.4168, -3.7038)
    assert len({restaurant.cuisine for restaurant in context.results}) >= 2


@when('the customer applies the "{cuisine}" filter')
def customer_filters_cuisine(context, cuisine):
    context.results = context.app.search_restaurants(
        40.4168, -3.7038, cuisine=cuisine
    )


@then('only restaurants tagged "{cuisine}" are shown')
def only_filtered_cuisine_is_shown(context, cuisine):
    assert context.results
    assert all(restaurant.cuisine.lower() == cuisine.lower() for restaurant in context.results)


@when("the customer clears the filter")
def customer_clears_cuisine_filter(context):
    context.results = context.app.search_restaurants(40.4168, -3.7038)


@then("all restaurants are shown again")
def all_restaurants_are_shown_again(context):
    assert len(context.results) == len(context.app.catalog.restaurants)


@given("the cart contains at least 1 available item")
def cart_contains_available_item(context):
    _start_app(context)
    _add_salmon_roll(context)


@when('the customer taps "Checkout"')
def customer_taps_checkout(context):
    context.order = context.app.checkout(
        Address("Main Street 12", "Madrid", "28001")
    )


@then("the order summary shows an itemized list")
def order_summary_is_itemized(context):
    assert context.order.items
    assert context.order.items[0].item.name == "Salmon Roll"


@then("the subtotal, delivery fee, and total are displayed")
def order_totals_are_available(context):
    assert context.order.subtotal == Decimal("10.00")
    assert context.order.delivery_fee == Decimal("3.50")
    assert context.order.total == Decimal("13.50")


@given("the cart is empty")
def cart_is_empty(context):
    _start_app(context)
    context.app.browse_restaurant("Sushi Place")


@when("the customer navigates directly to the checkout screen")
def customer_navigates_to_checkout(context):
    try:
        context.app.checkout(Address("Main Street 12", "Madrid", "28001"))
    except ValueError as error:
        context.checkout_error = str(error)


@then("checkout is rejected because the cart is empty")
def checkout_rejects_empty_cart(context):
    assert context.checkout_error is not None
    assert "empty cart" in context.checkout_error.lower()


@given("the customer is on the checkout screen")
def customer_is_on_checkout_screen(context):
    cart_contains_available_item(context)


@when("the customer enters a valid address and confirms")
def customer_confirms_valid_address(context):
    context.address = Address("Main Street 12", "Madrid", "28001")
    context.order = context.app.checkout(context.address)


@then("the address is saved for this order")
def address_is_saved_to_order(context):
    assert context.order.to_dict()["address"] == context.address.as_dict()


@given("the restaurant's delivery radius is 5km")
def restaurant_delivery_radius_is_five_km(context):
    cart_contains_available_item(context)
    context.restaurant = context.app.current_restaurant
    assert context.restaurant.delivery_radius_km == 5


@when("the customer enters an address 10km away")
def customer_enters_distant_address(context):
    context.address = Address("10km away", "Madrid", "28001")
    try:
        context.order = context.app.checkout(context.address)
    except ValueError as error:
        context.checkout_error = str(error)


@then("checkout is blocked")
def checkout_is_blocked(context):
    assert context.checkout_error is not None


@then('the message "Outside delivery area" is shown')
def outside_delivery_area_message_is_shown(context):
    assert context.checkout_error == "Outside delivery area"


@given("the customer has entered valid card details with sufficient funds")
def customer_has_valid_card(context):
    _create_order(context)
    context.card_number = "4111111111111111"


@given("the customer's card has insufficient funds")
def customer_card_has_insufficient_funds(context):
    _create_order(context)
    context.card_number = "4111111111111111"


@when("the customer submits the payment")
def customer_submits_payment(context):
    context.payment_result = context.app.submit_payment(
        context.card_number, context.order
    )


@then("the payment is authorized")
def payment_is_authorized(context):
    assert context.payment_result["authorized"] is True


@then('the order moves to the "confirmed" state')
def order_is_confirmed(context):
    assert context.order.status == "confirmed"


@then("the order is not created")
def order_is_not_created(context):
    assert context.payment_result["authorized"] is False
    assert context.order.status == "pending"


@then("the customer sees the decline reason")
def decline_reason_is_available(context):
    assert context.payment_result["message"]


@then("the customer can retry with another payment method")
def customer_can_retry_payment(context):
    retry = context.app.submit_payment("4111111111111111", context.order)
    assert retry["authorized"] is True


@when("the customer enters a malformed card number")
def customer_enters_malformed_card(context):
    _create_order(context)
    context.card_number = "1234"


@when("the customer submits the payment form")
def customer_submits_payment_form(context):
    customer_submits_payment(context)


@then("the payment is rejected with an invalid-card status")
def invalid_card_is_rejected(context):
    assert context.payment_result["authorized"] is False
    assert context.payment_result["status"] == "invalid"


@then("the order remains unconfirmed")
def order_remains_unconfirmed(context):
    assert context.order.status == "pending"
    assert context.order.payment_status == "pending"


@given("the customer is on the payment screen with valid details entered")
def customer_is_ready_to_pay(context):
    customer_has_valid_card(context)


@when('the customer clicks "Pay" twice in quick succession')
def customer_clicks_pay_twice(context):
    context.first_payment = context.app.submit_payment(
        context.card_number, context.order
    )
    context.second_payment = context.app.submit_payment(
        context.card_number, context.order, is_duplicate=True
    )


@then("only one charge is created")
def only_one_payment_is_authorized(context):
    assert context.first_payment["authorized"] is True
    assert context.second_payment["authorized"] is False
    assert context.second_payment["status"] == "duplicate"


@then("the second click is debounced or ignored")
def second_payment_is_ignored(context):
    assert context.second_payment["status"] == "duplicate"


@given("the customer's payment has just succeeded")
def customer_payment_has_succeeded(context):
    _create_order(context)
    context.app.submit_payment("4111111111111111", context.order)


@when("the customer views the post-payment screen")
def customer_views_confirmation(context):
    context.confirmation = context.order.to_dict()


@then("a confirmation screen shows the order number, items, and total")
def confirmation_contains_order_details(context):
    assert context.confirmation["order_number"]
    assert context.confirmation["items"]
    assert context.confirmation["total"] == "13.50"


@then("an estimated delivery time is displayed")
def estimated_delivery_time_is_displayed(context):
    assert context.confirmation["estimated_delivery_time_min"] > 0


@given("the order has been confirmed and accepted by the restaurant")
def confirmed_order_is_accepted(context):
    customer_payment_has_succeeded(context)


@when('the customer opens "Track order"')
def customer_opens_order_tracking(context):
    context.tracking_progress = context.app.track_order(context.order)


@then("the status progresses through Preparing, Out for delivery, and Delivered")
def tracking_returns_status_sequence(context):
    assert context.tracking_progress == [
        "Preparing",
        "Out for delivery",
        "Delivered",
    ]


@given('the backend marks the order as "delivered" directly')
def backend_marks_order_delivered(context):
    _create_order(context)
    context.order.status = "delivered"


@when("the customer views the tracking screen")
def customer_views_tracking(context):
    context.current_tracking_status = context.app.tracker.current_status(
        context.order
    )


@then('the current order status is "Delivered"')
def current_order_status_is_delivered(context):
    assert context.current_tracking_status == "Delivered"
