@FEAT-007
Feature: Delivery tracking
  As a customer
  I want to track my order
  So that I know when it will arrive

  @TC-028 @positive @high
  Scenario: View live order status
    Given the order has been confirmed and accepted by the restaurant
    When the customer opens "Track order"
    Then the status progresses through Preparing, Out for delivery, and Delivered
    And updates are reflected in real time

  @TC-029 @positive @medium
  Scenario: Track an order after an app restart
    Given an active order exists for the customer
    When the customer closes and reopens the app
    Then the tracking screen reloads the current status correctly
    And the status is not a stale or cached value

  @TC-030 @edge @low
  Scenario: Tracking when courier location is temporarily unavailable
    Given the courier's GPS signal is lost temporarily
    When the customer views the tracking screen
    Then the app shows the last known location with a timestamp
    And the map does not break or the app does not crash

  @TC-031 @negative @medium
  Scenario: Order marked delivered without being tracked live
    Given the backend marks the order as "delivered" directly
    When the customer views the tracking screen
    Then the status updates correctly to "Delivered"
    And the UI does not get stuck on an earlier stage
