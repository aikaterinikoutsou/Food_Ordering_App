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

- `FoodOrderingApp.load_menu()` retrieves the categorized menu, and
  `get_menu_item_details()` provides descriptions, prices, and allergen data.
- Closed restaurants remain browsable, but `Restaurant.menu_for_browsing()`
  returns unavailable item views and the app blocks adding those items.
- Menu loading reports a retryable error when the menu service is unavailable;
  `FoodOrderingApp.retry_menu()` retries the operation.
- The menu service is simulated locally; no external menu backend is connected.
