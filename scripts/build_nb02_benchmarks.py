"""Builds notebooks/02_social_commerce_benchmarks.ipynb (self-contained: data embedded)."""
import nbformat as nbf, sys
from pathlib import Path

REPO = Path(sys.argv[1])
OUT = REPO / "notebooks" / "02_social_commerce_benchmarks.ipynb"
data_dir = REPO / "research" / "data"
EMB = {p.name: p.read_text(encoding="utf-8") for p in sorted(data_dir.glob("*.csv"))}

cells = []
md = lambda s: cells.append(nbf.v4.new_markdown_cell(s.strip("\n")))
code = lambda s: cells.append(nbf.v4.new_code_cell(s.strip("\n")))

md(r"""
# Социальная коммерция в мире: бенчмарки для стратегии VK

**Зачем:** найти, как устроены успешные модели социальной коммерции на других рынках, кто на них продаёт, какие авторы продают лучше и кто покупает, и сравнить это с данными кейса VK. Результат — аргументы для слайдов 4–7 презентации.

**Что внутри:**

| Раздел | Вопрос |
|---|---|
| 1 | Какие модели соцкоммерции существуют и какая из них успешна |
| 2 | Откуда приходит GMV: контент, витрина, эфиры, авторы |
| 3 | Кто продаёт: МСБ, концентрация, проблема «первой продажи» |
| 4 | Какие авторы продают и кому доверяют покупатели |
| 5 | Кто покупает: возраст и пол |
| 6 | Что продаётся: категории |
| 7 | Метрики VK против бенчмарков |
| 8 | Какие модели подходят VK: матрица |
| 9 | Выводы для презентации |

**Данные:** 12 кейсов, 55 показателей, 42 источника. Таблицы лежат в `research/data/*.csv` и встроены в ноутбук, поэтому он запускается в Colab без загрузки файлов.

**Уровни достоверности** у каждого числа:
- `official` — отчётность или пресс-релиз компании;
- `research` — отраслевое исследование (Momentum Works, McKinsey, Accenture, eMarketer, НАФИ);
- `secondary` — пересказ в СМИ без доступа к первоисточнику. На слайдах такие числа идут с пометкой «оценка».

> Цифры с разных платформ измерены по-разному (GMV, заказы, открытия карточек, опросы). Сравниваем **направление и порядок величин**, а не точные значения.
""")

md("## 0. Настройка и данные")
code(r"""
import io, textwrap, warnings
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib.pyplot as plt, matplotlib.ticker as mtick
from matplotlib.colors import LinearSegmentedColormap
warnings.filterwarnings("ignore")
pd.set_option("display.max_colwidth", 120); pd.set_option("display.width", 220)

VK, PARTNER = "#2a78d6", "#eb6834"
CAT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
SEQ = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
INK, INK2, MUTED, GRID, BASE, SURF = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#fcfcfb"
GREY = "#c9c7c0"
plt.rcParams.update({
    "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
    "font.family": "DejaVu Sans", "font.size": 10.5,
    "axes.edgecolor": BASE, "axes.labelcolor": INK2, "axes.titlecolor": INK,
    "axes.titlesize": 11.5, "axes.titleweight": "bold", "axes.titlelocation": "left", "axes.titlepad": 10,
    "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False,
    "axes.grid": True, "axes.grid.axis": "y", "grid.color": GRID, "grid.linewidth": 0.8,
    "axes.axisbelow": True, "xtick.color": MUTED, "ytick.color": INK2,
    "xtick.major.size": 0, "ytick.major.size": 0, "legend.frameon": False, "legend.fontsize": 10,
    "figure.dpi": 110, "savefig.dpi": 200, "lines.linewidth": 2,
})
try:
    get_ipython().run_line_magic("config", "InlineBackend.figure_format = 'retina'")
except Exception:
    pass

SLIDES = Path("../research/slides") if Path("../research").exists() else Path("slides_png")  # PNG для слайдов
SLIDES.mkdir(parents=True, exist_ok=True)

def ru(x, d=0):
    if pd.isna(x): return "—"
    return f"{x:,.{d}f}".replace(",", " ").replace(".", ",")

def finish(fig, title, subtitle=None, note=None, top=0.84, name=None):
    fig.tight_layout(rect=[0, 0.05 if note else 0, 1, top])
    fig.text(0.012, 0.985, title, fontsize=15, fontweight="bold", color=INK, ha="left", va="top")
    if subtitle:
        fig.text(0.012, 0.985 - 0.075 * (6 / fig.get_figheight()), subtitle, fontsize=10.5, color=INK2, ha="left", va="top")
    if note:
        fig.text(0.012, 0.008, note, fontsize=8.5, color=MUTED, ha="left", va="bottom", wrap=True)
    if name:
        fig.savefig(SLIDES / f"{name}.png", bbox_inches="tight")
    plt.show()

def hgrid(ax):
    ax.grid(axis="x", color=GRID, linewidth=0.8); ax.grid(axis="y", visible=False)
    ax.spines["bottom"].set_visible(False); ax.spines["left"].set_visible(True); ax.spines["left"].set_color(BASE)

def hlabels(ax, bars, labels, pad=4, fs=9.5):
    for b, t in zip(bars, labels):
        ax.annotate(t, (b.get_width(), b.get_y() + b.get_height() / 2), xytext=(pad, 0),
                    textcoords="offset points", va="center", ha="left", fontsize=fs, color=INK)
""")

