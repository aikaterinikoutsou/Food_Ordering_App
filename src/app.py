"""Compatibility exports and module entry point for the application."""

from .application import FoodOrderingApp
from .cli import run_cli

__all__ = ["FoodOrderingApp", "run_cli"]


if __name__ == "__main__":
    run_cli()
