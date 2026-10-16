@FEAT-001
Feature: Restaurant discovery
  As a customer
  I want to search for nearby restaurants
  So that I can choose where to order from

  Background:
    Given the customer has opened the app

  @TC-001 @positive @high
  Scenario: Search returns nearby restaurants
    Given the customer has granted location permissions
    And at least 3 restaurants are within 5km of the customer
    When the customer performs a search with the default location
    Then the results list shows restaurants sorted by distance
    And each result shows a name, rating, and estimated delivery time

  @TC-002 @edge @medium
  Scenario: Search with no results nearby
    Given no restaurants are within 50km of the customer location
    When the customer performs a search
    Then an empty-state message "No restaurants found nearby" is shown
    And no error or blank screen is displayed

  @TC-003 @negative @high
  Scenario: Search with location services disabled
    Given the customer has denied location permission
    When the customer attempts a search
    Then the app prompts for a manual address or to enable location
    And the app does not crash

  @TC-004 @positive @medium
  Scenario: Filter restaurants by cuisine type
    Given search results include at least 2 cuisine types
    When the customer applies the "Italian" filter
    Then only restaurants tagged "Italian" are shown
    And the customer can clear the filter to see all results again