emb_src = "EMBEDDED = {\n" + "".join(f"    {k!r}: {v!r},\n" for k, v in EMB.items()) + "}\n"
code("# Данные исследования (копия research/data/*.csv). Если ноутбук запущен из репозитория — читаются файлы.\n" + emb_src + r"""
def load(name):
    for base in [Path("research/data"), Path("../research/data")]:
        if (base / name).exists():
            return pd.read_csv(base / name)
    return pd.read_csv(io.StringIO(EMBEDDED[name]))

sources = load("sources.csv"); cases = load("cases.csv"); metrics = load("metrics.csv")
demo = load("demographics.csv"); nafi = load("russia_nafi.csv"); creators = load("creators.csv"); cats = load("categories.csv")
SRC = sources.set_index("source_id")

def cite(ids):
    # Короткая подпись источника для графика: «Momentum Works 2026; VK 2026»
    out = []
    for i in str(ids).split(";"):
        r = SRC.loc[i.strip()]
        out.append(f"{r.publisher} ({str(r.published)[:4]})")
    return "; ".join(dict.fromkeys(out))

print(f"Кейсов: {len(cases)}, показателей: {len(metrics)}, демография: {len(demo)}, источников: {len(sources)}")
print(metrics.confidence.value_counts().rename("показатели по уровню достоверности").to_string())
""")

# ---------------------------------------------------------------- 1
md(r"""
## 1. Модели социальной коммерции и их результат

Мы собрали 12 платформ, которые закрывают все основные модели: интерес-коммерцию (Douyin, TikTok Shop), доверительные эфиры (Kuaishou), социальный граф и мессенджер (WeChat), отзывы и кураторов (Xiaohongshu), групповые покупки (Pinduoduo), реселлинг через переписку (Meesho), нишевые live-аукционы (Whatnot), отдельную витрину в соцсети (Instagram/Facebook Shops) и классифайд с чатом (Facebook Marketplace). Отдельной строкой — шопсы VK.
""")
code(r"""
view = cases[["platform", "market", "archetype", "where_buy", "outcome", "best_sellers", "lesson_for_vk", "sources"]].copy()
view["sources"] = view.sources.str.replace(";", ", ")
view.columns = ["Платформа", "Рынок", "Модель", "Где покупка", "Итог", "Кто продаёт лучше", "Урок для VK", "Источники"]
view.style.hide(axis="index").set_properties(**{"text-align": "left", "vertical-align": "top"})
""")

code(r"""
g = cases.dropna(subset=["gmv_usd_bn"]).sort_values("gmv_usd_bn")
fig, ax = plt.subplots(figsize=(12, 4.6))
col = {"Китай": CAT[0], "США": CAT[1], "Юго-Восточная Азия": CAT[2]}
bars = ax.barh(g.platform + "  ·  " + g.year.astype(str), g.gmv_usd_bn, color=[col.get(m, GREY) for m in g.market], height=0.6)
hlabels(ax, bars, [f"${ru(v, 1 if v < 20 else 0)} млрд" + (f"   +{ru(r)}% г/г" if pd.notna(r) else "") for v, r in zip(g.gmv_usd_bn, g.growth_pct)])
ax.set_xscale("log"); ax.set_xlim(1, 3000); hgrid(ax)
ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda v, _: f"${ru(v)} млрд"))
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=c, label=k) for k, c in col.items()], loc="lower right")
finish(fig, "Китайские платформы на порядок крупнее, но быстрее всех растут TikTok Shop и контент-коммерция ЮВА",
       "GMV социальной коммерции по платформам, млрд долларов (логарифмическая шкала); юани пересчитаны по курсу 7,2 юаня за доллар",
       "Источники: " + cite("S01;S03;S06;S07;S22") + ". Douyin — вторичная оценка 36Kr; WeChat, Xiaohongshu, Meesho не раскрывают GMV",
       name="01_gmv_scale")
""")

