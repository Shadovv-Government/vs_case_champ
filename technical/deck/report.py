"""Build the analytical appendix from the evidence used for the slides."""
from html import escape
from pathlib import Path

from reportlab import rl_config
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ASSETS = Path(__file__).resolve().parent / 'assets'
INK = HexColor('#102639')
MUTED = HexColor('#526981')
BLUE = HexColor('#0063CB')
SYNTHETIC = 'https://github.com/Shadovv-Government/vs_case_champ/blob/7c8bd6d/sources'
Q_AND_A = 'https://vkvideo.ru/video-92204627_456240708'


def number(value, digits=0):
    return f'{value:,.{digits}f}'.replace(',', ' ').replace('.', ',').replace('-', '−')


def percent(fraction, digits=0):
    return f'{number(100 * fraction, digits)}%'


def amount(value):
    return number(value, 1 if value != round(value) else 0)


def paragraph(text, role='body'):
    settings = {
        'title': (24, 30, 13), 'heading': (14, 18, 6), 'body': (10.5, 14.1, 8),
        'cell': (9.5, 12.3, 0), 'column': (9.5, 12.3, 0), 'source': (9.5, 12.5, 5),
    }
    size, leading, after = settings[role]
    return Paragraph(text, ParagraphStyle(
        role,
        fontName='GolosCaseBold' if role in ('title', 'heading', 'column') else 'GolosCase',
        fontSize=size, leading=leading, spaceAfter=after,
        textColor=white if role == 'column' else INK,
    ))


def source(label, url):
    return paragraph(f'<link href="{escape(url, quote=True)}" color="#0063CB"><u>{escape(label)}</u></link>', 'source')


def table(rows, widths):
    formatted = [[paragraph(escape(str(cell)), 'column' if index == 0 else 'cell')
                  for cell in row] for index, row in enumerate(rows)]
    result = Table(formatted, colWidths=widths, repeatRows=1, hAlign='LEFT')
    result.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), INK),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#EFF5FC'), white]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    return result


def write_pdf(destination, title, team, story):
    def decorate(page, doc):
        page.setFillColor(BLUE)
        page.rect(0, A4[1]-8, A4[0], 8, fill=1, stroke=0)
        page.setFillColor(MUTED)
        page.setFont('GolosCase', 9)
        page.drawString(42, 26, f'VK Case Champ 2026 · {team}')
        page.drawRightString(A4[0]-42, 26, str(doc.page))

    SimpleDocTemplate(
        str(destination), title=title, author=team, pagesize=A4,
        leftMargin=42, rightMargin=42, topMargin=38, bottomMargin=42,
    ).build(story, onFirstPage=decorate, onLaterPages=decorate)


def disclosure_story(disclosure, heading_role='title'):
    heading, *body = disclosure.strip().split('\n\n')
    return [paragraph(escape(heading.removeprefix('# ')), heading_role),
            *(paragraph(escape(block)) for block in body)]


