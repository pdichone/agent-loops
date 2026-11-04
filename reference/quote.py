"""Reference solution. Never shown to the model; it only proves the tests agree with SPEC.md."""

import math
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

TAX = {"US": Decimal("0.08"), "CA": Decimal("0.13"), "MX": Decimal("0.16")}


def _d(x) -> Decimal:
    return Decimal(str(x))


def _cents(x: Decimal) -> Decimal:
    return x.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def quote(cart: dict) -> dict:
    items = cart.get("items") or []
    if not items:
        raise ValueError("empty cart")
    for it in items:
        if not isinstance(it.get("qty"), int) or it["qty"] < 1:
            raise ValueError("bad qty")
        if it["price"] < 0:
            raise ValueError("negative price")
    country = cart.get("country")
    if country not in TAX:
        raise ValueError("unsupported country")
    coupon = (cart.get("coupon") or "").strip().upper()
    if coupon and coupon not in {"KETTLE10", "SAVE15", "FREESHIP"}:
        raise ValueError("unknown coupon")

    goods = [it for it in items if it.get("category") != "gift_card"]
    subtotal = sum(_d(it["price"]) * it["qty"] for it in items)
    discountable = sum((_d(it["price"]) * it["qty"] for it in goods), Decimal(0))

    off = Decimal(0)
    if coupon == "KETTLE10":
        off = sum((_d(it["price"]) * it["qty"] for it in goods if it.get("category") == "kettles"), Decimal(0)) * Decimal("0.10")
    elif coupon == "SAVE15" and discountable >= 100:
        off = Decimal(15)
    if cart.get("member"):
        off += (discountable - off) * Decimal("0.05")
    off = min(off, discountable)
    discount = _cents(off)
    merch = discountable - discount

    weight = sum((_d(it["weight_kg"]) * it["qty"] for it in goods), Decimal(0))
    freight = sum(40 * it["qty"] for it in goods if it["weight_kg"] > 20)
    if country == "US":
        standard = Decimal("5.99")
        if weight > 2:
            standard += Decimal("1.50") * math.ceil(weight - 2)
        if merch >= 75 or coupon == "FREESHIP":
            standard = Decimal(0)
        d = date.fromisoformat(cart["date"])
        if d.month == 12 and 15 <= d.day <= 24:
            standard = max(standard, Decimal("9.99"))
    else:
        standard = Decimal(14) + 2 * math.ceil(weight)
    shipping = _cents(standard + freight)

    base = merch if country == "CA" else merch + shipping
    tax = _cents(base * TAX[country])
    subtotal = _cents(subtotal)
    total = subtotal - discount + shipping + tax
    return {k: float(v) for k, v in
            {"subtotal": subtotal, "discount": discount, "shipping": shipping, "tax": tax, "total": total}.items()}