# ---------------------------------------------------------------- 2
md(r"""
## 2. Откуда приходит GMV: контент, витрина, эфиры

Ключевой вопрос для роли Маркета ВКонтакте: работает ли «витрина» сама по себе. У лидеров GMV делится между контентом (видео, эфиры) и поиском/витриной, но **витрина питается трафиком из контента**, а не живёт отдельно. Instagram попробовал отдельную вкладку магазина и свернул её.
""")
code(r"""
mix = {
    "Douyin, 2024\n(доля GMV)": {"Контент: эфиры авторов": 30, "Контент: эфиры магазинов": 30, "Витрина и поиск": 40},
    "TikTok Shop США, 2025\n(доля GMV)": {"Контент: видео": 50, "Контент: эфиры": 14, "Витрина и поиск": 36},
    "Маркет ВКонтакте, 2026\n(доля открытий карточки)": {"Контент: лента и клипы": 18.6, "Витрина и поиск": 39.1 + 1.9 + 0.2, "Другое (не расшифровано)": 40.2},
}
COLS = {"Контент: эфиры авторов": CAT[0], "Контент: эфиры магазинов": SEQ[4], "Контент: видео": CAT[0], "Контент: эфиры": SEQ[4],
        "Контент: лента и клипы": CAT[0], "Витрина и поиск": CAT[3], "Другое (не расшифровано)": GREY}
fig, ax = plt.subplots(figsize=(12, 4.4))
for i, (row, parts) in enumerate(mix.items()):
    left = 0
    for k, v in parts.items():
        ax.barh(i, v, left=left, color=COLS[k], height=0.58, edgecolor=SURF, linewidth=2)
        ax.text(left + v / 2, i, f"{k.split(': ')[-1]}\n{ru(v, 0)}%", ha="center", va="center", fontsize=9,
                color=INK if COLS[k] in (CAT[3], GREY) else "white", fontweight="bold")
        left += v
ax.set_yticks(range(len(mix)), list(mix)); ax.invert_yaxis(); ax.set_xlim(0, 100); hgrid(ax)
ax.xaxis.set_major_formatter(mtick.PercentFormatter(100))
ax.legend(handles=[Patch(color=CAT[0], label="Контент (видео, лента, эфиры)"), Patch(color=CAT[3], label="Витрина и поиск"), Patch(color=GREY, label="Не расшифровано")],
          ncol=3, loc="lower left", bbox_to_anchor=(0, 1.0))
finish(fig, "У лидеров 60% GMV даёт контент; у Маркета VK — 19% открытий, главная — 0,2%",
       "Структура источников продаж. Douyin и TikTok — доля GMV; Маркет ВКонтакте — доля открытий карточки (другая единица)",
       "Источники: " + cite("S01;S06;S43") + ". Douyin: «полка» >40%, эфиры магазинов >30%, остаток — эфиры авторов (оценка)",
       top=0.78, name="02_gmv_mix")
""")

code(r"""
lessons = pd.DataFrame([
    ["Instagram", "2022–2023", "Свернули live shopping, убрали вкладку Shop из навигации", "Отдельная витрина не собирала трафик; фокус вернули на рекламу и контент", "S18;S19"],
    ["Facebook", "2023–2024", "Магазины без чекаута закрыты; при этом 77,7% покупателей FB покупают на Marketplace и 14,2% — в Shops", "Люди покупают там, где есть локальные объявления и переписка", "S20;S21"],
    ["Douyin", "2024", "Поиск и витрина («полка») выросли до >40% GMV", "Витрина работает как продолжение контента: люди ищут то, что увидели", "S01"],
    ["Маркет ВКонтакте", "2026", "Главная Маркета даёт 0,2% открытий, витрины сообществ — 39%", "Повтор сценария Instagram: точка входа — сообщество и контент", "S43"],
], columns=["Платформа", "Когда", "Что произошло", "Вывод", "Источник"])
lessons.style.hide(axis="index").set_properties(**{"text-align": "left", "vertical-align": "top"})
""")

