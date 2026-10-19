# Food Ordering App

A Python project that models the main steps of a food-ordering workflow: finding restaurants, browsing menus, managing a cart, checking out, submitting payment, and tracking an order. The current app is a command-line demonstration of the domain logic rather than a web or mobile interface.

## Features

- Search restaurants by cuisine and list results by distance.
- Browse a restaurant menu and add available items to a single-restaurant cart.
- Update item quantities and calculate the cart subtotal.
- Create an order with an itemized subtotal, delivery fee, and total.
- Simulate payment approval, invalid card numbers, and duplicate submissions.
- Return delivery progress statuses for an order.
- Seeded demo restaurants and menu items for trying the workflow.

## Requirements

- Python 3.12 or newer
- `pip`

The project dependencies are listed in [`requirements.txt`](requirements.txt).

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

## Run the demo

Run from the project directory so Python can resolve the `src` package:

```powershell
python -m src.app
```

The demo seeds Sushi Place and Pizza Corner, searches for restaurants, adds a menu item to the cart, creates an order, submits a simulated payment, and prints delivery statuses.

## Run tests

Run the unit tests with pytest:

```powershell
python -m pytest
```

Gherkin scenarios and their Behave step definitions are in `validation/features`. Run the suite to see the actual results for the current code:

```powershell
python -m behave --format pretty
```

Behave reports scenario failures from failed assertions or errors in step definitions. Scenarios with undefined steps are reported as undefined/errors, and their remaining steps are skipped; they are not pre-labeled or automatically skipped as blocked.

## Project structure

```text
src/
  app.py          Application workflow and demo entry point
  models.py       Address, restaurant, menu, cart, payment, and order models
  services.py     Restaurant catalog, checkout, payment, and delivery services
test/             Pytest unit tests
validation/
  features/       Gherkin behavior specifications
docs/             Architecture diagrams
```

## Current scope

This is a learning/demo application: data is held in memory, payment is simulated, and there is no user interface or external payment provider. Delivery-address validation and delivery tracking are simplified placeholders; the feature files describe broader expected behaviors and are not all backed by step definitions yet.
