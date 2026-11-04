"""Held-out tests. The loop never sees these: they check the code works, not that it passes test_visible.py."""

import pytest

from quote import quote


CASES = [
    ('h_kettle10_member_mix',
     {'items': [{'sku': 'KT-01', 'price': 89.0, 'qty': 2, 'weight_kg': 1.4, 'category': 'kettles'}, {'sku': 'MG-02', 'price': 24.0, 'qty': 3, 'weight_kg': 0.4, 'category': 'mugs'}], 'country': 'US', 'date': '2026-11-04', 'coupon': 'Kettle10', 'member': True},
     {'subtotal': 250.0, 'discount': 29.41, 'shipping': 0.0, 'tax': 17.65, 'total': 238.24}),
    ('h_gift_card_not_threshold',
     {'items': [{'sku': 'GC-50', 'price': 100.0, 'qty': 1, 'weight_kg': 0.0, 'category': 'gift_card'}, {'sku': 'MG-02', 'price': 24.0, 'qty': 1, 'weight_kg': 0.4, 'category': 'mugs'}], 'country': 'US', 'date': '2026-11-04'},
     {'subtotal': 124.0, 'discount': 0.0, 'shipping': 5.99, 'tax': 2.4, 'total': 132.39}),
    ('h_gift_card_not_discounted',
     {'items': [{'sku': 'GC-50', 'price': 200.0, 'qty': 1, 'weight_kg': 0.0, 'category': 'gift_card'}, {'sku': 'MG-02', 'price': 24.0, 'qty': 1, 'weight_kg': 0.4, 'category': 'mugs'}], 'country': 'US', 'date': '2026-11-04', 'coupon': 'SAVE15'},
     {'subtotal': 224.0, 'discount': 0.0, 'shipping': 5.99, 'tax': 2.4, 'total': 232.39}),
    ('h_us_partial_kg',
     {'items': [{'sku': 'PN-04', 'price': 42.5, 'qty': 1, 'weight_kg': 1.1, 'category': 'pans'}, {'sku': 'MG-02', 'price': 24.0, 'qty': 1, 'weight_kg': 1.0, 'category': 'mugs'}], 'country': 'US', 'date': '2026-11-04'},
     {'subtotal': 66.5, 'discount': 0.0, 'shipping': 7.49, 'tax': 5.92, 'total': 79.91}),
    ('h_freight_not_waived_freeship',
     {'items': [{'sku': 'ST-09', 'price': 310.0, 'qty': 1, 'weight_kg': 21.0, 'category': 'stoves'}], 'country': 'US', 'date': '2026-11-04', 'coupon': 'freeship'},
     {'subtotal': 310.0, 'discount': 0.0, 'shipping': 40.0, 'tax': 28.0, 'total': 378.0}),
    ('h_freight_plus_holiday',
     {'items': [{'sku': 'ST-09', 'price': 60.0, 'qty': 1, 'weight_kg': 22.5, 'category': 'stoves'}, {'sku': 'MG-02', 'price': 24.0, 'qty': 1, 'weight_kg': 0.4, 'category': 'mugs'}], 'country': 'US', 'date': '2027-12-24'},
     {'subtotal': 84.0, 'discount': 0.0, 'shipping': 49.99, 'tax': 10.72, 'total': 144.71}),
    ('h_holiday_edges',
     {'items': [{'sku': 'MG-02', 'price': 24.0, 'qty': 1, 'weight_kg': 0.4, 'category': 'mugs'}], 'country': 'US', 'date': '2026-12-14'},
     {'subtotal': 24.0, 'discount': 0.0, 'shipping': 5.99, 'tax': 2.4, 'total': 32.39}),
    ('h_holiday_last_day',
     {'items': [{'sku': 'MG-02', 'price': 24.0, 'qty': 1, 'weight_kg': 0.4, 'category': 'mugs'}], 'country': 'US', 'date': '2026-12-24'},
     {'subtotal': 24.0, 'discount': 0.0, 'shipping': 9.99, 'tax': 2.72, 'total': 36.71}),
    ('h_ca_rounds_up_kg',
     {'items': [{'sku': 'MG-02', 'price': 24.0, 'qty': 1, 'weight_kg': 0.3, 'category': 'mugs'}, {'sku': 'MG-02', 'price': 24.0, 'qty': 1, 'weight_kg': 0.3, 'category': 'mugs'}], 'country': 'CA', 'date': '2026-11-04'},
     {'subtotal': 48.0, 'discount': 0.0, 'shipping': 16.0, 'tax': 6.24, 'total': 70.24}),
    ('h_mx_member',
     {'items': [{'sku': 'PN-04', 'price': 42.5, 'qty': 3, 'weight_kg': 2.3, 'category': 'pans'}], 'country': 'MX', 'date': '2026-11-04', 'member': True},
     {'subtotal': 127.5, 'discount': 6.38, 'shipping': 28.0, 'tax': 23.86, 'total': 172.98}),
    ('h_only_gift_cards_ca',
     {'items': [{'sku': 'GC-50', 'price': 50.0, 'qty': 1, 'weight_kg': 0.0, 'category': 'gift_card'}], 'country': 'CA', 'date': '2026-11-04'},
     {'subtotal': 50.0, 'discount': 0.0, 'shipping': 14.0, 'tax': 0.0, 'total': 64.0}),
    ('h_rounding_half_up',
     {'items': [{'sku': 'MG-02', 'price': 10.125, 'qty': 1, 'weight_kg': 0.1, 'category': 'mugs'}], 'country': 'US', 'date': '2026-11-04'},
     {'subtotal': 10.13, 'discount': 0.0, 'shipping': 5.99, 'tax': 1.29, 'total': 17.41}),
    ('h_heavy_pan_freight',
     {'items': [{'sku': 'PN-04', 'price': 150.0, 'qty': 1, 'weight_kg': 25.0, 'category': 'pans'}], 'country': 'US', 'date': '2026-11-04'},
     {'subtotal': 150.0, 'discount': 0.0, 'shipping': 40.0, 'tax': 15.2, 'total': 205.2}),
    ('h_light_stove_no_freight',
     {'items': [{'sku': 'ST-09', 'price': 310.0, 'qty': 1, 'weight_kg': 15.0, 'category': 'stoves'}], 'country': 'CA', 'date': '2026-11-04'},
     {'subtotal': 310.0, 'discount': 0.0, 'shipping': 44.0, 'tax': 40.3, 'total': 394.3}),
]

ERRORS = [
    ('h_float_qty', {'items': [{'sku': 'MG-02', 'price': 24.0, 'qty': 1.5, 'weight_kg': 0.4, 'category': 'mugs'}], 'country': 'US', 'date': '2026-11-04'}),
    ('h_negative_price', {'items': [{'sku': 'MG-02', 'price': -1.0, 'qty': 1, 'weight_kg': 0.4, 'category': 'mugs'}], 'country': 'US', 'date': '2026-11-04'}),
    ('h_country_lowercase', {'items': [{'sku': 'MG-02', 'price': 24.0, 'qty': 1, 'weight_kg': 0.4, 'category': 'mugs'}], 'country': 'us', 'date': '2026-11-04'}),
]


@pytest.mark.parametrize("name,cart,expected", CASES, ids=[c[0] for c in CASES])
def test_quote(name, cart, expected):
    got = quote(cart)
    assert got == expected, f"cart={cart} got={got} expected={expected}"


@pytest.mark.parametrize("name,cart", ERRORS, ids=[e[0] for e in ERRORS])
def test_rejects(name, cart):
    with pytest.raises(ValueError):
        quote(cart)