# ---------------------------------------------------------------- 3
md(r"""
## 3. Кто продаёт: МСБ, концентрация и «первая продажа»

В датасете VK 93% товарных сообществ не получили ни одного заказа за месяц, а топ-10 дают 54% заказов. Это не особенность VK: у TikTok Shop в США больше половины магазинов без продаж, а 1% продавцов делает 60% GMV. Разница в том, **что платформы делают с длинным хвостом**.
""")
code(r"""
fig, axes = plt.subplots(1, 2, figsize=(13, 4.6))
ax = axes[0]
d = pd.DataFrame({"Платформа": ["TikTok Shop США\n(магазины, 2025)", "VK, товарные сообщества\n(датасет, сентябрь 2026)"],
                  "v": [50, 93.1]})
bars = ax.bar(d["Платформа"], d.v, color=[PARTNER, VK], width=0.55)
for b, t in zip(bars, ["> 50%", "93%"]):
    ax.annotate(t, (b.get_x() + b.get_width() / 2, b.get_height()), xytext=(0, 4), textcoords="offset points", ha="center", fontsize=11, fontweight="bold")
ax.set_ylim(0, 110); ax.yaxis.set_major_formatter(mtick.PercentFormatter(100)); ax.set_title("Доля продавцов без продаж")
ax.tick_params(axis="x", colors=INK2)
ax = axes[1]
d = pd.DataFrame({"k": ["TikTok Shop США:\nтоп-1% продавцов", "VK датасет:\nтоп-10 продавцов (3,4%)"], "v": [60, 54]})
bars = ax.bar(d.k, d.v, color=[PARTNER, VK], width=0.55)
for b, t in zip(bars, ["60% GMV", "54% заказов"]):
    ax.annotate(t, (b.get_x() + b.get_width() / 2, b.get_height()), xytext=(0, 4), textcoords="offset points", ha="center", fontsize=11, fontweight="bold")
ax.set_ylim(0, 75); ax.yaxis.set_major_formatter(mtick.PercentFormatter(100)); ax.set_title("Доля продаж у крупнейших продавцов")
ax.tick_params(axis="x", colors=INK2)
finish(fig, "Длинный хвост без продаж есть у всех — лидеры выигрывают тем, что вытаскивают из него новых продавцов",
       "Периоды разные: TikTok — магазины за 2025 год, VK — сообщества за месяц, поэтому у VK доля без продаж выше",
       "Источники: " + cite("S06;S10;S43"), name="03_long_tail")
""")

code(r"""
prog = pd.DataFrame([
    ["Kuaishou", "Программа трафика 100 млрд юаней для новых продавцов; Golden Bounty, Set Sail", "Новые продавцы +30% г/г (Q3 2024)", "S04;S40"],
    ["Xiaohongshu", "Ставка на МСБ и эфиры самих продавцов; объединили операционку байеров и продавцов", "Новые продавцы ×8,1 за 2024; GMV МСБ +436% (H1 2024)", "S14;S15"],
    ["Douyin", "Программа для промышленных кластеров (с 2022): фабрики продают напрямую в своих эфирах", "1,5 млн продавцов кластеров; 90 тыс.+ МСБ прошли 1 млн юаней через свои эфиры", "S01;S02"],
    ["Meesho", "Нулевая комиссия, продажа через ссылки в мессенджерах", "300 тыс. новых продавцов за H1 2024; 80% покупателей из небольших городов", "S16;S17"],
    ["TikTok Shop", "Аффилиатная программа: 15,4 млн авторов продают чужие товары за комиссию", "~42% GMV через авторов (оценка)", "S06"],
], columns=["Платформа", "Что сделали для новых продавцов", "Результат", "Источник"])
prog.style.hide(axis="index").set_properties(**{"text-align": "left", "vertical-align": "top"})
""")

