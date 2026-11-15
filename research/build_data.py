"""Собирает датасет бенчмарков социальной коммерции в research/data/*.csv.

Каждое число привязано к источнику (sources.csv) и уровню достоверности:
  official  — отчётность или пресс-релиз самой компании
  research  — отраслевое исследование (Momentum Works, McKinsey, Accenture, НАФИ, Data Insight, eMarketer…)
  secondary — пересказ в СМИ/блогах без доступа к первоисточнику; использовать с оговоркой
Запуск: python research/build_data.py
"""
from pathlib import Path
import csv

OUT = Path(__file__).parent / "data"
OUT.mkdir(exist_ok=True)

# ---------------------------------------------------------------- источники
SOURCES = [
    # id, издатель, название, url, дата публикации, тип
    ("S01", "36Kr", "Douyin E-commerce 2024 GMV ~3.5 trn yuan; shelf >40%, store livestream >30%", "https://eu.36kr.com/en/p/3166066575158018", "2025-01", "secondary"),
    ("S02", "Sixth Tone", "Skincare to Seafood, China's Trade Hubs Ride the Livestream Wave (Douyin industrial belts report)", "https://www.sixthtone.com/news/1016455", "2025-01", "research"),
    ("S03", "Kuaishou Technology", "Fourth Quarter and Full Year 2024 Financial Results", "https://kuaishou.gcs-web.com/news-releases/news-release-details/kuaishou-technology-announces-fourth-quarter-and-full-year-2024", "2025-03-25", "official"),
    ("S04", "Kuaishou Technology", "Third Quarter 2024 Unaudited Financial Results", "https://itiger.com/news/2484422166", "2024-11", "official"),
    ("S05", "Dolphin Research", "Kuaishou Q2 2024: monthly active e-commerce buyers 131 mn", "https://longportapp.cn/topics/23304657", "2024-08", "secondary"),
    ("S06", "Momentum Works", "TikTok Shop in the U.S. 2025", "https://momentum.asia/insights/detail/tiktok-shop-in-the-us-2025", "2026-01", "research"),
    ("S07", "DealStreetAsia / Momentum Works", "TikTok Shop hits $15.1b GMV in US as SEA doubles to $45.6b in 2025", "https://cdn.dealstreetasia.com/stories/tiktok-shop-gmv-2025-472662", "2026-01", "research"),
    ("S08", "Momentum Works (The Low Down)", "Southeast Asia platform e-commerce reaches US$157.6B in 2025", "https://thelowdown.momentum.asia/new-report-southeast-asias-platform-ecommerce-reaches-us157-6b-in-2025-with-top-platforms-expanding-share-to-98-8/", "2026", "research"),
    ("S09", "e27", "Southeast Asia's live commerce boom enters its harder second act (Momentum Works Live Commerce 2026)", "https://e27.co/southeast-asias-live-commerce-boom-enters-its-harder-second-act-20260908/", "2026-09", "secondary"),
    ("S10", "Pulse / Marketplace Pulse", "On TikTok Shop, 1% of sellers drive 60% of GMV", "https://www.pulse.bot/ecommerce/news/on-tiktok-shop-1-of-sellers-drive-60-of-gmv-bef85eb3-e698-49b0-ac71-1a52b8b48024/", "2025", "secondary"),
    ("S11", "FitSmallBusiness (Momentum Works data)", "30 TikTok Shop Statistics: category shares US 2024", "https://fitsmallbusiness.com/tiktok-shop-statistics/", "2025", "secondary"),
    ("S12", "KrASIA", "WeChat outlines its e-commerce ambitions at latest Open Class event", "https://kr-asia.com/wechat-outlines-its-e-commerce-ambitions-at-latest-open-class-event", "2025-01", "secondary"),
    ("S13", "Tech Buzz China", "Tencent's e-Commerce Revival, Part 3", "https://techbuzzchina.substack.com/p/tencents-e-commerce-revival-part-17a", "2025-08", "secondary"),
    ("S14", "Jing Daily", "Xiaohongshu sees 8.1 times growth in new merchants in 2024", "https://jingdaily.com/intels/2025-01/15/xiaohongshu-sees-8-1-times-growth-in-new-merchants-in-2024", "2025-01-15", "secondary"),
    ("S15", "Jing Daily", "Small business GMV surges on Xiaohongshu (H1 2024)", "https://jingdaily.com/intels/2024-09/18/small-business-gmv-surges-on-xiaohongshu", "2024-09-18", "secondary"),
    ("S16", "Business Standard / Meesho", "Meesho achieves 35% Y-o-Y order growth fuelled by small towns, Gen Z", "https://business-standard.com/companies/news/meesho-achieves-35-y-o-y-order-growth-fueled-by-small-towns-gen-z-124121300402_1.html", "2024-12-13", "official"),
    ("S17", "Apparel Resources", "Meesho onboards three lakh sellers in first half of 2024", "https://in.apparelresources.com/business-news/retail/meesho-announces-onboarding-three-lakh-sellers-first-half-2024", "2024-07", "secondary"),
    ("S18", "Marketing Dive", "Instagram removes Shop tab (social commerce retreat)", "https://www.marketingdive.com/news/instagram-removes-shop-tab-social-commerce-marketing-tiktok/640246/", "2023-01", "secondary"),
    ("S19", "Marketing Dive", "Instagram sunsets live shopping in social commerce retreat", "https://www.marketingdive.com/news/instagram-sunsets-live-shopping-social-commerce-retreat/642826/", "2023-02", "secondary"),
    ("S20", "Value Added Resource", "Facebook Shops forces onsite checkout & ends fee waiver", "https://valueaddedresource.net/facebook-shops-forces-onsite-checkout-ends-fee-waiver", "2023-04", "secondary"),
    ("S21", "Cropink", "Facebook Marketplace statistics (purchase channel split)", "https://cropink.com/fb-marketplace-statistics", "2025-04-29", "secondary"),
    ("S22", "Value Added Resource", "Whatnot surpassed $3 billion 2024 GMV", "https://valueaddedresource.net/whatnot-3-billion-2024-gmv-raises-funding", "2025-01", "secondary"),
    ("S23", "VK (пресс-релиз)", "Авторы ВКонтакте заработали 1,6 млрд рублей на шопсах", "https://vk.company.ru/ru/press/releases/12423/", "2026-09-29", "official"),
    ("S24", "VK (пресс-релиз)", "Пользователи ВКонтакте оформили 9,5 млн заказов на Ozon через шопсы", "https://vk.ru/press/shops-year-records", "2026-10", "official"),
    ("S25", "Российская газета / НАФИ", "Почти половина россиян покупают одежду и косметику в соцсетях и мессенджерах", "https://rg.ru/2026/06/19/pochti-polovina-rossiian-pokupaiut-odezhdu-i-kosmetiku-v-socsetiah-i-messendzherah.html", "2026-06-19", "research"),
    ("S26", "Intellinews / Data Insight", "E-commerce grows up to 80% in Russian regions in 2024 (market ~11 trn RUB)", "https://www.intellinews.com/e-commerce-grows-up-to-80-in-russian-regions-in-2024-361854/", "2025", "secondary"),
    ("S28", "esports.ru / Mediascope", "ВКонтакте и Telegram возглавили рейтинг социальных платформ (DAU сентябрь 2025)", "https://esports.ru/news/vkontakte-i-telegram-vozglavili-rejting-soczialnykh-platform/", "2025-10-28", "secondary"),
    ("S29", "Accenture (Business Wire)", "Why Shopping's Set for a Social Revolution", "https://www.businesswire.com/news/home/20220103005434/en/", "2022-01-03", "research"),
    ("S30", "eMarketer", "Gen Z & Millennials will account for over 70% of US social buyers (2025)", "https://www.emarketer.com/chart/269285/gen-z-millennials-will-account-over-70-of-us-social-buyers-collectively-2025-of-total-us-social-buyers-by-generation-2024-2025", "2024-11", "research"),
    ("S31", "eMarketer", "Data Drop: 4 charts on social shopping habits", "https://www.emarketer.com/content/data-drop-4-charts-on-social-shopping-habits", "2024", "research"),
    ("S32", "Earnest Analytics", "TikTok Shop customers skew young, but not just Gen Z", "https://www.earnestanalytics.com/?p=18331", "2024", "research"),
    ("S33", "YouGov", "Are US TikTok users turning to TikTok Shop?", "https://yougov.com/articles/52193-are-us-tiktok-users-turning-to-tiktok-shop", "2025", "research"),
    ("S34", "eMarketer", "TikTok views lead to shares, research, purchases — especially among women (DISQO)", "https://www.emarketer.com/content/actions-taken-from-tiktok-views", "2024", "research"),
    ("S35", "eMarketer / Captiv8", "Instagram's nano-influencers outperform — as do TikTok's upper echelon of creators", "https://www.emarketer.com/content/exclusive-instagram-s-nano-influencers-outperform-as-do-tiktok-s-upper-echelon-of-creators", "2024", "research"),
    ("S36", "NetInfluencer / SushiVid", "TikTok nano-influencer engagement far outpaces other platforms", "https://www.netinfluencer.com/tiktok-nano-influencer-engagement-far-outpaces-other-platforms-per-report/", "2025", "secondary"),
    ("S37", "McKinsey", "It's showtime! How live commerce is transforming the shopping experience", "https://www.mckinsey.com/capabilities/tech-and-ai/our-insights/its-showtime-how-live-commerce-is-transforming-the-shopping-experience", "2021-07", "research"),
    ("S38", "Statista / CNNIC", "Share of live commerce users in China (Dec 2023: 54.7%)", "https://www.statista.com/statistics/1295800/china-share-of-live-commerce-users/", "2024", "research"),
    ("S39", "ecommerceDB", "Social commerce: women in China (Douyin female orders +65%)", "https://ecommercedb.com/insights/social-commerce-in-china-female-consumers-women-s-day-douyin/4742", "2024-03", "secondary"),
    ("S40", "KrASIA", "Kuaishou adopts 'user-first' e-commerce strategy (RMB 100 bn traffic for new merchants)", "https://kr-asia.com/kuaishou-adopts-user-first-e-commerce-strategy-to-win-over-customers", "2024", "secondary"),
    ("S41", "Chozan", "PDD Holdings: how Pinduoduo and Temu built a social commerce model", "https://chozan.co/pdd-holdings/", "2025", "secondary"),
    ("S42", "Entrepreneur India", "Inside Meesho: insights from India's most misunderstood unicorn (reseller model, women)", "https://india.entrepreneur.com/news-and-trends/inside-meesho-insights-from-indias-most-misunderstood/502064", "2023", "secondary"),
    ("S43", "VK Case Champ", "Синтетический датасет кейса (sources/dataset.xlsx), сентябрь 2026", "sources/dataset.xlsx", "2026-11", "official"),
]

