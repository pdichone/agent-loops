"""The tests the loop can see. Expected values come from reference/quote.py."""

import pytest

from quote import quote


CASES = [
    ('one_mug_us',
     {'items': [{'sku': 'MG-02', 'price': 24.0, 'qty': 1, 'weight_kg': 0.4, 'category': 'mugs'}], 'country': 'US', 'date': '2026-11-04'},
     {'subtotal': 24.0, 'discount': 0.0, 'shipping': 5.99, 'tax': 2.4, 'total': 32.39}),
    ('two_mugs_qty',
     {'items': [{'sku': 'MG-02', 'price': 24.0, 'qty': 2, 'weight_kg': 0.4, 'category': 'mugs'}], 'country': 'US', 'date': '2026-11-04'},
     {'subtotal': 48.0, 'discount': 0.0, 'shipping': 5.99, 'tax': 4.32, 'total': 58.31}),
    ('kettle10_on_kettle',
     {'items': [{'sku': 'KT-01', 'price': 89.0, 'qty': 1, 'weight_kg': 1.4, 'category': 'kettles'}], 'country': 'US', 'date': '2026-11-04', 'coupon': 'KETTLE10'},
     {'subtotal': 89.0, 'discount': 8.9, 'shipping': 0.0, 'tax': 6.41, 'total': 86.51}),
    ('kettle10_only_kettles',
     {'items': [{'sku': 'KT-01', 'price': 89.0, 'qty': 1, 'weight_kg': 1.4, 'category': 'kettles'}, {'sku': 'MG-02', 'price': 24.0, 'qty': 1, 'weight_kg': 0.4, 'category': 'mugs'}], 'country': 'US', 'date': '2026-11-04', 'coupon': 'KETTLE10'},
     {'subtotal': 113.0, 'discount': 8.9, 'shipping': 0.0, 'tax': 8.33, 'total': 112.43}),
    ('coupon_case_and_spaces',
     {'items': [{'sku': 'MG-02', 'price': 24.0, 'qty': 2, 'weight_kg': 0.4, 'category': 'mugs'}], 'country': 'US', 'date': '2026-11-04', 'coupon': '  save15 '},
     {'subtotal': 48.0, 'discount': 0.0, 'shipping': 5.99, 'tax': 4.32, 'total': 58.31}),
    ('save15_over_100',
     {'items': [{'sku': 'KT-01', 'price': 89.0, 'qty': 1, 'weight_kg': 1.4, 'category': 'kettles'}, {'sku': 'MG-02', 'price': 24.0, 'qty': 1, 'weight_kg': 0.4, 'category': 'mugs'}], 'country': 'US', 'date': '2026-11-04', 'coupon': 'SAVE15'},
     {'subtotal': 113.0, 'discount': 15.0, 'shipping': 0.0, 'tax': 7.84, 'total': 105.84}),
    ('save15_under_100_noop',
     {'items': [{'sku': 'MG-02', 'price': 24.0, 'qty': 3, 'weight_kg': 0.4, 'category': 'mugs'}], 'country': 'US', 'date': '2026-11-04', 'coupon': 'SAVE15'},
     {'subtotal': 72.0, 'discount': 0.0, 'shipping': 5.99, 'tax': 6.24, 'total': 84.23}),
    ('member_5pct',
     {'items': [{'sku': 'MG-02', 'price': 24.0, 'qty': 1, 'weight_kg': 0.4, 'category': 'mugs'}], 'country': 'US', 'date': '2026-11-04', 'member': True},
     {'subtotal': 24.0, 'discount': 1.2, 'shipping': 5.99, 'tax': 2.3, 'total': 31.09}),
    ('member_after_coupon',
     {'items': [{'sku': 'KT-01', 'price': 89.0, 'qty': 1, 'weight_kg': 1.4, 'category': 'kettles'}, {'sku': 'PN-04', 'price': 42.5, 'qty': 1, 'weight_kg': 2.3, 'category': 'pans'}], 'country': 'US', 'date': '2026-11-04', 'coupon': 'SAVE15', 'member': True},
     {'subtotal': 131.5, 'discount': 20.83, 'shipping': 0.0, 'tax': 8.85, 'total': 119.52}),
    ('free_shipping_75',
     {'items': [{'sku': 'KT-01', 'price': 89.0, 'qty': 1, 'weight_kg': 1.4, 'category': 'kettles'}], 'country': 'US', 'date': '2026-11-04'},
     {'subtotal': 89.0, 'discount': 0.0, 'shipping': 0.0, 'tax': 7.12, 'total': 96.12}),
    ('us_weight_over_2kg',
     {'items': [{'sku': 'PN-04', 'price': 12.0, 'qty': 2, 'weight_kg': 2.3, 'category': 'pans'}], 'country': 'US', 'date': '2026-11-04'},
     {'subtotal': 24.0, 'discount': 0.0, 'shipping': 10.49, 'tax': 2.76, 'total': 37.25}),
    ('freeship_coupon_us',
     {'items': [{'sku': 'MG-02', 'price': 24.0, 'qty': 1, 'weight_kg': 0.4, 'category': 'mugs'}], 'country': 'US', 'date': '2026-11-04', 'coupon': 'FREESHIP'},
     {'subtotal': 24.0, 'discount': 0.0, 'shipping': 0.0, 'tax': 1.92, 'total': 25.92}),
    ('freeship_coupon_ca_noop',
     {'items': [{'sku': 'MG-02', 'price': 24.0, 'qty': 1, 'weight_kg': 0.4, 'category': 'mugs'}], 'country': 'CA', 'date': '2026-11-04', 'coupon': 'FREESHIP'},
     {'subtotal': 24.0, 'discount': 0.0, 'shipping': 16.0, 'tax': 3.12, 'total': 43.12}),
    ('ca_shipping_and_tax',
     {'items': [{'sku': 'PN-04', 'price': 42.5, 'qty': 1, 'weight_kg': 2.3, 'category': 'pans'}], 'country': 'CA', 'date': '2026-11-04'},
     {'subtotal': 42.5, 'discount': 0.0, 'shipping': 20.0, 'tax': 5.53, 'total': 68.03}),
    ('mx_tax_includes_shipping',
     {'items': [{'sku': 'MG-02', 'price': 24.0, 'qty': 2, 'weight_kg': 0.4, 'category': 'mugs'}], 'country': 'MX', 'date': '2026-11-04'},
     {'subtotal': 48.0, 'discount': 0.0, 'shipping': 16.0, 'tax': 10.24, 'total': 74.24}),
    ('gift_card_untaxed',
     {'items': [{'sku': 'GC-50', 'price': 50.0, 'qty': 1, 'weight_kg': 0.0, 'category': 'gift_card'}, {'sku': 'MG-02', 'price': 24.0, 'qty': 1, 'weight_kg': 0.4, 'category': 'mugs'}], 'country': 'US', 'date': '2026-11-04'},
     {'subtotal': 74.0, 'discount': 0.0, 'shipping': 5.99, 'tax': 2.4, 'total': 82.39}),
    ('gift_card_member',
     {'items': [{'sku': 'GC-50', 'price': 50.0, 'qty': 1, 'weight_kg': 0.0, 'category': 'gift_card'}, {'sku': 'MG-02', 'price': 24.0, 'qty': 1, 'weight_kg': 0.4, 'category': 'mugs'}], 'country': 'US', 'date': '2026-11-04', 'member': True},
     {'subtotal': 74.0, 'discount': 1.2, 'shipping': 5.99, 'tax': 2.3, 'total': 81.09}),
    ('freight_per_unit',
     {'items': [{'sku': 'ST-09', 'price': 310.0, 'qty': 2, 'weight_kg': 24.0, 'category': 'stoves'}], 'country': 'US', 'date': '2026-11-04'},
     {'subtotal': 620.0, 'discount': 0.0, 'shipping': 80.0, 'tax': 56.0, 'total': 756.0}),
    ('holiday_cutoff_min',
     {'items': [{'sku': 'KT-01', 'price': 89.0, 'qty': 1, 'weight_kg': 1.4, 'category': 'kettles'}], 'country': 'US', 'date': '2026-12-20'},
     {'subtotal': 89.0, 'discount': 0.0, 'shipping': 9.99, 'tax': 7.92, 'total': 106.91}),
]

ERRORS = [
    ('empty_cart', {'items': [], 'country': 'US', 'date': '2026-11-04'}),
    ('zero_qty', {'items': [{'sku': 'MG-02', 'price': 24.0, 'qty': 0, 'weight_kg': 0.4, 'category': 'mugs'}], 'country': 'US', 'date': '2026-11-04'}),
    ('unknown_coupon', {'items': [{'sku': 'MG-02', 'price': 24.0, 'qty': 1, 'weight_kg': 0.4, 'category': 'mugs'}], 'country': 'US', 'date': '2026-11-04', 'coupon': 'BOGUS'}),
    ('unsupported_country', {'items': [{'sku': 'MG-02', 'price': 24.0, 'qty': 1, 'weight_kg': 0.4, 'category': 'mugs'}], 'country': 'FR', 'date': '2026-11-04'}),
]


@pytest.mark.parametrize("name,cart,expected", CASES, ids=[c[0] for c in CASES])
def test_quote(name, cart, expected):
    assert quote(cart) == expected, f"cart={cart}"


@pytest.mark.parametrize("name,cart", ERRORS, ids=[e[0] for e in ERRORS])
def test_rejects(name, cart):
    with pytest.raises(ValueError):
        quote(cart)
