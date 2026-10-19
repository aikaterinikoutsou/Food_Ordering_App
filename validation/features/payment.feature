@FEAT-005
Feature: Payment
  As a customer
  I want to pay for my order
  So that I can complete my purchase

  @TC-020 @positive @high
  Scenario: Pay successfully with a valid card
    Given the customer has entered valid card details with sufficient funds
    When the customer submits the payment
    Then the payment is authorized
    And the order moves to the "confirmed" state

  @TC-021 @negative @high
  Scenario: Payment declined due to insufficient funds
    Given the customer's card has insufficient funds
    When the customer submits the payment
    Then the order is not created
    And the customer sees the decline reason
    And the customer can retry with another payment method

  @TC-022 @negative @high
  Scenario: Payment gateway timeout
    Given the payment provider is simulating a timeout
    When the customer submits the payment
    Then the system does not double-charge the customer on retry
    And the customer sees a "checking payment status" message until resolved

  @TC-023 @negative @medium
  Scenario: Invalid card number is rejected by the payment service
    When the customer enters a malformed card number
    And the customer submits the payment form
    Then the payment is rejected with an invalid-card status
    And the order remains unconfirmed

  @TC-024 @edge @high
  Scenario: Duplicate submission from double-clicking Pay
    Given the customer is on the payment screen with valid details entered
    When the customer clicks "Pay" twice in quick succession
    Then only one charge is created
    And the second click is debounced or ignored
