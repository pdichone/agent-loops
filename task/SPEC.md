# Kettleworks checkout quote

Write `quote.py` with one function:

```python
def quote(cart: dict) -> dict: ...
```

## Input

```python
{
    "items": [{"sku": "KT-01", "price": 89.0, "qty": 1, "weight_kg": 1.4, "category": "kettles"}, ...],
    "country": "US",          # "US", "CA" or "MX"
    "coupon": "kettle10",     # optional, may be missing or None
    "member": False,          # optional, default False
    "date": "2026-11-04",     # order date, ISO format
}
```

## Output

```python
{"subtotal": 89.0, "discount": 8.9, "shipping": 0.0, "tax": 6.41, "total": 86.51}
```

Every value is in dollars, rounded to cents with ROUND_HALF_UP (use `decimal`).
`total` is the sum of the rounded parts: `subtotal - discount + shipping + tax`.

## Rules

This spec is not complete. Like every real spec, some business rules never got written down.
The test suite is the source of truth.

1. **Validation.** Raise `ValueError` if `items` is empty, if any `qty` is not an `int` of at least 1,
   or if any `price` is negative.
2. **Subtotal** is the sum of `price * qty` over all items.
3. **Coupons.** Codes are case-insensitive and ignore surrounding spaces. An unknown code raises `ValueError`.
   - `KETTLE10`: 10% off items in category `kettles`.
   - `SAVE15`: $15 off, only if the subtotal is at least $100. Below that it does nothing (no error).
   - `FREESHIP`: shipping is free. US only; in other countries it does nothing.
4. **Members** get 5% off the subtotal *after* the coupon.
5. `discount` is the coupon discount plus the member discount. It never makes merchandise negative.
   Discounted merchandise = subtotal - discount.
6. **Shipping, US.** $5.99 for up to 2 kg total weight, plus $1.50 for each additional kg or part of a kg.
   Free when discounted merchandise is $75 or more.
7. **Shipping, CA and MX.** $14.00 plus $2.00 per kg of total weight, rounded up to whole kg. Never free.
   Any other country raises `ValueError`.
8. **Tax.** US 8% of (discounted merchandise + shipping). CA 13% of discounted merchandise only.
   MX 16% of (discounted merchandise + shipping).
   Compute tax from the already-rounded discount and shipping.
9. Weight for shipping is `weight_kg * qty` summed over all items.
10. **Gift cards** (`category == "gift_card"`) never count toward any threshold: not the $75 free shipping, not SAVE15's $100.
