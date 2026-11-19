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
    return f"{value:,.{digits}f}".replace(",", " ").replace(".", ",")


def paragraph(text, role="body"):
    sizes = {"title": (23, 29, 13), "heading": (14, 20, 5), "body": (11, 15, 9),
             "cell": (10, 13, 0), "table_head": (10, 13, 0)}
    size, leading, gap = sizes[role]
    return Paragraph(text.replace("₽.", "руб.").replace("₽", "руб."), ParagraphStyle(
        role, fontName="CaseArial" if role in {"body", "cell"} else "CaseArialBold",
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
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return result


def source(label, url):
    return paragraph(f'<link href="{escape(url, quote=True)}" color="#005EC8"><u>{escape(label)}</u></link>')


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


def evidence_appendix(evidence):
    model = evidence["projection"]
    base = model["scenarios"]["base"]
    build = model["economics"]
    eligible = number(model["eligible"])
    opened = evidence["ready_with_content_opens"]
    sold = evidence["ready_with_content_opens_and_orders"]
    head = paragraph
    rows = [["На 100 тыс. сообществ", "Осторожный", "Базовый", "Верхний"]]
    scenarios = list(model["scenarios"].values())
    for label, key, digits, is_rate in [
        ("Охват подходящих", "reach", 0, True),
        ("Подключение среди охваченных", "adoption", 0, True),
        ("Прирост заказов на участника", "orders_per_adopter", 2, False),
        ("Прирост доли с заказом у участников", "seller_rate_lift", 0, True),
        ("Исполненные через платный сервис", "paid_share", 0, True),
        ("Заказы в месяц на масштабе", "monthly_incremental_orders_at_scale", 0, False),
        ("Бизнесы с заказом в месяц", "monthly_incremental_selling_communities_at_scale", 0, False),
        ("Заказы за первый год", "year_one_orders", 0, False),
        ("Валовая комиссия VK в месяц, ₽", "monthly_vk_fee_revenue_rub_at_scale", 0, False),
        ("Денежный результат VK за год, млн ₽", "year_one_vk_cash_flow_rub", 2, False),
    ]:
        values = [
            number(s[key] * 100) + "%" if is_rate else
            number(s[key] / 1_000_000, digits) if key.endswith("cash_flow_rub") else number(s[key], digits)
            for s in scenarios
        ]
        if key == "seller_rate_lift":
            values = [value.replace("%", " п. п.") for value in values]
        rows.append([label, *values])

    document("evidence", "VK Заказ рядом — доказательства и расчёты", [
        head("Доказательства и расчёты", "title"),
        head("Слайды 3–4. Датасет и выбор продавцов", "heading"),
        head("Единица анализа — сообщество. Для товарных и смешанных бизнесов получаем 4 158 строк по столбцу C листа «Бизнесы». Чекаут установлен у 3 826 по R, активный каталог и чекаут есть у 3 637 по Q и R, заказ за месяц есть у 285 по W. Флаги инструментов описывают конец месяца."),
        head("Стартовая группа — Q &gt; 0, R = 1, O &gt; 0, W = 0. Это 233 сообщества с медианой в два открытия из контента. При O ≥ 10 остаётся 39. Ещё 3 126 с активным каталогом и чекаутом имеют O = 0 и W = 0. Открытия учитываются только из контента. Для теста оформления дополнительно проверяем входящие вопросы о товаре и наличие товара."),
        head(f"Среди {number(opened)} сообществ с каталогом, чекаутом и открытиями заказы есть у {number(sold)} ({number(100*sold/opened,1)}%). Эта доля описывает совпадение признаков за месяц. Для выявления барьера нужно проследить отдельные переходы и проверить сценарий оформления."),
        head("Карточки собственных продавцов открывали 193 512 461 раз. Витрины магазинов — 39,1%, лента и клипы — 18,6%, главная Маркета — 0,2%, поиск — 1,9%, «Другое» — 40,2%. Доли отражают открытия карточек. Данные о заказах по этим источникам отсутствуют."),
        source("Датасет VK Case Champ, листы «Бизнесы», «Итоги» и «Источники»", f"{REPO}/sources/dataset.xlsx"),
        head("Слайды 4–5. Что уточнили организаторы", "heading"),
        head("Цель — оформленные заказы собственных продавцов внутри VK. Подключение инструментов отражает промежуточный шаг. Из 413 740 заказов 4 903 оплачены внутри VK. Другие заказы могут оплачиваться вне VK, их итоговый статус неизвестен. Партнёрские заказы из прямых переходов и других маршрутов учитываем отдельно."),
        source("Конспект Q&A от 16 ноября, 13:31, 22:38, 33:20, 39:40, 45:02, 49:58", f"{REPO}/docs/qa/2026-11-16_qa_summary.md"),
        head("Слайд 5. Роль Маркета и примеры платформ", "heading"),
        head("Сохраняем каталог, поиск, витрины и возврат к заказам. Для главной Маркета отдельный тест должен показать дополнительные заказы на равных затратах. В контенте VK уже работают товарные публикации и авторская программа для Ozon. В качестве гипотезы переносим путь от публикации к оформлению для собственных товаров сообществ."),
        source("VK и Ozon, официальный релиз о шопсах", "https://vk.company.ru/ru/press/releases/12431/"),
        source("Tencent, результаты III квартала 2024 года, Weixin Mini Shops", "https://static.www.tencent.com/uploads/2024/11/13/ccffd154b896b6c3e1ae65c13b73761d.pdf"),
        PageBreak(),
        head("Сценарная модель на 12 месяцев", "title"),
        head(f"100 000 — условная база товарных и смешанных сообществ. Доля подходящих по выборке — 233 / 4 158 ≈ 5,6%, или {eligible} на условную базу. При пороге десять открытий остаётся 39 / 4 158 ≈ 0,94%. Реальный доступный охват требует данных VK."),
        table(rows, [236, 91, 91, 91]),
        Spacer(1, 10),
        head("Заказы = подходящие × охват × подключение × дополнительные заказы на участника. Для бизнесов с заказом вместо заказов на участника используем прирост доли продавцов с заказом. Показатель относится к одному месяцу."),
        head("Первые три месяца — исследование и пилот. В месяцы 4–12 масштаб составляет 10%, 20%, 35%, 50%, 65%, 80%, 90%, 100% и 100% от целевого. В затратах учтены 2,4 млн ₽ разработки и 150 тыс. ₽ поддержки ежемесячно. Охват, подключение, эффект, расходы и доля платного сервиса заданы для проверки чувствительности."),
        head(f"При заказе на {number(build['aov_rub'])} ₽, марже 35% и затратах на получение 100 ₽ продавцу остаётся 600 ₽ до труда, налогов и постоянных затрат. При комиссии 3% остаётся 540 ₽. VK получает 60 ₽ комиссии, платит 20 ₽ за эквайринг и 10 ₽ переменных расходов. Вклад — 30 ₽ с исполненного заказа через платный сервис."),
        head(f"Порог на масштабе = (2,4 млн ₽ / 12 + 150 тыс. ₽) / (30 ₽ × доля заказов через сервис). При 15% это {number(base['monthly_order_hurdle'])} дополнительных заказов в месяц. В базовом сценарии комиссии недостаточно. Для покрытия разницы за первый год через рекламу нужен дополнительный чистый вклад порядка {number(base['year_one_other_contribution_needed_per_adopter_month_rub'])} ₽ на подключённый бизнес за активный месяц. Это порог для теста рекламы, а её эффект не включён в сценарий."),
        PageBreak(),
        head("Как привлечь МСБ и провести пилот", "title"),
        head("Слайд 6. От товара к заказу", "heading"),
        head("Стартуем в кабинете действующего сообщества с каталогом. VK предлагает выбрать один товар с остатком, заполнить условия получения и опубликовать шопс по шаблону обзора или демонстрации. Покупатель нажимает «Купить», проверяет предзаполненный заказ и подтверждает его. Два действия возможны при сохранённых данных и доступном варианте получения. Покупатель с вопросом получает тот же черновик из переписки."),
        head("Продавец подтверждает заказ и выдаёт или отправляет товар. Статус виден в диалоге и в заказах. Онлайн-оплата доступна по выбору продавца при поддержке его статуса. Для слабого спроса проверяем органический контент и затем ограниченное платное продвижение. Сотрудничество с авторами подключаем отдельным тестом после проверки атрибуции и экономики."),
        head("Слайд 8. Как принять решение", "heading"),
        head("Начать с 8 интервью и 5 пользовательских проверок, затем проверить прототип с 30 продавцами. Эти числа задают объём качественного и технического этапов. Размер A/B-теста определяем отдельно по дисперсии и минимальному полезному эффекту."),
        head("В группе с подтверждённым интересом сравнить текущий путь с предзаполненным заказом. В группе без сигнала интереса сравнить текущий способ работы с шаблоном шопса и тестовой дистрибуцией. Случайное назначение на уровне бизнесов, единое окно измерения в 28 дней и анализ всех назначенных бизнесов. Основная метрика — валидные оформленные заказы на бизнес, дополнительная — бизнесы с заказом."),
        head("Защита качества — отмены, жалобы, дубли, исполнение и перенос уже существующих продаж. Контролируем расходы на поддержку, доступность товара и качество товарного контента. При слабом эффекте оформления проверяем, хватает ли спроса. Бюджет расширения согласуем после положительного результата, проверки качества и подтверждения экономики."),
        head("Публичные материалы VK подтверждают наличие шопсов и работу авторской программы. Проверку действующего интерфейса продавца и интервью команда ещё не проводила. Сценарии в презентации остаются гипотезами до пилота."),
        source("VK, итоги III квартала 2026 года", "https://vk.company.ru/ru/investors/info/12477/"),
        source("Бриф VK Case Champ, страницы 7–9 и 20", f"{REPO}/sources/case-brief.pdf"),
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
    document("AI_disclosure", "Раскрытие использования ИИ", [
        paragraph("Раскрытие использования ИИ", "title"),
        *(paragraph(escape(block)) for block in disclosure.strip().split("\n\n")[1:]),
    ])
    evidence_appendix(evidence)


if __name__ == "__main__":
    main()
