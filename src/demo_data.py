"""Seed data for the local food-ordering demonstration."""

from decimal import Decimal

from .models import MenuItem, Restaurant


def create_demo_restaurants() -> list[Restaurant]:
    sushi = Restaurant(
        name="Sushi Place",
        cuisine="Japanese",
        rating=4.8,
        estimated_delivery_time_min=20,
        distance_km=1.2,
        delivery_radius_km=5,
        is_open=True,
    )
    sushi.add_item(
        MenuItem(
            name="Salmon Roll",
            description="Fresh salmon and rice",
            price=Decimal("10.00"),
            category="Sushi",
            allergens=["contains fish"],
            image_url="salmon-roll.jpg",
        )
    )
    sushi.add_item(
        MenuItem(
            name="Avocado Roll",
            description="Creamy avocado roll",
            price=Decimal("9.50"),
            category="Sushi",
            allergens=["contains sesame"],
            image_url="avocado-roll.jpg",
        )
    )

    pizza = Restaurant(
        name="Pizza Corner",
        cuisine="Italian",
        rating=4.7,
        estimated_delivery_time_min=25,
        distance_km=2.4,
        delivery_radius_km=6,
        is_open=True,
    )
    pizza.add_item(
        MenuItem(
            name="Margherita",
            description="Classic tomato basil pizza",
            price=Decimal("14.00"),
            category="Pizza",
            allergens=["contains gluten"],
            image_url="margherita.jpg",
        )
    )

    return [sushi, pizza]
