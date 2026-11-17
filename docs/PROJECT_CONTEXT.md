# Project Context

## Purpose

Food Ordering App is a Python command-line demo of a food-ordering workflow. It
lets a customer discover restaurants, browse a menu, manage a cart, check out,
simulate payment, and track an order. It is an in-memory domain application with
local JSON session persistence, not a production ordering service.

## Technology and entry points

- Python 3.12 or newer
- `python -m src.app` starts the interactive command-line app.
- `python -m pytest` runs unit and functional tests in `test/`.
- `python -m behave --format pretty` runs the Gherkin acceptance scenarios in
  `validation/features/`.

Dependencies are declared in `requirements.txt`.

## Source layout

- `src/application.py` — `FoodOrderingApp` workflow orchestration.
- `src/cli.py` — interactive terminal interface and user input/output.
- `src/demo_data.py` — factory for the seeded restaurants and menu items.
- `src/session_store.py` — JSON encoding, decoding, and file persistence for the
  local session.
- `src/app.py` — compatibility exports and module entry point for
  `python -m src.app`.
- `src/models.py` — domain data models: `Address`, `Restaurant`, `MenuItem`,
  `Cart`, `CartItem`, `Order`, and `PaymentResult`.
- `src/services.py` — restaurant catalog/search, checkout rules, payment
  simulation, and delivery tracking.
- `test/` — pytest tests for domain rules, persistence, and CLI behavior.
- `validation/features/` — behavior specifications for the seven app features.
- `validation/features/steps/` — Behave step implementations.
- `docs/architecture/` — architecture diagrams and CRC documentation,
  including the project-wide class diagram at
  `docs/architecture/uml/project-class-diagram.md`.

## Main runtime flow

1. `run_cli()` creates `FoodOrderingApp`, seeds the demo catalog, and attempts
   to restore the saved session from
   `~/.food_ordering_app/session.json`.
2. The customer searches nearby demo restaurants and chooses a restaurant.
3. The app displays categorized menu items and supports cart operations.
4. Checkout validates that the cart is non-empty, its items remain available,
   it belongs to the selected restaurant, and any supplied delivery distance is
   within the restaurant's delivery radius.
5. Payment is simulated. Successful payment confirms the order and clears the
   cart; a payment timeout can be resolved without charging twice.
6. Order tracking returns a status and a simulated last-known courier location.
7. Choosing exit saves the cart, orders, payment state, and tracking locations
   to the local JSON session file.

## Seed data

`FoodOrderingApp.seed_demo_data()` creates:

- **Sushi Place** — Japanese cuisine, with Salmon Roll and Avocado Roll.
- **Pizza Corner** — Italian cuisine, with Margherita.

The demo card `4111111111111111` is approved by the simulated payment gateway.
A card number ending in `0002` simulates insufficient funds. These are test
behaviors only; no real payment is made.

## Feature coverage

The Gherkin features cover:

1. Restaurant discovery
2. Menu browsing
3. Cart management
4. Checkout
5. Payment
6. Order confirmation
7. Delivery tracking

The corresponding feature files are the behavior-level reference for these
scenarios. Keep step definitions aligned with the feature wording, and add or
update pytest coverage for domain behavior when changing implementation.

## Scope and limitations

- Restaurant catalog data is seeded at startup and held in memory; session
  persistence stores cart and order state locally as JSON.
- Payment, email/push notifications, restaurant acknowledgement, menu-service
  availability, and courier GPS are simulated. No external service is
  contacted.
- Address distance is validated only when a distance is supplied. The app does
  not geocode addresses, calculate routes, or obtain a customer's location.
- Courier location is a simulated coordinate and timestamp, not live GPS.
- The CLI is the only user interface.

Do not treat simulated behavior as a real payment, notification, location, or
restaurant integration.
