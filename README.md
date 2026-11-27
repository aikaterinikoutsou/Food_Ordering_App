# Food Ordering App

A Python command-line food-ordering app that supports finding restaurants, browsing menus, managing a cart, checking out, simulating payment, receiving order updates, and tracking orders.

## Features

- Search restaurants by cuisine and list results by distance.
- Browse categorized menus, view item details and allergens, and prevent ordering unavailable items.
- Save and restore carts and orders across app restarts.
- Update item quantities and calculate the cart subtotal.
- Validate checkout items and delivery addresses against a restaurant's delivery radius.
- Create itemized orders with subtotal, delivery fee, and total.
- Simulate approved, declined, timed-out, and duplicate payments with idempotent retries.
- Track order status, provide a last-known courier location when GPS is unavailable, and surface restaurant-delay options.
- Seeded demo restaurants and menu items for trying the workflow.

## Requirements

- Python 3.12 or newer
- `pip`

The project dependencies, including the Ruff formatter and linter, are listed in
[`requirements.txt`](requirements.txt).

## Setup

From the project directory, create and activate a virtual environment, then install the dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell blocks script execution, allow scripts for the current terminal session and activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

If the `py` launcher is unavailable, use an installed Python executable to create the environment, for example:

```powershell
python -m venv .venv
```

## Run the app

Run from the project directory so Python can resolve the `src` package:

```powershell
python -m src.app
```

The app offers an interactive terminal menu for searching demo restaurants, browsing and adding menu items, checking the cart, completing checkout, and tracking the latest order. Session data is saved under `~/.food_ordering_app/session.json` when you exit, and restored the next time you run the app.

The payment gateway is simulated. The demo card `4111111111111111` is approved, while a card number ending in `0002` simulates insufficient funds. No actual payment is processed.

## Run tests

Run the unit tests with pytest:

```powershell
python -m pytest
```

Check and format Python code with Ruff:

```powershell
python -m ruff check .
python -m ruff format --check .
```

GitHub Actions runs pytest, all Behave feature suites, and both Ruff checks for
every pull request and every push to `main`.

Gherkin scenarios and their Behave step definitions are in `validation/features`. Run all seven feature suites with:

```powershell
python -m behave --format pretty
```

The Behave suite covers restaurant discovery, menu browsing, cart management, checkout, payment, order confirmation, and delivery tracking.

## Project structure

```text
src/
  app.py          Compatibility exports and application entry point
  application.py  Application workflow orchestration
  cli.py          Interactive terminal interface
  demo_data.py    Seeded restaurants and menu data
  models.py       Address, restaurant, menu, cart, payment, and order models
  session_store.py JSON session persistence
  services.py     Restaurant catalog, checkout, payment, and delivery services
test/             Pytest unit and functional tests
validation/
  features/       Gherkin specifications and Behave step implementations
docs/             Architecture diagrams
```

## Current scope

This is a local learning/demo application. Restaurant data is seeded in memory; session data is persisted locally as JSON. Payment, email/push notification, restaurant acknowledgement, and courier GPS are simulated domain behaviors rather than integrations with external providers. Delivery distance is checked when supplied with the address; the app does not geocode addresses or calculate live routes.