# ---------------------------------------------------------------- 4
md(r"""
## 4. Какие авторы продают и кому доверяют

Два независимых сигнала говорят одно и то же: **небольшие авторы и обычные пользователи продают лучше охватных блогеров и аккаунтов брендов.** Вовлечённость падает с ростом аудитории, а российские покупатели больше доверяют друзьям и людям с личным опытом, чем официальным аккаунтам магазинов.
""")
code(r"""
fig, axes = plt.subplots(1, 2, figsize=(13.5, 4.9), gridspec_kw={"width_ratios": [1.15, 1]})
ax = axes[0]
t = nafi[nafi.block == "Источник"].pivot(index="item", columns="metric", values="value_pct")
t = t.reindex(["Друзья и знакомые", "Обычные пользователи с опытом", "Аккаунты брендов и магазинов"])
y = np.arange(len(t)); h = 0.38
b1 = ax.barh(y - h / 2, t["Доверяют"], h, color=SEQ[2], label="Доверяют", edgecolor=SURF, linewidth=2)
b2 = ax.barh(y + h / 2, t["Мотивирует к покупке"], h, color=VK, label="Мотивирует к покупке", edgecolor=SURF, linewidth=2)
hlabels(ax, b1, [f"{v}%" for v in t["Доверяют"]]); hlabels(ax, b2, [f"{v}%" for v in t["Мотивирует к покупке"]])
ax.set_yticks(y, t.index); ax.invert_yaxis(); ax.set_xlim(0, 105); hgrid(ax)
ax.xaxis.set_major_formatter(mtick.PercentFormatter(100)); ax.legend(loc="lower right")
ax.set_title("Россия: кому верят в соцсетях (НАФИ, 2026)")
ax = axes[1]
c = creators.copy(); c["label"] = c.platform + "\n" + c.tier
bars = ax.bar(c.label, c.engagement_pct, color=[CAT[2], CAT[2], GREY], width=0.55)
for b, v, mtr in zip(bars, c.engagement_pct, c.metric):
    ax.annotate(f"{ru(v, 2)}%\n{mtr}", (b.get_x() + b.get_width() / 2, b.get_height()), xytext=(0, 4), textcoords="offset points", ha="center", fontsize=9)
ax.set_ylim(0, 12); ax.yaxis.set_major_formatter(mtick.PercentFormatter(100, decimals=0)); ax.tick_params(axis="x", colors=INK2)
ax.set_title("Вовлечённость нано- и мега-авторов")
finish(fig, "Друзья мотивируют к покупке почти вдвое сильнее брендов; нано-авторы вовлекают в 2,3 раза лучше мега",
       "Слева — опрос НАФИ жителей городов-миллионников; справа — вовлечённость по размеру автора (методики разные, сравнивать внутри источника)",
       "Источники: " + cite("S25;S35;S36"), name="04_trust_creators")
""")

md(r"""
**Что это значит для авторов VK.** У шопсов уже 42 тыс.+ авторов и 1,6 млрд ₽ выплат за год, лидеры — мода, дом, путешествия, авто (S23). Но заказы уходят на Ozon. Механика оплаты за результат работает; её логично открыть для **собственных товарных сообществ VK**, сделав ставку на нано- и микроавторов и клиентов продавца (отзывы, «посоветуй другу»).
""")

# ---------------------------------------------------------------- 5
md(r"""
## 5. Кто покупает: возраст и пол

Соцкоммерция везде моложе классического e-commerce: Gen Z и миллениалы дают 62–70% трат. Женщины чаще покупают после контента. Покупатели Маркета ВКонтакте в датасете совпадают с этим профилем: 73% женщин, 25–34 лет — 28% против 17% у Партнёра.
""")
code(r"""
fig, axes = plt.subplots(1, 3, figsize=(14.5, 4.8), gridspec_kw={"width_ratios": [1, 1, 1]})
ax = axes[0]
d = pd.DataFrame({"k": ["Мир: доля трат\n(Accenture, прогноз 2025)", "США: доля покупателей\n(eMarketer, 2025)"], "v": [62, 70]})
bars = ax.bar(d.k, d.v, color=[SEQ[3], SEQ[5]], width=0.55)
for b, v in zip(bars, d.v):
    ax.annotate(f"{v}%", (b.get_x() + b.get_width() / 2, v), xytext=(0, 4), textcoords="offset points", ha="center", fontweight="bold")
ax.set_ylim(0, 85); ax.yaxis.set_major_formatter(mtick.PercentFormatter(100)); ax.set_title("Gen Z + миллениалы")
ax.tick_params(axis="x", colors=INK2, labelsize=9)
ax = axes[1]
d = demo[demo.metric == "Индекс трат в TikTok Shop vs средний"]
bars = ax.bar(d.segment, d.value, color=[CAT[1], SEQ[3]], width=0.5)
for b, v in zip(bars, d.value):
    ax.annotate(f"×{ru(v, 1)}", (b.get_x() + b.get_width() / 2, v), xytext=(0, 4), textcoords="offset points", ha="center", fontweight="bold")
ax.axhline(1, color=MUTED, ls="--", lw=1); ax.text(-0.45, 1.07, "средний покупатель", color=MUTED, fontsize=8.5, ha="left")
ax.set_ylim(0, 3.8); ax.set_title("TikTok Shop США: индекс трат по возрасту")
ax = axes[2]
d = pd.DataFrame({"k": ["Маркет VK\n(датасет)", "Партнёр\n(датасет)"], "w": [73, 74], "y": [28, 17]})
x = np.arange(2); w = 0.36
b1 = ax.bar(x - w / 2, d.w, w, color=CAT[4], label="Доля женщин", edgecolor=SURF, linewidth=2)
b2 = ax.bar(x + w / 2, d.y, w, color=VK, label="Доля 25–34 лет", edgecolor=SURF, linewidth=2)
for bs in (b1, b2):
    for b in bs:
        ax.annotate(f"{int(b.get_height())}%", (b.get_x() + b.get_width() / 2, b.get_height()), xytext=(0, 4), textcoords="offset points", ha="center", fontsize=9.5)
ax.set_xticks(x, d.k); ax.set_ylim(0, 95); ax.yaxis.set_major_formatter(mtick.PercentFormatter(100)); ax.legend(loc="upper right")
ax.set_title("Покупатели в датасете кейса"); ax.tick_params(axis="x", colors=INK2)
finish(fig, "Соцкоммерция — молодой канал: 18–34 тратят в 1,8–3,2 раза больше среднего; у Маркета VK 73% покупателей — женщины",
       "Возрастной и гендерный профиль покупателей социальной коммерции",
       "Источники: " + cite("S29;S30;S32;S43"), name="05_buyers")
""")