# ---------------------------------------------------------------- кейсы (одна строка = одна платформа)
# archetype: как устроен путь к покупке
CASES = [
    dict(platform="Douyin", market="Китай", archetype="Интерес-коммерция: контент + полка + стрим магазина",
         where_buy="Внутри приложения (чекаут, своя логистика партнёров)", year=2024,
         gmv_native=3500, gmv_currency="CNY bn", gmv_usd_bn=486, growth_pct=30,
         best_sellers="МСБ и фабрики промышленных кластеров со своим стримом (店播); >90% бизнесов — МСБ",
         best_creators="Сам продавец в эфире (стрим магазина) + авторы; 90 тыс.+ МСБ прошли 1 млн юаней именно через собственные эфиры",
         buyer_profile="18–35 ядро; заказы женщин +65% г/г",
         outcome="Успех", lesson_for_vk="Собственный эфир/контент продавца даёт сопоставимый с авторами объём; поиск-«полка» уже >40% GMV — контент и витрина работают вместе",
         sources="S01;S02;S39"),
    dict(platform="Kuaishou", market="Китай", archetype="Доверительная коммерция: стримеры-«свои», приватный домен",
         where_buy="Внутри приложения", year=2024,
         gmv_native=1389.6, gmv_currency="CNY bn", gmv_usd_bn=193, growth_pct=17.3,
         best_sellers="Малые продавцы, фермеры, региональные бренды; новые продавцы +30% г/г",
         best_creators="Стримеры с лояльной подпиской (повторные покупки у «своего»)",
         buyer_profile="Малые города и регионы (62% потребителей local life — города низших уровней)",
         outcome="Успех", lesson_for_vk="Отдельная программа трафика для новых продавцов (100 млрд юаней) — платформа сама снимает барьер первой продажи",
         sources="S03;S04;S05;S40"),
    dict(platform="WeChat (Channels + Mini Store + Mini Programs)", market="Китай", archetype="Социальный граф и приватный домен: сообщество → чат → покупка",
         where_buy="Внутри мессенджера (мини-магазины, подарки друзьям)", year=2024,
         gmv_native=None, gmv_currency="", gmv_usd_bn=None, growth_pct=92,
         best_sellers="Бренды и локальный бизнес с собственной базой клиентов (официальный аккаунт + группа)",
         best_creators="Сам бизнес и его клиенты; подарки и групповые скидки внутри чатов",
         buyer_profile="Вся аудитория мессенджера, сильнее старшие возрасты",
         outcome="Растёт", lesson_for_vk="Ближайший аналог VK: сообщество + сообщения + платёж. Рост дают механики социального графа (подарок, «купи с другом»), а не витрина",
         sources="S12;S13"),
    dict(platform="Xiaohongshu (RED)", market="Китай", archetype="Контент-отзывы + «байеры»-стримеры",
         where_buy="Внутри приложения", year=2024,
         gmv_native=None, gmv_currency="", gmv_usd_bn=None, growth_pct=None,
         best_sellers="Нишевые и малые бренды: число МСБ +379% г/г, их GMV +436% (H1 2024); новые продавцы ×8,1 за 2024",
         best_creators="«Байеры» — эксперты-кураторы с небольшой аудиторией (кейс: 35 тыс. подписчиков → 3 млн юаней в месяц)",
         buyer_profile="Молодые женщины крупных городов",
         outcome="Растёт", lesson_for_vk="Экспертные авторы средней величины продают лучше охватных; ставка на МСБ дала кратный рост",
         sources="S14;S15"),
    dict(platform="TikTok Shop US", market="США", archetype="Интерес-коммерция + аффилиаты",
         where_buy="Внутри приложения", year=2025,
         gmv_native=15.1, gmv_currency="USD bn", gmv_usd_bn=15.1, growth_pct=68,
         best_sellers="DTC-бренды красоты и моды; 803,5 тыс. магазинов, но >50% без продаж, 2 000+ магазинов >$1 млн",
         best_creators="15,4 млн аффилиатов; ~42% GMV через авторов (вторичная оценка)",
         buyer_profile="18–24 тратят в 3,2 раза выше среднего, 25–34 — в 1,8; 35–44 растут быстрее всех",
         outcome="Успех", lesson_for_vk="Даже у лидера большинство магазинов не продаёт: проблема «первой продажи» универсальна. 50% GMV — видео, 36% — витрина, 14% — эфиры",
         sources="S06;S07;S10;S32"),
    dict(platform="TikTok Shop + Shopee/Lazada, ЮВА", market="Юго-Восточная Азия", archetype="Контент-коммерция внутри маркетплейсов и соцсети",
         where_buy="Внутри приложения", year=2025,
         gmv_native=45.6, gmv_currency="USD bn", gmv_usd_bn=45.6, growth_pct=100,
         best_sellers="Локальные МСБ и бренды; контент-коммерция = 32% GMV платформ",
         best_creators="Эфиры и видео самих продавцов + аффилиаты",
         buyer_profile="Молодая мобильная аудитория",
         outcome="Успех", lesson_for_vk="Контент-коммерция выросла на 98% за год до $49,7 млрд — классические маркетплейсы были вынуждены встроить видео и эфиры",
         sources="S07;S08;S09"),
    dict(platform="Instagram / Facebook Shops", market="США и мир", archetype="Отдельная витрина магазина в соцсети",
         where_buy="Сначала внешний сайт, с 2023 — обязательный чекаут в США", year=2023,
         gmv_native=None, gmv_currency="", gmv_usd_bn=None, growth_pct=None,
         best_sellers="Бренды с готовым e-commerce",
         best_creators="—",
         buyer_profile="Миллениалы, Gen X",
         outcome="Свёрнуто", lesson_for_vk="Вкладку Shop убрали из навигации (2023), live shopping закрыли (2022–2023). Отдельная витрина без потока контента не прижилась — прямая параллель с главной Маркета VK (0,2% открытий)",
         sources="S18;S19;S20;S21"),
    dict(platform="Facebook Marketplace + Messenger", market="США и мир", archetype="Классифайд внутри соцсети + переписка",
         where_buy="Договорённость в сообщениях, оплата часто вне платформы", year=2024,
         gmv_native=None, gmv_currency="", gmv_usd_bn=None, growth_pct=None,
         best_sellers="Частные лица и малый локальный бизнес; >1/3 малых бизнесов США продают через Marketplace",
         best_creators="—",
         buyer_profile="Широкая аудитория Facebook",
         outcome="Успех (вне чекаута)", lesson_for_vk="77,7% покупателей в Facebook покупают на Marketplace и лишь 14,2% в Shops: люди идут туда, где есть локальные объявления и чат",
         sources="S21"),
    dict(platform="Meesho", market="Индия", archetype="Социальный реселлинг через WhatsApp/соцсети",
         where_buy="Приложение Meesho (ссылки распространяются в мессенджерах)", year=2024,
         gmv_native=None, gmv_currency="", gmv_usd_bn=None, growth_pct=35,
         best_sellers="Малые производители одежды и товаров для дома; 300 тыс. новых продавцов за H1 2024",
         best_creators="Реселлеры-«микроинфлюенсеры» своего круга, более половины — женщины",
         buyer_profile="175 млн покупателей в год, ~80% из городов 2-го уровня и ниже",
         outcome="Успех", lesson_for_vk="Доверие к знакомому продавцу важнее охвата: сарафан внутри переписки масштабируется на регионы",
         sources="S16;S17;S42"),
    dict(platform="Pinduoduo", market="Китай", archetype="Групповые покупки через социальный граф",
         where_buy="Внутри приложения, вирусность через WeChat", year=2024,
         gmv_native=None, gmv_currency="", gmv_usd_bn=None, growth_pct=None,
         best_sellers="Фермеры и фабрики с низкой ценой (16 млн+ аграрных продавцов, вторичная оценка)",
         best_creators="Сами покупатели, приглашающие друзей за скидку",
         buyer_profile="Регионы, чувствительные к цене",
         outcome="Успех", lesson_for_vk="Механика «позови друга — получи цену» превращает соцграф в канал привлечения без рекламного бюджета",
         sources="S41"),
    dict(platform="Whatnot", market="США", archetype="Live-аукционы нишевых сообществ",
         where_buy="Внутри приложения", year=2024,
         gmv_native=3.0, gmv_currency="USD bn", gmv_usd_bn=3.0, growth_pct=None,
         best_sellers="Нишевые продавцы коллекционных товаров, карт, кроссовок, винтажа",
         best_creators="Сами продавцы-ведущие эфиров; топ-500 продавцов заработали ≥$1 млн",
         buyer_profile="Энтузиасты-коллекционеры",
         outcome="Успех", lesson_for_vk="Сообщество по интересу + эфир продавца: GMV $3 млрд в 2024 и >$6 млрд в 2025",
         sources="S22"),
    dict(platform="ВКонтакте — шопсы (товары Ozon)", market="Россия", archetype="Аффилиатный контент авторов → внешний маркетплейс",
         where_buy="На стороне Ozon", year=2026,
         gmv_native=None, gmv_currency="", gmv_usd_bn=None, growth_pct=None,
         best_sellers="Продавцы Ozon (22 тыс.+ использовали продвижение через авторов)",
         best_creators="42 тыс.+ авторов, 1,6 млрд руб. дохода за год; лидеры — мода, дом, путешествия, авто",
         buyer_profile="Пользователи VK; категории-лидеры: дом, бытовая химия, косметика, товары для животных",
         outcome="Растёт", lesson_for_vk="Механика авторов уже работает (700 тыс. шопсов, 45 млрд просмотров, 9,5 млн заказов), но заказ уходит к Партнёру. Её можно открыть для собственных продавцов VK",
         sources="S23;S24"),
]

