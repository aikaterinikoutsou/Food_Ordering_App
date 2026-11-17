from src.app import FoodOrderingApp


def before_scenario(context, scenario):
    context.app = FoodOrderingApp()
    context.app.seed_demo_data()
    context.order = None
    context.checkout_error = None
    context.payment_result = None


def after_scenario(context, scenario):
    session_directory = getattr(context, "session_directory", None)
    if session_directory is not None:
        session_directory.cleanup()
        del context.session_directory
