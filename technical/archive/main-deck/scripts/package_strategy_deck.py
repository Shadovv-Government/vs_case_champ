"""Package the eight-slide PDF and the separate submission appendices."""

from html import escape
import json
import os
from pathlib import Path

from reportlab import rl_config
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "presentation"
BUILD = ROOT / ".local" / "deck-build"
MATERIALS = ROOT / "materials" / "presentation"
TEAM = "Теневое Правительство"
BLUE = colors.HexColor("#0077FF")
INK = colors.HexColor("#142438")
MUTED = colors.HexColor("#52657A")
REPO = "https://github.com/Shadovv-Government/vs_case_champ/blob/8b1a979"


def register_fonts():
    regular, bold = (
        ("C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/arialbd.ttf")
        if os.name == "nt"
        else ("/System/Library/Fonts/Supplemental/Arial.ttf",
              "/System/Library/Fonts/Supplemental/Arial Bold.ttf")
    )
    pdfmetrics.registerFont(TTFont("CaseArial", os.getenv("CASE_FONT", regular)))
    pdfmetrics.registerFont(TTFont("CaseArialBold", os.getenv("CASE_BOLD_FONT", bold)))
    pdfmetrics.registerFontFamily("CaseArial", normal="CaseArial", bold="CaseArialBold")


def number(value, digits=0):
    return f"{value:,.{digits}f}".replace(",", " ").replace(".", ",").replace("-", "−")


def paragraph(text, role="body"):
    sizes = {"title": (23, 29, 12), "heading": (14, 19, 5), "body": (11, 14, 8),
             "cell": (10, 13, 0), "table_head": (10, 13, 0), "source": (10, 13, 5)}
    size, leading, gap = sizes[role]
    return Paragraph(text.replace("₽.", "руб.").replace("₽", "руб."), ParagraphStyle(
        role, fontName="CaseArial" if role in {"body", "cell", "source"} else "CaseArialBold",
        fontSize=size, leading=leading, spaceAfter=gap,
        textColor=colors.white if role == "table_head" else INK,
    ))


def table(rows, widths):
    cells = [[paragraph(str(x), "table_head" if i == 0 else "cell") for x in row]
             for i, row in enumerate(rows)]
    result = Table(cells, colWidths=widths, repeatRows=1, hAlign="LEFT")
    result.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), INK),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#EFF5FC"), colors.white]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return result


def source(label, url):
    return paragraph(f'<link href="{escape(url, quote=True)}" color="#005EC8"><u>{escape(label)}</u></link>', "source")


def document(suffix, title, story):
    target = OUT / f"{TEAM}_{suffix}.pdf"

    def decorate(page, doc):
        page.setFillColor(BLUE)
        page.rect(0, A4[1] - 9, A4[0], 9, fill=1, stroke=0)
        page.setFillColor(MUTED)
        page.setFont("CaseArial", 9)
        page.drawString(42, 26, f"VK Case Champ 2026 · {TEAM}")
        page.drawRightString(A4[0] - 42, 26, str(doc.page))

    SimpleDocTemplate(
        str(target), pagesize=A4, title=title, author=TEAM,
        leftMargin=42, rightMargin=42, topMargin=40, bottomMargin=42,
    ).build(story, onFirstPage=decorate, onLaterPages=decorate)


def percent(fraction, digits=0):
    return number(fraction * 100, digits) + "%"


def disclosure_story(disclosure):
    return [
        paragraph("Использование ИИ", "title"),
        *(paragraph(escape(block)) for block in disclosure.strip().split("\n\n")[1:]),
    ]


