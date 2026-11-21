"""Calculate the evidence pictured on the slides from the original workbook."""
import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
WORKBOOK = HERE.parents[1] / 'sources/dataset.xlsx'
d = pd.read_excel(WORKBOOK, sheet_name='Бизнесы')
d = d[d.iloc[:, 2].isin(['товарное', 'товарное и услужное'])]
posts = (d.iloc[:, 6] > 0) | (d.iloc[:, 7] > 0)
opened, active, checkout, orders = (d.iloc[:, i] for i in [14, 16, 17, 22])
ready = (active > 0) & (checkout == 1)
quiet = ready & (orders == 0) & (opened == 0)
warm = ready & (orders == 0) & (opened > 0)
observed = {
    'goods': len(d),
    'checkout': int(checkout.sum()),
    'sellers_with_orders': int((orders > 0).sum()),
    'all_orders': int(orders.sum()),
    'top_10_orders': int(orders.nlargest(10).sum()),
    'groups': [
        int((active == 0).sum()),
        int(((active > 0) & (checkout == 0)).sum()),
        int((ready & (opened == 0)).sum()),
        int((ready & opened.between(1, 9)).sum()),
        int((ready & (opened >= 10)).sum()),
    ],
    'quiet': int(quiet.sum()),
    'quiet_with_normal_views': int((quiet & (d.iloc[:, 8] > 0)).sum()),
    'quiet_with_product_posts': int((quiet & posts).sum()),
    'warm': int(warm.sum()),
    'warm_under_10': int((warm & (opened < 10)).sum()),
    'warm_at_least_10': int((warm & (opened >= 10)).sum()),
    'no_content_openings_with_orders': int((ready & (opened == 0) & (orders > 0)).sum()),
}
assert sum(observed['groups']) == observed['goods']
assert observed['warm_under_10'] + observed['warm_at_least_10'] == observed['warm']

traffic = pd.read_excel(WORKBOOK, sheet_name='Маркет Вконтакте — источники').iloc[:, 1]
values = traffic.dropna().tolist()
market = [values[1], values[2] + values[3], values[5], values[0] + values[4]]
assert sum(market) == 193_512_461
market_pct = [round(100 * v / sum(market), 1) for v in market]

control_p, control_m = .15, 2
scenarios = [
    {'label': label, 'p': p, 'm': m,
     'seller_lift': round(1000 * (p - control_p)),
     'order_lift': round(1000 * (p * m - control_p * control_m))}
    for label, p, m in [('Осторожный', .18, 2), ('Средний', .22, 2.1), ('Сильный', .25, 2.2)]
]
year_cost = 2_400_000 + 150_000 * 12
net_per_order = .8 * .5 * 30 - 2
monthly_orders = 25_000
model = {
    'year_cost': year_cost,
    'active_months': 10,
    'net_per_order': net_per_order,
    'example_monthly_orders': monthly_orders,
    'breakeven_monthly_orders': int(year_cost / 10 / net_per_order),
    'example_year_result': int(monthly_orders * 10 * net_per_order - year_cost),
}

(HERE / 'evidence.json').write_text(json.dumps({
    'source': 'sources/dataset.xlsx',
    'observed': observed,
    'market_pct': market_pct,
    'scenarios': scenarios,
    'model': model,
}, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
