@FEAT-004
Feature: Checkout
  As a customer
  I want to review my order and enter delivery details
  So that I can confirm my order before paying

  @TC-015 @passing @positive @high
  Scenario: Proceed to checkout with a valid cart
    Given the cart contains at least 1 available item
    When the customer taps "Checkout"
    Then the order summary shows an itemized list
    And the subtotal, delivery fee, and total are displayed

  @TC-016 @passing @negative @medium
  Scenario: Checkout with an empty cart
    Given the cart is empty
    When the customer navigates directly to the checkout screen
    Then checkout is rejected because the cart is empty

  @TC-017 @passing @positive @high
  Scenario: Enter a valid delivery address
    Given the customer is on the checkout screen
    When the customer enters a valid address and confirms
    Then the address is saved for this order

  @TC-018 @failing @negative @high
  Scenario: Enter an address outside the delivery zone
    Given the restaurant's delivery radius is 5km
    When the customer enters an address 10km away
    Then checkout is blocked
    And the message "Outside delivery area" is shown

  @TC-019 @blocked @edge @high
  Scenario: Item becomes unavailable mid-checkout
    Given the customer has reached the checkout screen
    When an item in the cart is marked unavailable by the backend
    And the customer attempts to confirm the order
    Then the customer is notified before payment
    And the customer must remove or replace the item before proceeding