# ---------------------------------------------------------------- показатели в длинном формате
M = []
def m(platform, market, metric, value, unit, year, source, conf, note=""):
    M.append(dict(platform=platform, market=market, metric=metric, value=value, unit=unit,
                  year=year, source_id=source, confidence=conf, note=note))

# Масштаб
m("Douyin", "Китай", "GMV", 3500, "CNY bn", 2024, "S01", "secondary", "цель была 4 трлн")
m("Douyin", "Китай", "Рост GMV", 30, "% г/г", 2024, "S01", "secondary")
m("Kuaishou", "Китай", "GMV", 1389.6, "CNY bn", 2024, "S03", "official")
m("Kuaishou", "Китай", "Рост GMV", 17.3, "% г/г", 2024, "S03", "official")
m("TikTok Shop", "Мир", "GMV", 64.3, "USD bn", 2025, "S07", "research")
m("TikTok Shop", "ЮВА", "GMV", 45.6, "USD bn", 2025, "S07", "research", "71% глобального GMV TikTok Shop")
m("TikTok Shop", "США", "GMV", 15.1, "USD bn", 2025, "S06", "research")
m("TikTok Shop", "США", "GMV", 9.0, "USD bn", 2024, "S06", "research")
m("TikTok Shop", "США", "Рост GMV", 68, "% г/г", 2025, "S06", "research")
m("Whatnot", "США", "GMV", 3.0, "USD bn", 2024, "S22", "secondary")
m("Платформы ЮВА", "ЮВА", "Контент-коммерция, GMV", 49.7, "USD bn", 2025, "S09", "secondary", "Shopee + TikTok Shop + Lazada, +98% г/г")
m("Платформы ЮВА", "ЮВА", "Доля контент-коммерции в GMV", 32, "%", 2025, "S09", "secondary")
m("Платформы ЮВА", "ЮВА", "Доля live-коммерции в GMV", 14, "%", 2024, "S09", "secondary")
m("Мир", "Мир", "Прогноз рынка соцкоммерции", 1200, "USD bn", 2025, "S29", "research", "прогноз Accenture 2022; 2021 — $492 млрд")
m("Россия", "Россия", "Рынок e-commerce", 11000, "RUB bn", 2024, "S26", "secondary", "+40% г/г, Data Insight")
m("ВКонтакте", "Россия", "Среднесуточная аудитория (DAU)", 58.0, "млн", 2025, "S28", "secondary", "Mediascope, сентябрь 2025")
# Каналы внутри платформы
m("Douyin", "Китай", "Доля «полки» (поиск, витрина) в GMV", 40, "%", 2024, "S01", "secondary", ">40%")
m("Douyin", "Китай", "Доля стримов самих магазинов в GMV", 30, "%", 2024, "S01", "secondary", "чуть больше 30%")
m("Douyin", "Китай", "Доля стримов авторов в GMV", 30, "%", 2024, "S01", "secondary", "остаток; оценка")
m("TikTok Shop", "США", "Доля видео в GMV", 50, "%", 2025, "S06", "research")
m("TikTok Shop", "США", "Доля витрины (Shop tab) в GMV", 36, "%", 2025, "S06", "research")
m("TikTok Shop", "США", "Доля эфиров в GMV", 14, "%", 2025, "S06", "research")
m("TikTok Shop", "США", "Доля GMV через авторов-аффилиатов", 42, "%", 2025, "S06", "secondary", "вторичные оценки 42–45%")
m("Маркет ВКонтакте (датасет)", "Россия", "Доля открытий карточки из витрин магазинов", 39.1, "%", 2026, "S43", "official")
m("Маркет ВКонтакте (датасет)", "Россия", "Доля открытий карточки из ленты и клипов", 18.6, "%", 2026, "S43", "official")
m("Маркет ВКонтакте (датасет)", "Россия", "Доля открытий карточки с главной Маркета", 0.2, "%", 2026, "S43", "official")
m("Партнёр (датасет)", "Россия", "Доля открытий из реферальных постов и клипов", 94.8, "%", 2026, "S43", "official")
# Продавцы
m("Douyin", "Китай", "Доля МСБ среди бизнесов", 90, "%", 2024, "S02", "research", ">90%")
m("Douyin", "Китай", "МСБ, прошедшие 1 млн юаней через свои эфиры", 90000, "продавцов", 2024, "S01", "secondary")
m("Douyin", "Китай", "Продавцы промышленных кластеров", 1500000, "продавцов", 2024, "S02", "research")
m("Kuaishou", "Китай", "Рост числа новых продавцов", 30, "% г/г", 2024, "S04", "official", "Q3 2024")
m("Kuaishou", "Китай", "Покупатели e-commerce в месяц", 131, "млн", 2024, "S05", "secondary", "Q2 2024, +14,1%")
m("Xiaohongshu", "Китай", "Рост числа новых продавцов", 710, "% г/г", 2024, "S14", "secondary", "×8,1")
m("Xiaohongshu", "Китай", "Рост GMV МСБ", 436, "% г/г", 2024, "S15", "secondary", "H1 2024")
m("TikTok Shop", "США", "Магазины", 803500, "магазинов", 2025, "S06", "research")
m("TikTok Shop", "США", "Доля магазинов без продаж", 50, "%", 2025, "S06", "research", "«более половины»")
m("TikTok Shop", "США", "Доля GMV у топ-1% продавцов", 60, "%", 2025, "S10", "secondary")
m("TikTok Shop", "США", "Авторы-аффилиаты", 15.4, "млн", 2025, "S06", "research")
m("Meesho", "Индия", "Покупатели в год", 175, "млн", 2024, "S16", "official", "+25%")
m("Meesho", "Индия", "Рост заказов", 35, "% г/г", 2024, "S16", "official")
m("Meesho", "Индия", "Доля покупателей из городов 2-го уровня и ниже", 80, "%", 2024, "S16", "official")
m("Meesho", "Индия", "Новые продавцы за H1", 300000, "продавцов", 2024, "S17", "secondary")
m("ВКонтакте — шопсы", "Россия", "Авторы в программе монетизации", 42000, "авторов", 2026, "S23", "official")
m("ВКонтакте — шопсы", "Россия", "Доход авторов за год", 1.6, "RUB bn", 2026, "S23", "official")
m("ВКонтакте — шопсы", "Россия", "Выкупленные заказы Ozon", 9.5, "млн", 2026, "S24", "official")
m("ВКонтакте — шопсы", "Россия", "Просмотры шопсов", 45, "млрд", 2026, "S24", "official")
m("ВКонтакте — шопсы", "Россия", "Опубликовано шопсов", 700000, "публикаций", 2026, "S24", "official")
m("Маркет ВКонтакте (датасет)", "Россия", "Доля GMV у топ-10 продавцов (выборка)", 42, "%", 2026, "S43", "official", "заказы — 54%")
m("Маркет ВКонтакте (датасет)", "Россия", "Доля товарных сообществ без заказов", 93.1, "%", 2026, "S43", "official")
# Воронка
m("Маркет ВКонтакте (датасет)", "Россия", "Конверсия открытие карточки → заказ", 0.21, "%", 2026, "S43", "official")
m("Партнёр (датасет)", "Россия", "Конверсия открытие карточки → заказ", 5.67, "%", 2026, "S43", "official")
m("Live-коммерция", "Китай", "Конверсия в live-коммерции", 30, "%", 2021, "S37", "research", "«приближается к 30%», до 10× выше обычного e-commerce; возвраты выше")
m("Facebook", "США", "Доля покупателей, покупающих на Marketplace", 77.7, "%", 2024, "S21", "secondary")
m("Facebook", "США", "Доля покупателей, покупающих в Shops", 14.2, "%", 2024, "S21", "secondary")
m("Facebook", "США", "Доля покупателей, покупающих в Messenger", 8.1, "%", 2024, "S21", "secondary")