code(r"""
d = demo[demo.market == "Россия"][["segment", "metric", "value", "unit", "source_id"]]
d.style.hide(axis="index").format({"value": lambda v: ru(v)})
""")

# ---------------------------------------------------------------- 6
md(r"""
## 6. Что продаётся

Лидируют визуальные товары с невысоким чеком и импульсной покупкой: красота, одежда, дом, еда. В датасете у Маркета ВКонтакте 70% заказов дают «Продукты питания» и «Хобби», у Партнёра — «Дом и дача» и «Красота». Шопсы VK с товарами Ozon чаще всего продают товары для дома, бытовую химию, косметику и товары для животных (S24).
""")
code(r"""
plats = ["TikTok Shop США", "Маркет ВКонтакте (датасет)", "Партнёр (датасет)"]
fig, axes = plt.subplots(1, 3, figsize=(14.5, 3.9))
for ax, p, c in zip(axes, plats, [CAT[2], VK, PARTNER]):
    d = cats[cats.platform == p].sort_values("share_pct")
    bars = ax.barh(d.category, d.share_pct, color=c, height=0.6)
    hlabels(ax, bars, [f"{ru(v, 0)}%" for v in d.share_pct]); hgrid(ax)
    ax.set_xlim(0, 60); ax.xaxis.set_major_formatter(mtick.PercentFormatter(100)); ax.set_title(p)
finish(fig, "Продают визуальные товары повседневного спроса: красота, одежда, дом, еда",
       "Категории-лидеры: TikTok — доля GMV 2024; VK и Партнёр — доля заказов категорийного среза датасета",
       "Источники: " + cite("S11;S43"), name="06_categories")
""")

# ---------------------------------------------------------------- 7
md(r"""
## 7. Метрики VK против бенчмарков

Центральная таблица исследования. Для каждой метрики стратегии — значение в датасете VK, ориентир с других рынков и что из этого следует. Предлагаемая **главная метрика** для стратегии: *число товарных сообществ с хотя бы одним заказом, оплаченным внутри VK, за 30 дней* — она прямо отвечает обеим целям брифа (больше продающих бизнесов и больше заказов внутри VK).
""")
code(r"""
bench = pd.DataFrame([
    ["Продающие бизнесы", "Доля продавцов без продаж", "93% товарных сообществ (месяц)", ">50% магазинов TikTok Shop США (год)", "Проблема первой продажи общая; нужен отдельный путь для новичков", "S43;S06"],
    ["Продающие бизнесы", "Концентрация продаж", "Топ-10 (3,4% продавцов) = 54% заказов", "Топ-1% = 60% GMV TikTok Shop США", "Норма для рынка; цель — расширять базу, а не растить лидеров", "S43;S10"],
    ["Заказы внутри VK", "Конверсия открытие → заказ", "0,21% Маркет VK", "5,67% Партнёр; до ~30% в live-коммерции Китая", "Узкое место — оформление и оплата, а не охват", "S43;S37"],
    ["Заказы внутри VK", "Доля заказов, оплаченных на платформе", "1,2% Маркет VK", "Douyin, TikTok Shop, WeChat — оплата внутри приложения по умолчанию", "Встроенная оплата — условие цели «заказы внутри VK»", "S43;S01;S06"],
    ["Трафик", "Доля продаж из контента", "18,6% открытий из ленты и клипов", "60% GMV Douyin; 64% GMV TikTok Shop США; 32% GMV ЮВА", "Контент недоиспользован как источник продаж", "S43;S01;S06;S09"],
    ["Трафик", "Доля общей витрины", "0,2% открытий с главной Маркета", "Instagram убрал вкладку Shop (2023)", "Отдельная витрина не точка входа", "S43;S18"],
    ["Авторы", "Доля GMV через авторов", "Нет данных для своих продавцов; у Партнёра 94,8% открытий из реферальных постов", "~42% GMV TikTok Shop США; ~30% Douyin", "Аффилиатов стоит открыть для товарных сообществ VK", "S43;S06;S01"],
    ["Покупатели", "Ядро аудитории", "73% женщины; 25–34 — 28%", "Gen Z + миллениалы = 62–70% трат", "Профиль совпадает с мировым ядром соцкоммерции", "S43;S29;S30"],
], columns=["Цель", "Метрика", "VK (датасет кейса)", "Бенчмарк", "Вывод", "Источники"])
bench.style.hide(axis="index").set_properties(**{"text-align": "left", "vertical-align": "top"})
""")

