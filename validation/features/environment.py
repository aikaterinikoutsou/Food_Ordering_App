def before_scenario(context, scenario):
    if "blocked" in scenario.tags:
        scenario.skip("Blocked: required application behavior is not implemented.")