def evidence_appendix(evidence, disclosure):
    model = evidence["projection"]
    pilot = evidence["pilot"]
    build = model["economics"]
    scenarios = model["scenarios"]
    base = scenarios["base"]
    head = paragraph
    c = model["vk_contribution_per_paid_order_rub"]
    order_contribution = c * base["paid_share"]
    if base["monthly_order_hurdle"] is None:
        payback = "В этом сценарии для покрытия затрат требуются другие источники вклада."
    else:
        payback = (f"При вкладе {number(order_contribution, 1)} ₽ это "
                   f"{number(base['monthly_order_hurdle'])} дополнительных заказов в месяц.")
    chart_rows = [["Открытия из контента", "Сообщества", "С заказами", "Доля с заказом"]]
    for row in evidence["cohort_stats"]:
        chart_rows.append([
            row["openings"], number(row["communities"]),
            number(row["selling"]), percent(row["selling_rate"], 1),
        ])
    threshold_rows = [["Открытий за месяц"] + [
        f"≥{row['openings_at_least']}" for row in evidence["thresholds"]
    ], ["Сообществ с 0 заказов"] + [
        number(row["communities_without_orders"]) for row in evidence["thresholds"]
    ], ["Доля открытий среди 233"] + [
        percent(row["opening_share"], 1) for row in evidence["thresholds"]
    ]]
    invited = number(model["reference_invited_communities"])
    rows = [[f"На {invited} приглашённых", "Осторожный", "Базовый", "Верхний"]]
    for label, key, digits, style in [
        ("Подключатся среди приглашённых", "adoption", 0, "percent"),
        ("Прирост заказов на подключившегося", "orders_per_adopter", 2, "number"),
        ("Прирост доли с заказом у подключившихся", "seller_rate_lift", 0, "pp"),
        ("Доп. заказы в VK за 30 дней", "monthly_orders_per_reference_invites", 0, "number"),
        ("Доп. сообщества с заказом", "monthly_selling_per_reference_invites", 0, "number"),
        ("Будут исполнены / из них новые продажи", None, 0, "pair"),
        ("Доп. исполненные продажи во всех каналах", "monthly_net_merchant_sales_per_reference_invites", 0, "number"),
    ]:
        values = []
        for scenario in scenarios.values():
            if style == "percent":
                value = percent(scenario[key], digits)
            elif style == "pp":
                value = f"{number(scenario[key] * 100, digits)} п. п."
            elif style == "pair":
                value = f"{percent(scenario['fulfillment_share'])} / {percent(scenario['incremental_sales_share'])}"
            else:
                value = number(scenario[key], digits)
            values.append(value)
        rows.append([label, *values])

    power_rows = [["Дисперсия заказов", "В каждую группу", "С запасом 10% в каждую группу"]]
    for size in pilot["sample_sizes"]:
        power_rows.append([
            number(size["order_variance"], 2), number(size["per_arm"]),
            number(size["per_arm_with_reserve"]),
        ])

    document("evidence", "VK Заказ рядом — аналитический отчёт", [
        head("Аналитический отчёт", "title"),
        head("1. Где искать барьер оформления", "heading"),
        head(f"Из {number(evidence['goods_communities'])} товарных и смешанных сообществ "
             f"{number(evidence['checkout_enabled'])} имеют флаг чекаута ({number(evidence['checkout_pct'], 1)}%). "
             f"У {number(evidence['selling_in_month'])} есть хотя бы один заказ за месяц "
             f"({number(evidence['selling_pct'], 1)}%). В {number(evidence['checkout_and_catalog'])} "
             "сообществах с активным каталогом и чекаутом заказы распределены так:"),
        table(chart_rows, [174, 111, 112, 110]),
        Spacer(1, 8),
        head("Фильтр по листу «Бизнесы»", "heading"),
        head("<b>C</b> — товарное или смешанное сообщество, <b>Q &gt; 0</b> — есть активные товары, "
             "<b>R = 1</b> — чекаут на конец месяца, <b>O</b> — открытия карточек из контента, "
             "<b>W</b> — заказы за месяц. В группе с W = 0 и O &gt; 0 меняем порог открытия:"),
        table(threshold_rows, [190, 79, 79, 79, 80]),
        Spacer(1, 8),
        head(f"При пороге ≥10 остаётся {number(evidence['warm_at_least_10_opens'])}. "
             f"Медиана открытий у них {number(evidence['strict_median_opens'])} против "
             f"{number(evidence['warm_median_opens'])} в широкой группе. "
             f"В теме «Творчество и хендмейд» {number(evidence['strict_topics']['Творчество и хендмейд'])} из "
             f"{number(evidence['warm_at_least_10_opens'])}. Старт с малых мастерских — гипотеза рекрутинга. "
             "Проверяем реальные обращения о варианте, наличии и самовывозе, наличие товара и время ответа."),
        head(f"У {number(evidence['ready_orders_without_content_opens'])} сообществ с нулём открытий из контента были заказы. "
             "Открытия учитывают одну группу источников, флаги описывают конец периода. Размер и ассортимент магазина "
             "могут объяснять различия. Синтетический месяц помогает искать признаки для отбора и задавать вопросы продавцам."),
        head("Что считать заказом", "heading"),
        head(f"В агрегатах VK {number(evidence['market_orders'])} оформленных и "
             f"{number(evidence['market_paid_orders'])} оплаченных внутри VK заказов. Другие заказы могут оплачиваться "
             f"при получении или снаружи. В партнёрском потоке {number(evidence['partner_orders'])} заказов "
             f"и {number(evidence['partner_direct_clicks'])} прямых переходов. Прямые переходы — лишь один из маршрутов."),
        source("Датасет VK · листы «Бизнесы», «Маркет Вконтакте — итоги» и «Источники»", f"{REPO}/sources/dataset.xlsx"),
        source("Q&A организаторов · 13:31, 22:38, 33:20, 39:40, 45:02 и 49:58", "https://vkvideo.ru/video-92204627_456240708"),

        PageBreak(),
        head("2. Роль VK среди каналов", "title"),
        head("Выбранная позиция", "heading"),
        head("Малый бизнес продаёт своей аудитории там, где она его уже знает. Контент показывает товар в использовании. "
             "Клиент уточняет детали и подтверждает заказ из переписки. VK сохраняет связь покупателя с конкретным "
             "сообществом и получает измеримый заказ. Сайт продавца даёт контроль над покупкой и требует отдельно привлекать спрос."),
        table([
            ["Канал", "Где начинается покупка", "Что получает продавец"],
            ["Ozon", "Поиск по широкому ассортименту", "Готовая аудитория, оформление и логистика по условиям Ozon"],
            ["Авито", "Поиск по объявлениям и уточнение в чате", "Связь с покупателем, доставка или самовывоз"],
            ["VK Заказ рядом", "Рекомендация, шопс или диалог с магазином", "Свой каталог, подтверждение условий и заказ в том же сообществе"],
        ], [107, 175, 225]),
        Spacer(1, 8),
        head("Что оставляем в Маркете", "heading"),
        head(f"Витрины, каталог, поиск, оформление и учёт заказов. Из {number(evidence['market_total_opens'])} "
             "открытий нативных карточек в датасете витрины дают 39,1%, лента и клипы — 18,6%, "
             "главная Маркета — 0,2%, поиск — 1,9%, «Другое» — 40,2%. Это посещения карточек. "
             "Главную можно улучшать отдельным тестом с сопоставимыми затратами, измеряя прирост суммарных "
             "внутренних заказов по всем входам. Партнёрский маршрут оставляем для спроса на ассортимент партнёра. "
             "Его заказы идут в Ozon Seller и считаются отдельно."),
        head("Что уже есть в VK и у аналогов", "heading"),
        head("У VK есть товарные метки, шопсы, чекаут и продвижение с авторами. Prodamus умеет отправить "
             "в чат состав покупки и счёт, а также выставить счёт по уже созданному заказу VK. Проверяем, "
             "добавляет ли заказы <b>штатный черновик по товару из каталога до оформления заказа</b>, "
             "после которого выдача и статус относятся к одному номеру. Сверка кабинета — первый этап."),
        head("Weixin Mini Shops соединяет социальные взаимодействия, контент и платежи. TikTok Shop сочетает "
             "витрину, контент с товарными метками, чекаут и авторские продажи. Эти примеры помогают выбрать "
             "путь пользователя. Эффект для собственного магазина VK оцениваем в своём эксперименте."),
        head("За год работы шопсов VK сообщила о 9,5 млн выкупленных заказов товаров Ozon. Этот результат "
             "показывает, что через этот маршрут уже проходят покупки. Прирост у продавцов Магазина VK измеряем отдельно."),
        source("VK · итоги III квартала 2026 года и лента шопсов", "https://vk.company.ru/ru/press/releases/12477/"),
        source("VK и Ozon · результаты первого года шопсов", "https://vk.company.ru/ru/press/releases/12431/"),
        source("Prodamus · два сценария заказов и счёта в сообщениях", "https://prodamus.ru/blog/kak-prinimat-platezhi-iz-vkontakte-s-pomoschyu-prodamus"),
        source("Ozon · интеграция с VK и маршрут до Ozon Seller", "https://seller.ozon.ru/media/boost/kak-rabotaet-integraciya-ozon-i-vkontakte/"),
        source("Авито · самовывоз и получение заказа", "https://t.me/s/AvitoLive/5039"),
        source("Tencent · Weixin Mini Shops, с. 3–5", "https://static.www.tencent.com/uploads/2025/11/24/7f70c308ee5e84548f3c782c22e4a077.pdf"),
        source("TikTok · модель Shop и авторская программа", "https://newsroom.tiktok.com/introducing-tiktok-shop?lang=en"),

        PageBreak(),
        head("3. Как подключать и развивать МСБ", "title"),
        head("Кого подключаем и с какой задачей", "heading"),
        head("<b>Первыми</b> — малые магазины и мастерские, у которых есть товары и недавние вопросы покупателей "
             "о варианте, наличии или выдаче. Задача — завершить покупку после консультации и подготовить выдачу. "
             "Проверяем, приходится ли покупателю повторно вводить данные и ведёт ли продавец сделки вручную."),
        head("<b>Вторыми</b> — сообщества с товаром, которым не хватает обращений. Задача — создать доступный "
             "контент с товаром и получить первые обращения. <b>У действующих бизнесов без каталога</b> "
             "сначала проверяем, можно ли подключить один ходовой товар и получить продажу. "
             "Путь сервисных бизнесов с расписанием и записью требует отдельной проверки."),
        table([
            ["Шаг и инструмент", "Эффект для бизнеса и покупателя", "Эффект для VK"],
            ["1. Вход из кабинета магазина. Чек-лист одного товара", "Быстрее готовится первый товар. Покупатель видит актуальное наличие и получение", "Доля приглашённых с товаром, готовым к продаже, и доля активировавшихся"],
            ["2. Шаблон шопса и товарная метка. Для слабого спроса — отдельный тест продвижения", "Покупатель узнаёт товар в контенте. Бизнес получает целевые открытия и вопросы", "Дополнительные обращения и валидные заказы на 1 000 показов"],
            ["3. Штатный чекаут из карточки или черновик продавца из чата", "Меньше ручных действий. Покупатель видит согласованные товар, цену и получение", "Валидные заказы на сообщество и доля диалогов с подтверждением"],
            ["4. Статус выдачи, связь с продавцом по номеру", "Покупатель отслеживает выдачу. Продавцу проще обработать вопрос и возврат", "Доля исполненных и повторные заказы. Отмены, дубли и обращения в поддержку"],
        ], [145, 181, 181]),
        Spacer(1, 8),
        head("Первый контакт с бизнесом", "heading"),
        head("Начинаем с приглашений в кабинете магазина и одной демонстрации по реальному товару. Для продавца "
             "обещание простое: отправить покупателю заказ с условиями, которые они уже согласовали. После подтверждённого "
             "прироста используем VK Education и разбор первого успешного запуска. Продавцов со слабым входящим спросом "
             "приглашаем в отдельный тест дистрибуции. VK Рекламу и VK AdBlogger тестируем поверх работающей воронки "
             "отдельно, с удержанием контрольной группы и учётом затрат на стимулирование."),
        head("Когда остаток или цена меняются", "heading"),
        head("Черновик фиксирует вариант, цену, количество, получение и срок подтверждения. Перед заказом проверяем "
             "актуальность условий. Если цена изменилась или товара нет, продавец обновляет черновик, покупатель "
             "подтверждает заново. Повторное нажатие возвращает существующий номер. Сначала тестируем самовывоз "
             "с оплатой при получении. Далее добавляем способы, доступные продавцу в штатном магазине."),
        source("VK Education · инструменты продаж и карточки в контенте", "https://object2-ac.vk-apps.com/vk-education-0554ff56-27eb-4093-a702-685722cef6d9/media/7f/d57feb9aadd64a7398136615c637acc9.pdf"),
        source("VK · партнёрская сеть шопсов и VK AdBlogger", "https://vk.company.ru/ru/press/releases/12423/"),

        PageBreak(),
        head("4. Сценарии эффекта и экономика", "title"),
        head(f"30 дней, {invited} предложений подходящим сообществам. Все параметры — сценарные допущения. "
             "Долю подключившихся считаем от всех, кому отправили приглашение в кабинет магазина."),
        table(rows, [239, 89, 89, 90]),
        Spacer(1, 8),
        head("Как считаем", "heading"),
        head("Заказы = приглашённые × доля подключившихся × прирост заказов на подключившегося. "
             "Для числа продавцов с заказом используем прирост доли с заказом. Исполненные продажи сверх привычных "
             "каналов = дополнительные заказы VK × исполнение × доля действительно новых продаж."),
        head(f"Заказ на {number(build['aov_rub'])} ₽ при марже {percent(build['seller_gross_margin'])} и "
             f"{number(build['seller_fulfillment_rub'])} ₽ за комплектацию и выдачу оставляет продавцу "
             f"{number(model['seller_contribution_per_completed_order_without_service_rub'])} ₽ до труда, налогов "
             f"и постоянных затрат. При комиссии {percent(build['service_fee'])} остаётся "
             f"{number(model['seller_contribution_per_completed_order_with_service_rub'])} ₽. Вклад VK — {number(c)} ₽ "
             f"с оплаченного через сервис и исполненного заказа после эквайринга и переменных затрат. "
             f"В базе таких заказов {percent(base['paid_share'])} от всех дополнительных. Вклад на дополнительный "
             f"заказ — {number(order_contribution, 1)} ₽."),
        head("Что нужно для расширения", "heading"),
        head(f"На условные {number(model['reference_goods_communities'] / 1000)} тыс. товарных и смешанных сообществ "
             f"при доле приглашённых {percent(base['reach'])} от подходящих "
             f"и одинаковом эффекте на приглашённого получаем {number(base['monthly_incremental_orders_at_scale'])} "
             "заказов в месяц для фильтра 233/4 158 и "
             f"{number(base['monthly_orders_strict_pool_at_scale'])} для фильтра 39/4 158. Доступную базу и эффект "
             "для каждой группы проверяем по живым данным VK."),
        head(f"Допущения затрат — {number(build['development_rub'] / 1_000_000, 1)} млн ₽ разработки, в том числе "
             f"бюджет прототипа, и {number(build['monthly_fixed_rub'] / 1000)} тыс. ₽ поддержки в месяц. "
             f"На масштабе нужно {number(model['monthly_fixed_plus_development_rub'] / 1000)} тыс. ₽ в месяц "
             f"на поддержку и покрытие разработки за {build['steady_payback_months']} месяцев. {payback} "
             f"При постепенном запуске база даёт {number(base['year_one_orders'])} заказов за первый год "
             f"и {number(base['year_one_vk_cash_flow_rub'] / 1_000_000, 2)} млн ₽ денежного результата VK."),
        head("Поэтапный запуск в модели", "heading"),
        head("Месяцы 1–3 — подготовка. Доли охвата целевого масштаба в месяцах 4–12 — 10%, 20%, 35%, 50%, "
             "65%, 80%, 90%, 100%, 100%. Комиссия в сценариях не финансирует разработку сама. Оценку дополнительного "
             "чистого вклада рекламы считаем в контрольном тесте с учётом перетока бюджета с других кампаний VK. "
             "Модель на 12 месяцев воспроизводится по исходному XLSX и JSON с параметрами сценариев."),

        PageBreak(),
        head("5. Пилот и условия продолжения", "title"),
        head("Дни 1–40. Оценить барьер и стоимость", "heading"),
        head("До 14-го дня проводим 8 интервью с продавцами и 5 тестов нового и текущего пути. Сверяем работу "
             "каталога, чекаута и переписки на тестовом сообществе. Если штатный черновик уже есть, ищем "
             "подтверждённую потерю на входе или предзаполнении. В дни 15–40 до 30 продавцов проверяют сценарий. "
             "Для перехода нужны воспроизводимое оформление, отсутствие дублей при повторных действиях, видимый "
             "статус и доступная база для эксперимента."),
        head(f"Из лимита {number(pilot['pre_experiment_budget_rub'] / 1000)} тыс. ₽ сначала выделяем "
             f"{number(pilot['research_rub'] / 1000)} тыс. на исследование. Если продавцы подтвердят, что "
             f"согласованные условия приходится переносить вручную, до {number(pilot['prototype_rub'] / 1000)} тыс. "
             f"пойдут на прототип и {number(pilot['instrumentation_and_qa_rub'] / 1000)} тыс. на события и QA. "
             "Бюджет A/B-теста уточняем после прототипа."),
        head("Дни 41–90. Измерить добавленные заказы", "heading"),
        head("Контроль — текущий путь. Тест — тот же путь с черновиком из чата. Для A/B можно приглашать разные "
             "категории со свежими вопросами о покупке. Условия продвижения одинаковы. Назначаем вариант случайно "
             "с учётом тематики и прошлой активности. Все магазины владельца получают один вариант. Считаем все "
             "назначенные сообщества за 30 дней и отслеживаем статус ещё 14 дней."),
        head("Первичная метрика — валидные заказы собственных продавцов на назначенное сообщество. "
             "Считаем по уникальным номерам заказов, оформленных покупателями. Исключаем технические и фродовые записи по правилам, "
             "заданным до теста. Дополнительно считаем долю с заказом, валидные исполнения на сообщество и покупки "
             "во всех каналах на подвыборке учёта с согласия продавцов."),
        head(f"Порог продолжения — ≥{number(pilot['minimum_orders_per_invited'], 3)} заказа на сообщество, примерно "
             "один дополнительный заказ на 13 приглашённых. Фиксируем порог до случайного назначения. Нижняя граница "
             "95%-го интервала должна быть выше нуля. Следим, чтобы исполненные заказы на бизнес не снижались, "
             "прирост доли отмен не превышал 2 п. п., доля жалоб не росла и заказы не дублировались. "
             "Масштабируем при подтверждённой экономике и измеряемой дополнительной продаже."),
        head("Размер выборки", "heading"),
        head("При двустороннем уровне 5% и мощности 80% для обнаружения эффекта 0,075 при независимых продавцах "
             "n ≈ 2 × (1,96 + 0,84)² × дисперсия / 0,075² в каждую группу."),
        table(power_rows, [161, 147, 199]),
        Spacer(1, 7),
        head("Дисперсия в таблице условная. До теста рассчитываем её по живому ряду и учитываем кластеризацию магазинов. "
             "Если доступной выборки не хватает, оцениваем работоспособность и сбор событий на прототипе. "
             "Решение о масштабе требует отдельного полноценного измерения."),
        source("Бриф VK Case Champ · задания и критерии, с. 7–9, 20", f"{REPO}/sources/case-brief.pdf"),

        PageBreak(),
        *disclosure_story(disclosure),
    ])


def main():
    rl_config.useA85 = False
    register_fonts()
    evidence = json.loads((MATERIALS / "evidence.json").read_text(encoding="utf-8"))
    deck = canvas.Canvas(str(OUT / f"{TEAM}_strategy_msk.pdf"), pagesize=(960, 540))
    deck.setTitle(f"{TEAM} — VK Заказ рядом")
    deck.setAuthor(TEAM)
    for slide in range(1, 9):
        deck.drawImage(str(BUILD / f"slide-{slide}.png"), 0, 0, 960, 540)
        deck.showPage()
    deck.save()
    disclosure = (MATERIALS / "ai_disclosure.md").read_text(encoding="utf-8")
    document("AI_disclosure", "Раскрытие использования ИИ", disclosure_story(disclosure))
    evidence_appendix(evidence, disclosure)


if __name__ == "__main__":
    main()
