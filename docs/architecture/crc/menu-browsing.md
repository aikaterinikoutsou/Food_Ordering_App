# CRC Cards: Menu Browsing

Scope: `Menu browsing` (`@FEAT-002`) only. Responsibilities below describe the
classes involved in the feature; they do not cover ordering, payment, or other
features.

## FoodOrderingApp

| Class | Responsibilities | Collaborators |
|---|---|---|
| `FoodOrderingApp` | Select a restaurant by name; retain the selected restaurant as the current browsing context; provide the selected restaurant to the caller. | `RestaurantCatalog`, `Restaurant` |

## RestaurantCatalog

| Class | Responsibilities | Collaborators |
|---|---|---|
| `RestaurantCatalog` | Look up a restaurant by name and report when it cannot be found. | `Restaurant`, `FoodOrderingApp` |

## Restaurant

| Class | Responsibilities | Collaborators |
|---|---|---|
| `Restaurant` | Organize menu items by category; add and find items; expose whether the restaurant is open. | `MenuItem`, `FoodOrderingApp` |

## MenuItem

| Class | Responsibilities | Collaborators |
|---|---|---|
| `MenuItem` | Hold the menu item's name, description, price, category, allergen tags, image reference, and availability; provide these details for display. | `Restaurant` |

## Feature coverage notes

- The current classes support selecting a restaurant and retrieving its categorized
  menu items and item details.
- The closed-restaurant scenario needs menu items to become unavailable when the
  restaurant is closed. `Restaurant.is_menu_viewable()` currently always returns
  `True`, and no current logic connects `is_open` to item availability.
- Backend timeout handling and a retry option are not represented in the current
  menu-browsing classes and would require a menu-loading boundary that can report
  and retry failures.