# ---------------------------------------------------------------- покупатели
DEMO = [
    # market, segment, metric, value, unit, year, source, conf
    ("Мир", "Gen Z + миллениалы", "Доля трат на соцкоммерцию (прогноз)", 62, "%", 2025, "S29", "research"),
    ("США", "Gen Z + миллениалы", "Доля покупателей в соцсетях", 70, "%", 2025, "S30", "research"),
    ("США", "Gen Z (покупатели в соцсетях)", "Покупали после контента автора", 82, "%", 2024, "S31", "research"),
    ("США", "18–24", "Индекс трат в TikTok Shop vs средний", 3.2, "×", 2024, "S32", "research"),
    ("США", "25–34", "Индекс трат в TikTok Shop vs средний", 1.8, "×", 2024, "S32", "research"),
    ("США", "Мужчины", "Покупали в TikTok Shop за год (пользователи TikTok)", 33, "%", 2025, "S33", "research"),
    ("США", "Женщины", "Покупали в TikTok Shop за год (пользователи TikTok)", 28, "%", 2025, "S33", "research"),
    ("США", "Женщины", "Покупали после видео в TikTok", 31, "%", 2024, "S34", "research"),
    ("США", "Мужчины", "Покупали после видео в TikTok", 22, "%", 2024, "S34", "research"),
    ("Китай", "Все интернет-пользователи", "Пользуются live-коммерцией", 54.7, "%", 2023, "S38", "research"),
    ("Китай", "Женщины (Douyin)", "Рост числа заказов", 65, "% г/г", 2024, "S39", "secondary"),
    ("Россия", "Жители городов-миллионников", "Покупали через соцсети, сообщества, каналы", 49, "%", 2026, "S25", "research"),
    ("Россия", "Пользователи соцсервисов", "Покупали прямо из публикации", 46, "%", 2026, "S25", "research"),
    ("Россия", "Пользователи соцсервисов", "Покупали из публикации неоднократно", 27, "%", 2026, "S25", "research"),
    ("Россия", "Жители городов-миллионников", "Хотят покупать из публикации в 1–2 клика", 72, "%", 2026, "S25", "research"),
    ("Россия", "Маркет ВКонтакте (датасет)", "Доля женщин среди покупателей", 73, "%", 2026, "S43", "official"),
    ("Россия", "Маркет ВКонтакте (датасет)", "Доля 25–34 среди покупателей", 28, "%", 2026, "S43", "official"),
    ("Россия", "Партнёр (датасет)", "Доля 25–34 среди покупателей", 17, "%", 2026, "S43", "official"),
]

