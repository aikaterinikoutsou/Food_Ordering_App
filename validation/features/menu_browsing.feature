@FEAT-002
Feature: Menu browsing
  As a customer
  I want to view a restaurant's menu
  So that I can select food to order

  @TC-005 @positive @high
  Scenario: View full menu for a restaurant
    Given the restaurant "Sushi Place" has an active menu with categories
    When the customer selects "Sushi Place" from the results
    Then the menu loads showing categories, item names, prices, and images

  @TC-006 @edge @medium
  Scenario: View menu for a currently closed restaurant
    Given a restaurant is outside its operating hours
    When the customer selects that restaurant
    Then the menu is viewable in browse-only mode
    And items are marked unavailable
    And "Add to cart" is not allowed on any item

  @TC-007 @negative @high
  Scenario: Menu fails to load due to a backend timeout
    Given the menu service is unreachable
    When the customer selects a restaurant
    Then the app shows a clear error message with a retry option
    And the app does not hang indefinitely

  @TC-008 @positive @low
  Scenario: View item details with allergen info
    Given the item "Salmon Roll" has allergen metadata set
    When the customer taps on "Salmon Roll"
    Then the detail view shows the description and price
    And allergen tags such as "contains fish" are displayed
