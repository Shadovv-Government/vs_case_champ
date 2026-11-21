"""Calculate the evidence pictured on the slides from the original workbook."""
import json
from math import ceil
from pathlib import Path
from statistics import NormalDist

import pandas as pd

HERE = Path(__file__).resolve().parent
WORKBOOK = HERE.parents[1] / 'sources/dataset.xlsx'
d = pd.read_excel(WORKBOOK, sheet_name='Бизнесы')
d = d[d['Тип бизнеса (товары / услуги)'].isin(['товарное', 'товарное и услужное'])]
assert d['ID бизнеса'].is_unique
posts = (d['Посты с товаром за 30 дней'] > 0) | (d['Клипы с товаром за 30 дней'] > 0)
views = d['Просмотры обычного контента'] > 0
opened = d['Открытия карточки товара из контента']
active = d['Число активных товаров в каталоге']
checkout = d['Подключён чекаут']
orders = d['Заказы через чекаут']
ready = (active > 0) & (checkout == 1)
quiet = ready & (orders == 0) & (opened == 0)
warm = ready & (orders == 0) & (opened > 0)
high_openings = warm & (opened >= 10)
states = (
    active == 0, (active > 0) & (checkout == 0), ready & (opened == 0),
    ready & opened.between(1, 9), ready & (opened >= 10),
)
observed = {
    'goods': len(d),
    'checkout': int(checkout.sum()),
    'sellers_with_orders': int((orders > 0).sum()),
    'all_orders': int(orders.sum()),
    'top_10_orders': int(orders.nlargest(10).sum()),
    'groups': [int(state.sum()) for state in states],
    'groups_without_orders': [int((state & (orders == 0)).sum()) for state in states],
    'quiet': int(quiet.sum()),
    'quiet_with_normal_views': int((quiet & views).sum()),
    'quiet_with_product_posts': int((quiet & posts).sum()),
    'quiet_with_normal_views_without_product_posts': int((quiet & views & ~posts).sum()),
    'warm': int(warm.sum()),
    'warm_under_10': int((warm & (opened < 10)).sum()),
    'warm_at_least_10': int(high_openings.sum()),
    'warm_high_opening_share': float(opened[high_openings].sum() / opened[warm].sum()),
    'without_checkout_active_openings': int(((active > 0) & (checkout == 0) & (opened > 0)).sum()),
    'no_content_openings_with_orders': int((ready & (opened == 0) & (orders > 0)).sum()),
}
assert sum(observed['groups']) == observed['goods']
assert observed['warm_under_10'] + observed['warm_at_least_10'] == observed['warm']

traffic = pd.read_excel(WORKBOOK, sheet_name='Маркет Вконтакте — источники')
traffic = traffic.set_index('Источник')['Маркет Вконтакте'].dropna().astype(int).to_dict()
market = [
    traffic['Витрина магазина'], traffic['Лента'] + traffic['Клипы'],
    traffic['Главная Маркета Вконтакте'], traffic['Поиск'] + traffic['Другое'],
]
totals = pd.read_excel(WORKBOOK, sheet_name='Маркет Вконтакте — итоги').set_index('Метрика')
categories = pd.read_excel(WORKBOOK, sheet_name='Маркет Вконтакте — категории')
assert sum(market) == totals.loc['Открытия карточки товара', 'Маркет Вконтакте']
market_pct = [round(100 * value / sum(market), 1) for value in market]
market_totals = {
    'opens': sum(market),
    'search_pct': round(100 * traffic['Поиск'] / sum(market), 1),
    'other_pct': round(100 * traffic['Другое'] / sum(market), 1),
    'orders': int(totals.loc['Оформленные заказы', 'Маркет Вконтакте']),
    'category_orders': int(categories['Заказы: Маркет Вконтакте'].sum()),
    'paid_in_vk': int(totals.loc['Оплаченные заказы', 'Маркет Вконтакте']),
    'partner_orders': int(totals.loc['Оформленные заказы', 'Партнёр 1']),
    'partner_direct_clicks': int(totals.loc[
        'Прямые переходы к Партнёру 1 (без открытия карточки)', 'Партнёр 1'
    ]),
}