# Россия: где видят товарные публикации и чему доверяют (НАФИ, S25)
RU_TRUST = [
    ("Площадка", "ВКонтакте", "Видели шопсы за месяц", 49),
    ("Площадка", "Telegram", "Видели шопсы за месяц", 35),
    ("Площадка", "YouTube", "Видели шопсы за месяц", 19),
    ("Площадка", "ВКонтакте", "Интересно знакомиться с товарами через публикации", 46),
    ("Площадка", "Telegram", "Интересно знакомиться с товарами через публикации", 37),
    ("Площадка", "YouTube", "Интересно знакомиться с товарами через публикации", 26),
    ("Источник", "Друзья и знакомые", "Доверяют", 90),
    ("Источник", "Обычные пользователи с опытом", "Доверяют", 82),
    ("Источник", "Аккаунты брендов и магазинов", "Доверяют", 72),
    ("Источник", "Друзья и знакомые", "Мотивирует к покупке", 66),
    ("Источник", "Обычные пользователи с опытом", "Мотивирует к покупке", 52),
    ("Источник", "Аккаунты брендов и магазинов", "Мотивирует к покупке", 35),
    ("Что помогает купить", "Цена в публикации", "Важно", 53),
    ("Что помогает купить", "Отзывы и оценки", "Важно", 48),
    ("Что помогает купить", "Реальные фото и видео", "Важно", 47),
    ("Что помогает купить", "Понятное описание товара", "Важно", 42),
]

