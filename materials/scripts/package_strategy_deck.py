"""Recompute slide evidence and package the 8-page PDF and separate AI disclosure."""
from pathlib import Path
import json
import pandas as pd
import pymupdf as fitz

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'presentation'
BUILD = ROOT / '.local' / 'deck-build'
EVIDENCE = ROOT / 'materials' / 'presentation'
EVIDENCE.mkdir(parents=True, exist_ok=True)

d = pd.read_excel(ROOT / 'sources/dataset.xlsx', sheet_name='Бизнесы')
g = d[d.iloc[:, 2].isin(['товарное', 'товарное и услужное'])]
w = (g.iloc[:, 16] > 0) & (g.iloc[:, 17] == 1) & (g.iloc[:, 14] > 0) & (g.iloc[:, 22] == 0)
traffic = pd.read_excel(ROOT / 'sources/dataset.xlsx', sheet_name='Маркет Вконтакте — источники')
traffic.iloc[:, 0] = traffic.iloc[:, 0].str.strip()
market = traffic.set_index(traffic.columns[0]).iloc[:, 0].dropna()
evidence = {
    'source': 'sources/dataset.xlsx', 'synthetic': True,
    'goods_communities': len(g), 'checkout_enabled': int(g.iloc[:, 17].eq(1).sum()),
    'selling_in_month': int(g.iloc[:, 22].gt(0).sum()),
    'warm_zero_orders': int(w.sum()), 'warm_at_least_10_opens': int((w & g.iloc[:, 14].ge(10)).sum()),
    'checkout_pct': float(g.iloc[:, 17].eq(1).mean() * 100),
    'selling_pct': float(g.iloc[:, 22].gt(0).mean() * 100),
    'market_total_opens': int(market.sum()),
    'traffic': {str(k): {'opens': int(v), 'share_pct': float(v / market.sum() * 100)} for k, v in market.items()},
    'economics_assumptions': {'aov_rub': 2000, 'seller_gross_margin': .35, 'seller_receipt_cost_rub': 100,
        'fee': .03, 'acquiring': .01, 'variable_cost_per_paid_order_rub': 10,
        'development_rub': 2400000, 'monthly_fixed_rub': 150000, 'payback_months_after_scale': 12},
    'monthly_extra_order_threshold': {str(q): (2400000/12+150000)/(30*q) for q in [.25, .5, .75]},
}
assert [evidence[k] for k in ['goods_communities', 'checkout_enabled', 'selling_in_month', 'warm_zero_orders', 'warm_at_least_10_opens']] == [4158, 3826, 285, 233, 39]
assert evidence['market_total_opens'] == 193512461
(EVIDENCE / 'evidence.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding='utf8')

pdf = fitz.open()
for i in range(1, 9):
    page = pdf.new_page(width=960, height=540)
    page.insert_image(page.rect, filename=str(BUILD / f'slide-{i}.png'))
pdf.set_metadata({'title': 'Теневое Правительство — VK Заказ рядом', 'author': 'Теневое Правительство', 'subject': 'VK Case Champ 2026, Москва; 8 слайдов'})
pdf.save(OUT / 'Теневое Правительство_strategy_msk.pdf', deflate=True)
pdf.close()

disclosure = """# Раскрытие использования ИИ

Команда: Теневое Правительство. Город: Москва. Дата подготовки: 17 ноября 2026.

Инструменты: Claude использовался на предыдущем этапе исследования и разработки ноутбуков; Whisper large-v3 — для автоматической расшифровки Q&A; ChatGPT / Codex и редактор Artifact Tool — для развития концепции, расчётов и редактируемой презентации.

Задачи: анализ брифа и синтетического датасета, поиск и систематизация примеров социальной коммерции, выделение ответов организаторов, разработка продуктовой гипотезы, финансовых сценариев и плана проверки, создание текстов, графиков и интерфейсных макетов.

Входные материалы: бриф, dataset.xlsx, ноутбуки и исследовательские материалы репозитория, запись Q&A и её автоматическая расшифровка. Имя команды, город и участники предоставлены участником команды.

Проверки: показатели слайдов повторно рассчитаны по исходному XLSX; результаты, допущения и гипотезы разделены. Источники и таймкоды указаны в заметках к слайдам. Проведена визуальная проверка восьми слайдов. Интервью, пилот и A/B-тест ещё не проводились.

Ограничения: макеты показывают предлагаемую концепцию, а не действующие экраны VK. Расходы и монетизация — сценарные допущения. Перенос зарубежных показателей на VK не выполнялся. Автоматическая расшифровка может содержать ошибки. Команде предстоит согласовать финальные выводы и допущения перед подачей.

Типы запросов к ИИ: проанализировать материалы; уточнить значение метрик по Q&A; сравнить пути решения; разработать концепцию заказа; рассчитать пороги экономики; подготовить восемь редактируемых слайдов по структуре брифа.
"""
(EVIDENCE / 'ai_disclosure.md').write_text(disclosure, encoding='utf8')
ap = fitz.open()
page = ap.new_page(width=595, height=842)
page.insert_font(fontname='Arial', fontfile='C:/Windows/Fonts/arial.ttf')
page.insert_font(fontname='ArialBold', fontfile='C:/Windows/Fonts/arialbd.ttf')
page.draw_rect(fitz.Rect(0,0,595,12), fill=(0, .467, 1), color=None)
page.insert_text((42, 61), 'Раскрытие использования ИИ', fontname='ArialBold', fontsize=23, color=(.08,.14,.22))
body = disclosure.split('\n\n',1)[1]
remaining = page.insert_textbox(fitz.Rect(42,91,553,788), body, fontname='Arial', fontsize=11.5, lineheight=1.35, color=(.08,.14,.22))
assert remaining >= 0, f'AI disclosure overflow: {remaining}'
page.insert_text((42,815), 'Отдельное приложение. Не входит в 8 слайдов решения.', fontname='Arial', fontsize=9, color=(.4,.46,.55))
ap.save(OUT / 'Теневое Правительство_AI_disclosure.pdf', deflate=True)
ap.close()
print(json.dumps({'slides':8, 'goods':len(g), 'warm':int(w.sum()), 'files':[f.name for f in OUT.glob('*.pdf')]}, ensure_ascii=False))