def evidence_story(e):
    o, m, p = e['observed'], e['model'], e['pilot']
    traffic = e['market_totals']
    h = paragraph
    names = ('0 активных товаров', 'Товары есть, чекаут выключен',
             'Товары и чекаут, 0 открытий из контента',
             'Товары и чекаут, 1–9 открытий из контента',
             'Товары и чекаут, ≥10 открытий из контента')
    cohorts = [['Состояние сообщества', 'Всего', 'Без заказов']]
    cohorts.extend([name, number(size), number(zero)]
                   for name, size, zero in zip(names, o['groups'], o['groups_without_orders']))
    model_rows = [['Вариант на 1 000', 'С заказом', 'Заказов на продавца с заказом', 'Заказы', 'Прирост продавцов / заказов']]
    control = e['control']
    control_orders = round(1_000 * control['share_with_orders'] * control['orders_per_selling_community'])
    model_rows.append(['Контроль', percent(control['share_with_orders']),
                       number(control['orders_per_selling_community'], 1), number(control_orders), '—'])
    for scenario in e['scenarios']:
        model_rows.append([scenario['label'], percent(scenario['p']), number(scenario['m'], 1),
                           number(control_orders + scenario['order_lift']),
                           f"+{scenario['seller_lift']} / +{scenario['order_lift']}"])
    post_rows = [['Вариант', 'Прирост доли с шопсом', 'Заказов на доп. магазин с шопсом', 'Прирост магазинов / заказов']]
    for scenario in e['post_scenarios']:
        post_rows.append([scenario['label'], f"+{number(100*scenario['publisher_rate_lift'])} п. п.",
                          number(scenario['orders_per_additional_publisher'], 1),
                          f"+{scenario['publisher_lift']} / +{scenario['order_lift']}"])
    connection = e['connection']
    example_volume = number(m['example_monthly_orders'])
    payback_rows = [['Доля сервиса среди исполненных', 'Вклад с оформления',
                     'Порог в месяц', f'Первый год при {example_volume}/мес.']]
    for scenario in m['sensitivity']:
        threshold = scenario['breakeven_monthly_orders']
        payback_rows.append([percent(scenario['paid_service_share']), f"{amount(scenario['net_per_order'])} ₽",
                             number(threshold) if threshold is not None else 'Вклад ≤0',
                             f"{number(scenario['example_year_result']/1_000_000, 1)} млн ₽"])
    reach = m['monthly_eligible_reach']
    scale_text = ('Если эффект из теста оформления сохранится в месячном окне, для базового порога нужны '
                  f"{number(reach[0]['communities'])} подходящих сообществ в среднем сценарии или "
                  f"{number(reach[1]['communities'])} в сильном. Доступный охват проверяем по живым данным."
                  if len(reach) == 2 else
                  'Коммерческий объём зависит от положительного вклада и доступного охвата.')
    sample_rows = [['Дисперсия заказов', 'Заказ из чата', 'Подсказка шопса']]
    sample_rows.extend([number(row['variance'], 1), number(row['per_arm_with_reserve']),
                        number(row['post_per_arm_with_reserve'])]
                       for row in p['sample_size'])

    return [
        h('Аналитический отчёт', 'title'),
        h('1. Данные и выбор продавцов', 'heading'),
        h(f"Синтетический срез за сентябрь 2026 года. Из {number(o['goods'])} товарных и смешанных сообществ "
          f"{number(o['checkout'])} имеют флаг чекаута на конец месяца. "
          f"Хотя бы один заказ за месяц есть у {number(o['sellers_with_orders'])}. "
          "Состояние чекаута и каталога относится к концу периода, заказы — ко всему периоду."),
        table(cohorts, [272, 105, 130]),
        Spacer(1, 8),
        h('Кого проверяем в первую очередь', 'heading'),
        h(f"Товарный контент. У {number(o['quiet_with_normal_views_without_product_posts'])} из "
          f"{number(o['quiet'])} сообществ с товарами, чекаутом, нулём заказов и открытий из контента "
          "были просмотры обычного контента и отсутствовали товарные посты и клипы. Для живого пилота "
          "подтверждаем устойчивый охват и товар, который можно купить."),
        h(f"Оформление. Из {number(o['warm'])} с открытиями и без заказов у {number(o['warm_at_least_10'])} "
          f"было хотя бы 10 открытий. На них приходится {percent(o['warm_high_opening_share'], 1)} всех "
          "открытий этой группы. Кандидатов ищем по недавним вопросам о покупке и реальному остатку. "
          "Открытия карточек помогают выбрать группу для исследования."),
        h(f"У {number(o['no_content_openings_with_orders'])} сообществ с каталогом и чекаутом были заказы "
          "при нуле открытий из контента. Это поле охватывает один набор точек входа. Реальные продажи вне VK, "
          "содержание переписки и история статуса чекаута в синтетическом срезе неизвестны."),
        h('Роль Маркета в цифрах', 'heading'),
        h(f"Из {number(traffic['opens'])} открытий карточек витрины дали {number(e['market_pct'][0], 1)}%, "
          f"лента и клипы — {number(e['market_pct'][1], 1)}%, главная — {number(e['market_pct'][2], 1)}%, "
          f"поиск — {number(traffic['search_pct'], 1)}%, «Другое» — {number(traffic['other_pct'], 1)}%. "
          f"В агрегатах {number(traffic['orders'])} собственных оформлений и {number(traffic['paid_in_vk'])} "
          "оплат через VK. По остальным заказам способ оплаты и исполнение неизвестны. У Партнёра 1 "
          f"{number(traffic['partner_orders'])} заказов, в том числе возможны маршруты через "
          f"{number(traffic['partner_direct_clicks'])} прямых переходов. Партнёр 1 — условная площадка, "
          "её воронку считаем отдельно."),
        h(f"Сумма заказов VK по строкам листа «Категории» равна {number(traffic['category_orders'])}, "
          f"сводный объём — {number(traffic['orders'])}. Правила согласования срезов неизвестны. "
          "Общий объём берём из «Итогов», он совпадает с суммой дней. Категорийный лист используем "
          "для описания его собственных строк."),
        source('Датасет · «Бизнесы», «Источники», «Категории» и «Итоги»', f'{SYNTHETIC}/dataset.xlsx'),
        source('Q&A · метрика, заказ без онлайн-оплаты и роль витрины, 13:31, 22:56, 39:40, 46:18', Q_AND_A),
        PageBreak(),

        h('2. Позиция VK и путь бизнеса', 'title'),
        h('VK помогает купить у сообщества, которое покупатель нашёл в контенте или знает по переписке. '
          'Маркет сохраняет поиск и рекомендации, Магазин сообщества ведёт собственные карточки и заказы. '
          'Вклад главной проверяем отдельно по суммарным заказам при сопоставимых затратах. Партнёрский '
          'чекаут Ozon учитываем отдельно.'),
        table([
            ['Канал', 'Где появляется спрос', 'Как оформляют', 'Как ведут клиента'],
            ['Ozon', 'Поиск в каталоге', 'Чекаут и выдача Ozon', 'Заказ в Ozon Seller'],
            ['Авито', 'Поиск по объявлениям', 'Доставка или самовывоз', 'Чат и состояние сделки'],
            ['Сайт продавца', 'Трафик продавца', 'Свой чекаут', 'Свои каналы поддержки'],
            ['Weixin Mini Shops', 'Контент и общение', 'Карточки и оплата Weixin', 'Общение в Weixin'],
            ['TikTok Shop', 'Видео, эфиры, авторы', 'Корзина и чекаут Shop', 'Заказы в приложении'],
            ['VK Заказ рядом', 'Шопс, витрина или диалог', 'Заказ по каталогу сообщества', 'Чат, номер заказа и выдача'],
        ], [105, 134, 134, 134]),
        Spacer(1, 8),
        h('От первого контакта до продажи', 'heading'),
        h('Действующему магазину показываем приглашение в кабинете. После подтверждения эффекта зовём новую '
          'мастерскую через VK Education или сообщества предпринимателей. Мастерская создаёт сообщество, '
          'добавляет один собственный товар и настраивает чекаут и получение. Магазин с вопросами о покупке '
          'переходит к черновику в чате, магазин с охватом — к товарной публикации.'),
        h('Покупатель открывает штатный чекаут из шопса или подтверждает согласованные товар и условия из чата. '
          'Обновление цены и остатка требует нового согласия, повтор подтверждения возвращает тот же номер. '
          'При самовывозе продавец меняет статус выдачи и видит оформление в аналитике сообщества.'),
        h('Шопсы доступны, а Prodamus отправляет счёт в переписке. Проверяем черновик штатного заказа с '
          'вариантом товара и возможностью оплаты при получении. Если черновик уже доступен, проверяем, '
          'где покупатель или продавец теряет согласованные условия.'),
        source('VK · шопсы и авторы', 'https://vk.company.ru/ru/press/releases/12423/'),
        source('Prodamus · счёт из переписки и оплата существующего заказа', 'https://prodamus.ru/blog/kak-prinimat-platezhi-iz-vkontakte-s-pomoschyu-prodamus'),
        source('Ozon · маршрут из VK в Ozon Seller', 'https://seller.ozon.ru/media/boost/kak-rabotaet-integraciya-ozon-i-vkontakte/'),
        source('Авито · самовывоз', 'https://t.me/s/AvitoLive/5039'),
        source('Tencent · Weixin Mini Shops, раздел Business', 'https://www.tencent.com/wp-content/uploads/2026/10/c700_Joshua-PS-Publication-Announcement.pdf'),
        source('TikTok · запуск Shop, товарные видео, эфиры и управление заказами', 'https://newsroom.tiktok.com/introducing-tiktok-shop?lang=en'),
        PageBreak(),

        h('3. Что дадут три инструмента', 'title'),
        h('Заказ из диалога · 1 000 подходящих сообществ', 'heading'),
        h('Измеряем повторный ввод и время до подтверждения для бизнеса, валидные заказы по всем входам для VK. '
          'В сценарии за 28 дней число заказов = размер группы × доля с заказом × среднее число заказов '
          'у продающих сообществ. Контроль и эффект заданы для расчёта чувствительности.'),
        table(model_rows, [109, 66, 120, 59, 153]),
        Spacer(1, 9),
        h('Подсказка товарной публикации · другая группа из 1 000 сообществ', 'heading'),
        h('Продавец показывает товар в привычном посте. Для бизнеса измеряем товарные публикации и открытия, '
          'для VK — заказы всех входов. Условный прирост заказов = дополнительные магазины, выпустившие шопс, '
          '× дополнительные заказы на каждый такой магазин. На пилоте сравниваем все назначенные магазины.'),
        table(post_rows, [106, 123, 131, 147]),
        Spacer(1, 9),
        h('Подключение чекаута · резервный тест', 'heading'),
        h(f"В срезе {number(o['without_checkout_active_openings'])} сообществ с активными товарами и открытиями "
          "не имеют флага чекаута. Для теста сверяем актуальную настройку и живые вопросы о покупке. "
          f"Продавцу нужен один готовый к покупке товар. Новое подключение — первый работающий чекаут для "
          f"собственного товара. При росте доли подключений на {number(connection['checkout_rate_lift']*100)} п. п. "
          f"на {connection['reference_communities']} приглашённых будет на {connection['additional_connected']} "
          f"подключений больше. При {percent(connection['order_share_among_incremental_connections'])} "
          f"с первым заказом среди дополнительных подключений это +{connection['additional_with_order']} "
          "магазина с заказом. Все значения условны. Подключение и первый заказ учитываем раздельно."),
        h('Использование черновика, первая товарная публикация, новое подключение чекаута и заказ — '
          'отдельные события. Показатели разных тестов относятся к своим группам и периодам.'),
        PageBreak(),

        h('4. Экономика и условия окупаемости', 'title'),
        h('Экономика одного исполненного заказа', 'heading'),
        h(f"При чеке {number(m['aov_rub'])} ₽, валовой марже {percent(m['seller_gross_margin'])} и "
          f"{number(m['seller_handling_rub'])} ₽ на комплектацию и выдачу продавец сохраняет "
          f"{number(m['seller_contribution'])} ₽ до труда, налогов и постоянных затрат. С условной комиссией "
          f"{percent(m['fee_rate'])} — {number(m['seller_contribution_with_service'])} ₽. "
          f"VK получает {number(m['net_per_paid_order'])} ₽ с исполненной покупки через добровольный сервис "
          f"после эквайринга {percent(m['acquiring_rate'])} и {number(m['paid_order_cost_rub'])} ₽ переменных "
          f"расходов. Доля исполнения — {percent(m['fulfillment'])}. Обработка каждого оформления — "
          f"{number(m['booked_order_cost_rub'])} ₽."),
        h('Требуемый объём первого года', 'heading'),
        h(f"Разработка и запуск {number(m['development_rub'])} ₽, включая бюджет прототипа, плюс "
          f"поддержка {number(m['monthly_support_rub'])} ₽ × 12 дают {number(m['year_cost'])} ₽. "
          f"После разгона остаётся {m['active_months']} активных месяцев. Результат = оформления в месяц × "
          "активные месяцы × вклад с оформления − затраты первого года."),
        table(payback_rows, [174, 95, 85, 153]),
        Spacer(1, 9),
        h(f"При {example_volume} оформлениях в месяц и базовой доле сервиса валовой сбор за первый год "
          f"составит {number(m['example_year_gross_fee'] / 1_000_000, 1)} млн ₽. Результат после всех "
          f"модельных затрат — {number(m['example_year_result'] / 1_000_000, 1)} млн ₽."),
        h(scale_text),
        h('Пилот бесплатный. Отдельно измеряем спрос на добровольный сервис сверки оплат и возвратов по номеру '
          f"заказа и стоимость поддержки. В синтетике в VK отмечено {percent(traffic['paid_in_vk']/traffic['orders'], 1)} "
          "оплат от оформлений. Гипотеза о доле "
          'платного сервиса относится к исполненным заказам и требует отдельного теста. Рекламный вклад '
          'считаем после проверки прироста и перетока из других кампаний VK.'),
        PageBreak(),

        h('5. План проверки и решение о запуске', 'title'),
        h('Дни 1–14. Проверяем барьер', 'heading'),
        h(f"До {number(p['budget_rub']['research'])} ₽ на проверку пути в текущем кабинете, 8 интервью "
          "с продавцами и 5 проверок оформления. С согласия продавца разбираем недавние вопросы о товаре, "
          "повторный ввод и способ фиксации оплаты и выдачи."),
        h('Дни 15–34. Проверяем прототип', 'heading'),
        h(f"До {number(p['budget_rub']['prototype'])} ₽ на прототип, "
          f"{number(p['budget_rub']['events_and_qa'])} ₽ на события и проверку. На 30 продавцах проверяем "
          "работоспособность, отсутствие дублей и сохранение согласованных условий. Подсказку товарного "
          "поста можно проверить независимо с имеющимся прикреплением товара. Бюджет A/B оцениваем отдельно."),
        h('Дни 35–90. Сравниваем с контролем при достаточной базе', 'heading'),
        h('Для каждой когорты — отдельное сравнение штатного пути и предложенного инструмента. '
          'Правила показа и продвижения одинаковы внутри сравнения. При совпадении критериев начинаем с теста '
          'заказа из чата. Один владелец участвует в одном сравнении и получает один вариант. Назначения '
          'стратифицированы по тематике и прошлой активности. В расчёте все назначенные '
          f"сообщества за {p['observation_days']} дней, с дозреванием статусов ещё {p['followup_days']} дней."),
        h('События — назначение, приглашение, добавление товара или черновик, открытие, подтверждение, '
          'выдача, отмена, возврат. Первичная метрика — уникальные валидные оформления собственных продавцов '
          'VK на назначенное сообщество по всем точкам входа. Панель продавцов с согласием до назначения '
          'сравнивает исполненные продажи во всех каналах. Отдельно отмечаем пропуски в панели и перенос из чата.'),
        h(f"Порог на 1 000 сообществ — +{p['orders_per_1000_gate']} заказов для чата и "
          f"+{p['post_orders_per_1000_gate']} для подсказки шопса, с нижней границей 95%-го интервала выше нуля. "
          f"Исполнения на сообщество сохраняются, предел роста отмен +{p['cancel_margin_pp']} п. п., жалоб "
          f"+{number(p['complaint_margin_pp'], 1)} п. п. Отслеживаем верхние границы и дубли. "
          "Для расширения проверяем продажи во всех каналах и вклад VK."),
        h('Ориентир размера A/B', 'heading'),
        h('На вариант, запас 10%. Для обнаружения эффекта при двустороннем уровне 5% и мощности 80% '
          'n ≈ 2 × (1,96 + 0,84)² × дисперсия / эффект² до запаса.'),
        table(sample_rows, [165, 171, 171]),
        Spacer(1, 7),
        h(f"Качество может требовать большей базы. При отменах 10% и жалобах 1% для выбранных порогов "
          f"ориентиры — {number(p['quality_sample'][0]['orders_per_arm_with_reserve'])} и "
          f"{number(p['quality_sample'][1]['orders_per_arm_with_reserve'])} оформлений на вариант. "
          "Это односторонний уровень 5%, мощность 80% и запас 10%. Размер фиксируем по живым данным и "
          "кластеризации до запуска. При малой базе этап проверяет использование и стабильность, "
          "решение о расширении ждёт достаточного наблюдения."),
        source('Бриф VK Case Champ · критерии, с. 7–9, и задача, с. 20', f'{SYNTHETIC}/case-brief.pdf'),
    ]


def register_fonts():
    pdfmetrics.registerFont(TTFont('GolosCase', str(ASSETS / 'GolosText-Regular.ttf')))
    pdfmetrics.registerFont(TTFont('GolosCaseBold', str(ASSETS / 'GolosText-Bold.ttf')))


def write_supporting_pdfs(destination, team, evidence, disclosure):
    rl_config.invariant = True
    write_pdf(destination / f'{team}_AI_disclosure.pdf', 'Использование ИИ', team, disclosure_story(disclosure))
    story = evidence_story(evidence)
    story.extend([PageBreak(), *disclosure_story(disclosure, 'heading')])
    write_pdf(destination / f'{team}_evidence.pdf', 'VK Заказ рядом — аналитический отчёт', team, story)