code(r"""
fig, ax = plt.subplots(figsize=(12, 4.3))
rows = [("Конверсия открытие → заказ, %", 0.21, 5.67, "Партнёр (датасет)"),
        ("Доля продаж из контента, %", 18.6, 64, "TikTok Shop США (GMV)"),
        ("Доля заказов с оплатой на платформе, %", 1.2, 100, "Douyin / TikTok (оплата в приложении)")]
y = np.arange(len(rows)); h = 0.36
b1 = ax.barh(y - h / 2, [r[1] for r in rows], h, color=VK, label="VK (датасет кейса)", edgecolor=SURF, linewidth=2)
b2 = ax.barh(y + h / 2, [r[2] for r in rows], h, color=GREY, label="Бенчмарк", edgecolor=SURF, linewidth=2)
hlabels(ax, b1, [f"{ru(r[1], 2 if r[1] < 1 else 1)}%" for r in rows])
hlabels(ax, b2, [f"{ru(r[2], 2 if r[2] < 10 else 0)}% · {r[3]}" for r in rows])
ax.set_yticks(y, [r[0] for r in rows]); ax.invert_yaxis(); ax.set_xscale("log"); ax.set_xlim(0.1, 1500); hgrid(ax)
ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda v, _: f"{ru(v, 1 if v < 1 else 0)}%")); ax.legend(loc="upper right")
finish(fig, "Три разрыва VK с бенчмарками: оформление заказа, контент как источник продаж и оплата внутри платформы",
       "Значения VK из датасета кейса против ориентиров (логарифмическая шкала)",
       "Источники: " + cite("S43;S06") + ". Оплата 100% у Douyin/TikTok — свойство модели (чекаут в приложении), а не измеренная доля",
       name="07_gaps")
""")

# ---------------------------------------------------------------- 8
md(r"""
## 8. Какие модели подходят VK

Оценка команды по пяти критериям (1 — слабо, 5 — сильно). Это **экспертная оценка**, а не измерение: её стоит обсудить в команде и при необходимости поменять баллы в ячейке ниже — график и итог пересчитаются.

| Критерий | Что оцениваем |
|---|---|
| Опора на активы VK | Есть ли у VK нужное сейчас: сообщества, контент, авторы, сообщения, приём заказов и онлайн-оплата |
| Подтверждено датасетом | Есть ли в данных кейса признаки, что модель сработает |
| Масштаб на МСБ | Подходит ли длинному хвосту небольших продавцов |
| Заказы внутри VK | Остаётся ли заказ и оплата на платформе |
| Скорость запуска | Насколько быстро проверить пилотом (5 — быстро) |
""")
code(r"""
CRIT = ["Опора на активы VK", "Подтверждено датасетом", "Масштаб на МСБ", "Заказы внутри VK", "Скорость запуска"]
fit = pd.DataFrame([
    ["Контент сообщества + заказ и оплата в VK (Douyin)", 5, 4, 5, 5, 4],
    ["Аффилиаты-авторы для своих продавцов (TikTok Shop, шопсы)", 5, 4, 4, 4, 4],
    ["Социальный граф: подарок, «купи с другом», сообщения (WeChat)", 4, 3, 4, 5, 3],
    ["Переписка → оформленный заказ (Meesho, FB Marketplace)", 5, 3, 5, 4, 4],
    ["Групповые покупки (Pinduoduo)", 2, 1, 3, 5, 2],
    ["Нишевые live-аукционы (Whatnot)", 3, 2, 2, 5, 3],
    ["Отдельная витрина-маркетплейс (Instagram Shop)", 3, 1, 2, 4, 2],
], columns=["Модель"] + CRIT).set_index("Модель")
fit["Итог"] = fit[CRIT].mean(axis=1).round(1)
fit = fit.sort_values("Итог", ascending=False)

fig, ax = plt.subplots(figsize=(13, 5.2))
cmap = LinearSegmentedColormap.from_list("seq", SEQ)
M = fit[CRIT + ["Итог"]].values
im = ax.imshow(M, cmap=cmap, vmin=1, vmax=5, aspect="auto")
for i in range(M.shape[0]):
    for j in range(M.shape[1]):
        v = M[i, j]
        ax.text(j, i, ru(v, 1) if j == M.shape[1] - 1 else int(v), ha="center", va="center",
                fontsize=11 if j == M.shape[1] - 1 else 10, fontweight="bold", color="white" if v >= 3.5 else INK)
ax.set_xticks(range(M.shape[1]), [c.replace(" ", "\n", 1) for c in CRIT] + ["Итог"]); ax.set_yticks(range(len(fit)), fit.index)
ax.xaxis.tick_top(); ax.grid(False); ax.spines["bottom"].set_visible(False); ax.tick_params(axis="x", colors=INK2)
ax.axvline(len(CRIT) - 0.5, color=SURF, lw=4)
finish(fig, "Лучше всего VK подходят контент сообщества с заказом и оплатой внутри VK и авторы-аффилиаты",
       "Оценка команды, 1–5. Баллы можно изменить в ячейке выше", "Обоснование баллов — в разделах 2–7 и в research/data/cases.csv",
       top=0.86, name="08_fit_matrix")
""")