control_p, control_m = .15, 2
scenarios = [
    {'label': label, 'p': p, 'm': m,
     'seller_lift': round(1000 * (p - control_p)),
     'order_lift': round(1000 * (p * m - control_p * control_m))}
    for label, p, m in [('Осторожный', .18, 2), ('Средний', .22, 2.1), ('Сильный', .25, 2.2)]
]
post_scenarios = [
    {
        'label': label, 'publisher_rate_lift': lift, 'orders_per_additional_publisher': orders,
        'publisher_lift': round(1_000 * lift),
        'order_lift': round(1_000 * lift * orders),
    }
    for label, lift, orders in (
        ('Осторожный', .05, .2), ('Средний', .10, .4), ('Сильный', .15, .6),
    )
]
connection = {
    'reference_communities': 100, 'checkout_rate_lift': .10,
    'order_share_among_incremental_connections': .20,
}
connection['additional_connected'] = round(connection['reference_communities'] * connection['checkout_rate_lift'])
connection['additional_with_order'] = round(
    connection['additional_connected'] * connection['order_share_among_incremental_connections']
)
model = {
    'development_rub': 2_400_000,
    'monthly_support_rub': 150_000,
    'active_months': 10,
    'aov_rub': 2_000,
    'seller_gross_margin': .35,
    'seller_handling_rub': 100,
    'fee_rate': .03,
    'acquiring_rate': .01,
    'paid_order_cost_rub': 10,
    'fulfillment': .80,
    'paid_service_share': .50,
    'booked_order_cost_rub': 2,
    'example_monthly_orders': 25_000,
}
fee = model['aov_rub'] * model['fee_rate']
contribution = fee - model['aov_rub'] * model['acquiring_rate'] - model['paid_order_cost_rub']
merchant_contribution = model['aov_rub'] * model['seller_gross_margin'] - model['seller_handling_rub']
year_cost = model['development_rub'] + model['monthly_support_rub'] * 12
months = model['active_months']
model['net_per_paid_order'] = contribution
model['seller_contribution'] = merchant_contribution
model['seller_contribution_with_service'] = merchant_contribution - fee
model['year_cost'] = year_cost
model['example_year_gross_fee'] = round(
    model['example_monthly_orders'] * months * model['fulfillment'] * model['paid_service_share'] * fee
)
model['sensitivity'] = []
for paid_share in sorted({.10, .25, model['paid_service_share'], .75}):
    net = round(model['fulfillment'] * paid_share * contribution - model['booked_order_cost_rub'], 2)
    model['sensitivity'].append({
        'paid_service_share': paid_share,
        'net_per_order': net,
        'breakeven_monthly_orders': ceil(year_cost / months / net) if net > 0 else None,
        'example_year_result': model['example_monthly_orders'] * months * net - year_cost,
    })
base_model = next(s for s in model['sensitivity'] if s['paid_service_share'] == model['paid_service_share'])
for field in ('net_per_order', 'breakeven_monthly_orders', 'example_year_result'):
    model[field] = base_model[field]
threshold = model['breakeven_monthly_orders']
model['monthly_eligible_reach'] = [
    {'label': s['label'], 'communities': ceil(threshold * 1_000 / s['order_lift'])}
    for s in scenarios[1:] if threshold is not None and s['order_lift'] > 0
]

pilot = {
    'budget_rub': {'research': 75_000, 'prototype': 150_000, 'events_and_qa': 75_000},
    'observation_days': 28,
    'followup_days': 28,
    'orders_per_1000_gate': 100,
    'post_orders_per_1000_gate': 40,
    'cancel_margin_pp': 2,
    'complaint_margin_pp': .5,
    'alpha': .05,
    'power': .80,
    'reserve': .10,
}
pilot['budget_total_rub'] = sum(pilot['budget_rub'].values())
normal = NormalDist()
z = normal.inv_cdf(1 - pilot['alpha'] / 2) + normal.inv_cdf(pilot['power'])
lift = pilot['orders_per_1000_gate'] / 1_000
post_lift = pilot['post_orders_per_1000_gate'] / 1_000
reserve_factor = 1 - pilot['reserve']
pilot['sample_size'] = [
    {'variance': variance, 'per_arm_with_reserve': ceil(
        2 * z**2 * variance / lift**2 / reserve_factor
    ), 'post_per_arm_with_reserve': ceil(2 * z**2 * variance / post_lift**2 / reserve_factor)}
    for variance in (.5, 1., 2.)
]
z_quality = normal.inv_cdf(1 - pilot['alpha']) + normal.inv_cdf(pilot['power'])
pilot['quality_sample'] = [
    {'metric': name, 'event_rate': rate, 'margin_pp': margin, 'orders_per_arm_with_reserve': ceil(
        2 * z_quality**2 * rate * (1 - rate) / (margin / 100)**2 / reserve_factor
    )}
    for name, rate, margin in (
        ('Отмены', .10, pilot['cancel_margin_pp']), ('Жалобы', .01, pilot['complaint_margin_pp']),
    )
]

(HERE / 'evidence.json').write_text(json.dumps({
    'source': 'sources/dataset.xlsx',
    'observed': observed,
    'market_pct': market_pct,
    'market_totals': market_totals,
    'control': {'share_with_orders': control_p, 'orders_per_selling_community': control_m},
    'scenarios': scenarios,
    'post_scenarios': post_scenarios,
    'connection': connection,
    'model': model,
    'pilot': pilot,
}, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
