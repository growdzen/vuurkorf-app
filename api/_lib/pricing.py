"""Pricing service — identical to backend version."""
from typing import Dict

MATERIAL_BASE_PRICES: Dict[str, float] = {
    "cortenstaal": 89.0,
    "rvs": 149.0,
    "zwart_staal": 69.0,
}

THICKNESS_MULTIPLIERS: Dict[float, float] = {
    2.0: 1.0,
    3.0: 1.15,
    4.0: 1.30,
    6.0: 1.55,
}

COMPLEXITY_TIERS = [
    (50, 1.0),
    (150, 1.20),
    (400, 1.45),
    (float("inf"), 1.75),
]

SETUP_FEE = 25.0
MIN_PRICE = 49.0


def calculate_price(material: str, thickness: float, complexity_score: float) -> Dict[str, float]:
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