# ---------------------------------------------------------------- 9
md(r"""
## 9. Выводы для презентации

**Слайд «Место VK среди каналов» (бриф, задача 1).** Мировые лидеры соцкоммерции продают там, где человек уже смотрит контент и общается: Douyin и TikTok Shop получают около 60% GMV из видео и эфиров, WeChat растёт на подарках и чатах. Отдельная витрина в соцсети без контента не прижилась (Instagram, 2023). У VK есть всё сразу — сообщества, контент, авторы, сообщения, приём заказов и онлайн-оплата, — но они не связаны в один путь: заказ оформляют в VK, а оплачено внутри VK лишь 1,2% заказов. Это и есть позиционирование: **VK — место, где малый бизнес продаёт своим подписчикам и их друзьям, не уходя на маркетплейс.**

**Слайд «Целевые бизнесы» (задача 2).** Везде выигрывают МСБ, которые сами ведут контент и эфиры: у Douyin >90% бизнесов — МСБ, 90 тыс.+ из них прошли 1 млн юаней через собственные эфиры; Xiaohongshu за год увеличил число новых продавцов в 8 раз. При этом даже у TikTok Shop больше половины магазинов не продают. Целевой сегмент VK — товарные сообщества, которые принимают заказы в VK, но не подключили онлайн-оплату и доставку и не получили ни одного заказа (61% выборки).

**Слайд «Инструменты и авторы» (задача 3).** Продают нано- и микроавторы и обычные пользователи: друзья мотивируют к покупке в России почти вдвое сильнее брендов (66% против 35%). Авторы VK уже заработали 1,6 млрд ₽ на шопсах, но для товаров Ozon. Предложение: открыть аффилиатную механику для собственных продавцов VK и добавить «посоветовать другу / подарить» в карточку.

**Слайд «Роль Маркета» (задача 4).** Маркет — не отдельная витрина, а общая инфраструктура карточки, корзины и оплаты для сообществ, ленты, клипов и сообщений. Аргументы: главная даёт 0,2% открытий; Instagram свернул вкладку магазина; у Douyin витрина растёт как продолжение контента.

**Слайд «Экономика и метрики» (задачи 3, 5).** Главная метрика — число сообществ с заказом, оплаченным внутри VK, за 30 дней. Три разрыва с бенчмарками: конверсия открытие → заказ (0,21% против 5,67%), доля продаж из контента (19% против ~60%), оплата внутри платформы (1,2%).

**Ограничения.** Платформы раскрывают разные показатели; часть чисел — вторичные оценки (помечены `secondary`). Рынки Китая и США отличаются логистикой и платёжной инфраструктурой, поэтому переносим механики, а не абсолютные значения. Матрица в разделе 8 — экспертная оценка команды.
""")

code(r"""
# Полный список источников с уровнем достоверности
sources.style.hide(axis="index").set_properties(**{"text-align": "left"})
""")

nb = nbf.v4.new_notebook(); nb["cells"] = cells
nb["metadata"] = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                  "language_info": {"name": "python"}, "colab": {"provenance": [], "toc_visible": True}}
nbf.write(nb, OUT); print("written", OUT, len(cells))