# Вовлечённость по размеру автора (разные методики — сравнивать внутри источника)
CREATORS = [
    ("Instagram", "Нано (<10 тыс.)", 6.23, "средний ER", "S35"),
    ("TikTok", "Нано", 8.95, "медианный ER", "S36"),
    ("TikTok", "Мега", 3.90, "медианный ER", "S36"),
]

# Категории-лидеры
CATS = [
    ("TikTok Shop США", "Красота и уход", 21, "доля GMV", 2024, "S11"),
    ("TikTok Shop США", "Женская одежда и бельё", 13, "доля GMV", 2024, "S11"),
    ("TikTok Shop США", "Спорт и отдых", 7, "доля GMV", 2024, "S11"),
    ("Маркет ВКонтакте (датасет)", "Продукты питания", 44.9, "доля заказов категорийного среза", 2026, "S43"),
    ("Маркет ВКонтакте (датасет)", "Хобби и развлечения", 25.4, "доля заказов категорийного среза", 2026, "S43"),
    ("Маркет ВКонтакте (датасет)", "Дом и дача", 8.3, "доля заказов категорийного среза", 2026, "S43"),
    ("Маркет ВКонтакте (датасет)", "Гардероб", 6.7, "доля заказов категорийного среза", 2026, "S43"),
    ("Партнёр (датасет)", "Дом и дача", 31.0, "доля заказов категорийного среза", 2026, "S43"),
    ("Партнёр (датасет)", "Красота и здоровье", 27.2, "доля заказов категорийного среза", 2026, "S43"),
    ("Партнёр (датасет)", "Транспорт", 5.8, "доля заказов категорийного среза", 2026, "S43"),
]


def write(name, rows, header):
    with open(OUT / name, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


write("sources.csv", SOURCES, ["source_id", "publisher", "title", "url", "published", "type"])
write("cases.csv", [[c.get(k) for k in CASES[0]] for c in CASES], list(CASES[0]))
write("metrics.csv", [[r[k] for k in M[0]] for r in M], list(M[0]))
write("demographics.csv", DEMO, ["market", "segment", "metric", "value", "unit", "year", "source_id", "confidence"])
write("russia_nafi.csv", [r + ("S25",) for r in RU_TRUST], ["block", "item", "metric", "value_pct", "source_id"])
write("creators.csv", CREATORS, ["platform", "tier", "engagement_pct", "metric", "source_id"])
write("categories.csv", CATS, ["platform", "category", "share_pct", "metric", "year", "source_id"])

ids = {s[0] for s in SOURCES}
used = {x for c in CASES for x in c["sources"].split(";")} | {r["source_id"] for r in M} | {d[6] for d in DEMO} | {"S25"} | {c[4] for c in CREATORS} | {c[5] for c in CATS}
assert used <= ids, used - ids
print(f"ok: {len(CASES)} кейсов, {len(M)} показателей, {len(SOURCES)} источников; не использованы: {sorted(ids - used)}")
