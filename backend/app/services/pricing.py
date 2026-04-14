"""
Pricing service: calculate order price based on material, thickness, and design complexity.
"""
from typing import Dict

# Base prices per material (EUR per unit, for a standard 500x400mm panel)
MATERIAL_BASE_PRICES: Dict[str, float] = {
    "cortenstaal": 89.0,
    "rvs": 149.0,
    "zwart_staal": 69.0,
}

# Thickness multipliers
THICKNESS_MULTIPLIERS: Dict[float, float] = {
    2.0: 1.0,
    3.0: 1.15,
    4.0: 1.30,
    6.0: 1.55,
}

# Complexity tiers: (max_score, multiplier)
COMPLEXITY_TIERS = [
    (50, 1.0),
    (150, 1.20),
    (400, 1.45),
    (float("inf"), 1.75),
]

SETUP_FEE = 25.0  # EUR fixed setup/programming fee
MIN_PRICE = 49.0  # EUR minimum order price


def calculate_price(
    material: str,
    thickness: float,
    complexity_score: float,
) -> Dict[str, float]:
    """
    Calculate the total price for a laser-cut vuurkorf.

    Args:
        material: one of cortenstaal / rvs / zwart_staal
        thickness: material thickness in mm (2, 3, 4, or 6)
        complexity_score: path complexity score from svg_utils.path_complexity_score()

    Returns:
        dict with base_price, material_price, complexity_surcharge, setup_fee, total
    """
    base = MATERIAL_BASE_PRICES.get(material, MATERIAL_BASE_PRICES["zwart_staal"])
    thickness_mult = THICKNESS_MULTIPLIERS.get(thickness, 1.0)

    complexity_mult = 1.0
    for max_score, mult in COMPLEXITY_TIERS:
        if complexity_score <= max_score:
            complexity_mult = mult
            break

    material_price = round(base * thickness_mult, 2)
    complexity_surcharge = round(material_price * (complexity_mult - 1.0), 2)
    subtotal = material_price + complexity_surcharge + SETUP_FEE
    total = round(max(subtotal, MIN_PRICE), 2)

    return {
        "material_price": material_price,
        "complexity_surcharge": complexity_surcharge,
        "setup_fee": SETUP_FEE,
        "total": total,
        "currency": "EUR",
    }
