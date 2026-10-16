from copy import deepcopy
from decimal import Decimal

from behave import given, then, when


ITEM_PRICE = Decimal("10.00")


def _start_scenario(context):
    context.cart = {}
    context.meals = {}
    context.message = ""
    context.total_history = []
    context.persisted_cart = {}
    context.action_blocked = False


def _register_meal(context, name, restaurant="Sushi Place", available=True):
    context.meals[name] = {
        "available": available,
        "price": ITEM_PRICE,
        "restaurant": restaurant,
    }


def _cart_total(context):
    return sum(
        (item["price"] * item["quantity"] for item in context.cart.values()),
        start=Decimal("0.00"),
    )


def _record_total(context):
    context.total_history.append(_cart_total(context))


def _add_meal(context, name):
    meal = context.meals[name]
    if not meal["available"]:
        context.message = "This meal is currently unavailable."
        return False

    if context.cart:
        restaurants = {item["restaurant"] for item in context.cart.values()}
        if meal["restaurant"] not in restaurants:
            context.cart.clear()
            context.message = "Start a new cart to order from another restaurant."
            context.action_blocked = True
            context.persisted_cart = deepcopy(context.cart)
            _record_total(context)
            return False

    if name not in context.cart:
        context.cart[name] = {
            "price": meal["price"],
            "quantity": 0,
            "restaurant": meal["restaurant"],
        }
    context.cart[name]["quantity"] += 1
    context.persisted_cart = deepcopy(context.cart)
    _record_total(context)
    return True


def _set_quantity(context, name, quantity):
    if quantity <= 0:
        context.cart.pop(name, None)
        context.message = "Your cart is empty." if not context.cart else ""
    else:
        context.cart[name]["quantity"] = quantity
    context.persisted_cart = deepcopy(context.cart)
    _record_total(context)


@given('the meal "{meal}" is available')
def meal_is_available(context, meal):
    _start_scenario(context)
    _register_meal(context, meal)


@given('the meal "{meal}" is marked unavailable')
def meal_is_unavailable(context, meal):
    _start_scenario(context)
    _register_meal(context, meal, available=False)


@when('the customer taps "Add to cart" on "{meal}"')
def customer_adds_meal(context, meal):
    _add_meal(context, meal)


@then('"{meal}" appears in the cart with quantity {quantity:d}')
def meal_appears_with_quantity(context, meal, quantity):
    assert context.cart[meal]["quantity"] == quantity


@then("the cart total is updated to include it")
def cart_total_includes_added_meal(context):
    assert context.cart
    assert sum(item["quantity"] for item in context.cart.values()) == 1
    assert _cart_total(context) == ITEM_PRICE
    assert context.total_history[-1] == _cart_total(context)


@when('the customer attempts to add "{meal}" to the cart')
def customer_attempts_to_add_meal(context, meal):
    _add_meal(context, meal)


@then("the item is not added to the cart")
def item_is_not_added(context):
    assert context.cart == {}


@then("the customer sees a message that it is currently unavailable")
def unavailable_message_is_shown(context):
    assert "currently unavailable" in context.message


@given('"{meal}" is already in the cart with quantity {quantity:d}')
def meal_is_already_in_cart(context, meal, quantity):
    _start_scenario(context)
    _register_meal(context, meal)
    for _ in range(quantity):
        _add_meal(context, meal)


@when("the customer increases the quantity by {amount:d}")
def customer_increases_quantity(context, amount):
    meal = next(iter(context.cart))
    _set_quantity(context, meal, context.cart[meal]["quantity"] + amount)


@when("the customer decreases the quantity by {amount:d}")
def customer_decreases_quantity(context, amount):
    meal = next(iter(context.cart))
    _set_quantity(context, meal, context.cart[meal]["quantity"] - amount)


@then('the cart shows "{meal}" with quantity {quantity:d}')
def cart_shows_quantity(context, meal, quantity):
    assert context.cart[meal]["quantity"] == quantity


@then("the cart total is recalculated automatically after each change")
def cart_total_recalculated_after_each_change(context):
    assert len(context.total_history) >= 3
    assert context.total_history[-2] != context.total_history[-3]
    assert context.total_history[-1] != context.total_history[-2]
    assert context.total_history[-1] == _cart_total(context)


@given('"{meal}" is the only item in the cart with quantity {quantity:d}')
def meal_is_only_cart_item(context, meal, quantity):
    _start_scenario(context)
    _register_meal(context, meal)
    for _ in range(quantity):
        _add_meal(context, meal)


@when("the customer decreases the quantity to {quantity:d}")
def customer_sets_quantity(context, quantity):
    meal = next(iter(context.cart))
    _set_quantity(context, meal, quantity)


@then('"{meal}" is removed from the cart entirely')
def meal_is_removed(context, meal):
    assert meal not in context.cart


@then("the cart total updates to zero")
def cart_total_is_zero(context):
    assert _cart_total(context) == Decimal("0.00")


@then("an empty-cart message is shown")
def empty_cart_message_is_shown(context):
    assert not context.cart
    assert "cart is empty" in context.message.lower()


@given("the customer has added an item to the cart in the current session")
def customer_has_added_item(context):
    _start_scenario(context)
    _register_meal(context, "Salmon Roll")
    _add_meal(context, "Salmon Roll")
    context.cart_before_reload = deepcopy(context.cart)


@when("the customer reloads the page")
def customer_reloads_page(context):
    context.cart.clear()
    context.cart = deepcopy(context.persisted_cart)


@then("the cart still shows the same items and quantities")
def cart_is_persisted(context):
    assert context.cart == context.cart_before_reload


@given('the cart contains an item from "{restaurant}"')
def cart_has_item_from_restaurant(context, restaurant):
    _start_scenario(context)
    meal = f"{restaurant} meal"
    _register_meal(context, meal, restaurant=restaurant)
    _add_meal(context, meal)


@when('the customer attempts to add an item from "{restaurant}"')
def customer_adds_item_from_another_restaurant(context, restaurant):
    meal = f"{restaurant} meal"
    _register_meal(context, meal, restaurant=restaurant)
    _add_meal(context, meal)


@then("the app blocks the action")
def cross_restaurant_action_is_blocked(context):
    assert context.action_blocked


@then("the customer is prompted to start a new cart, clearing the current one")
def customer_is_prompted_to_start_new_cart(context):
    assert "start a new cart" in context.message.lower()
    assert context.cart == {}
