@FEAT-003
Feature: Cart management
  As a customer
  I want to add, remove, and adjust items in my cart
  So that I can manage my order before checkout

  @TC-009 @US-005 @positive @high
  Scenario: Add an available item to the cart
    Given the meal "Salmon Roll" is available
    When the customer taps "Add to cart" on "Salmon Roll"
    Then "Salmon Roll" appears in the cart with quantity 1
    And the cart total is updated to include it

  @TC-010 @US-005 @negative @high
  Scenario: Attempt to add an unavailable item
    Given the meal "Salmon Roll" is marked unavailable
    When the customer attempts to add "Salmon Roll" to the cart
    Then the item is not added to the cart
    And the customer sees a message that it is currently unavailable

  @TC-011 @US-007 @positive @medium
  Scenario: Increase and decrease item quantity
    Given "Salmon Roll" is already in the cart with quantity 1
    When the customer increases the quantity by 2
    And the customer decreases the quantity by 1
    Then the cart shows "Salmon Roll" with quantity 2
    And the cart total is recalculated automatically after each change

  @TC-012 @US-006 @edge @medium
  Scenario: Decrease quantity to zero removes the item
    Given "Salmon Roll" is the only item in the cart with quantity 1
    When the customer decreases the quantity to 0
    Then "Salmon Roll" is removed from the cart entirely
    And the cart total updates to zero

  @TC-013 @US-005 @positive @high
  Scenario: Cart persists after a page reload
    Given the customer has added an item to the cart in the current session
    When the customer reloads the page
    Then the cart still shows the same items and quantities

  @TC-014 @negative @high
  Scenario: Reject an item from a different restaurant without changing the cart
    Given the cart contains an item from "Sushi Place"
    When the customer attempts to add an item from "Pizza Corner"
    Then the app blocks the action
    And the existing cart remains unchanged
