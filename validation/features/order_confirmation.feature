@FEAT-006
Feature: Order confirmation
  As a customer
  I want to receive confirmation of my order
  So that I know my order was accepted

  @TC-025 @passing @positive @high
  Scenario: Confirmation shown after successful payment
    Given the customer's payment has just succeeded
    When the customer views the post-payment screen
    Then a confirmation screen shows the order number, items, and total
    And an estimated delivery time is displayed

  @TC-026 @blocked @positive @medium
  Scenario: Confirmation notification is sent
    Given the order has been successfully placed
    When up to 2 minutes have passed
    Then the customer receives a confirmation email or push notification

  @TC-027 @blocked @edge @medium
  Scenario: Restaurant does not acknowledge the order in time
    Given the restaurant has not accepted the order within the SLA window
    When the SLA window elapses
    Then the customer is notified of the delay
    And a support or cancellation option is surfaced
