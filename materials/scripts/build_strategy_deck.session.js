// Execute through artifactSession.run in the presentation editor.
// Charts, table, text and interface sketches are editable. The cover photo is embedded.
async function buildStrategyDeck(p, evidence, cover) {
  const model = evidence.projection;
  const { low, base, high } = model.scenarios;
  const pilot = evidence.pilot;
  const number = (value, digits = 0) => new Intl.NumberFormat('ru-RU', {
    minimumFractionDigits: digits, maximumFractionDigits: digits
  }).format(value);
  const pct = (fraction, digits = 0) => number(fraction * 100, digits) + '%';
  const team = 'Теневое Правительство';
  const C = {
    blue: '#0077FF', textBlue: '#0063D6', ink: '#142438', gray: '#52657A', pale: '#F2F6FB',
    line: '#DCE5EF', white: '#FFFFFF', navy: '#092749', light: '#D9E9FF', softBlue: '#E9F2FF',
  };

  if (p.slides.items.length) p.slides.delete(p.slides.items.map((_, i) => i));

  function rect(s, left, top, width, height, fill, radius = 0, stroke = 'none') {
    return s.shapes.add({
      geometry: radius ? 'roundRect' : 'rect',
      position: { left, top, width, height },
      fill,
      line: { fill: stroke, width: stroke === 'none' ? 0 : 1, style: 'solid' },
      ...(radius ? { borderRadius: radius } : {}),
    });
  }

  function txt(s, text, x, y, w, h, size = 26, color = C.ink, bold = false, align = 'left') {
    const shape = rect(s, x, y, w, h, 'none');
    shape.text = text;
    shape.text.style = { fontSize: size, color, bold, alignment: align, verticalAlignment: 'middle' };
    shape.text.typeface = 'Arial';
    return shape;
  }

  function rule(s, y, x = 64, w = 1152, color = C.line) {
    rect(s, x, y, w, 1, color);
  }

  function slide(n, section, title, bg = C.white) {
    const s = p.slides.add();
    s.size = { width: 1280, height: 720 };
    s.background.fill = bg;
    const dark = bg === C.navy;
    const chrome = dark ? C.light : C.gray;
    txt(s, 'VK CASE CHAMP 2026', 64, 28, 420, 28, 16, chrome, true);
    txt(s, section.toUpperCase(), 720, 28, 496, 28, 15, chrome, false, 'right');
    if (title) txt(s, title, 64, 77, 1152, 114, 44, dark ? C.white : C.ink, true);
    rule(s, 670, 64, 1152, dark ? '#426389' : C.line);
    txt(s, team, 64, 679, 680, 23, 14, chrome);
    txt(s, String(n).padStart(2, '0') + ' / 08', 1090, 679, 126, 23, 14, chrome, false, 'right');
    return s;
  }

  function note(s, text) {
    s.speakerNotes.text = text;
  }

  function button(s, label, x, y, w) {
    rect(s, x, y, w, 40, C.blue, 9);
    txt(s, label, x + 8, y + 2, w - 16, 36, 18, C.white, true, 'center');
  }

  function phone(s, x, title) {
    rect(s, x, 260, 366, 289, C.pale, 20, C.line);
    rect(s, x + 7, 267, 352, 275, C.white, 16);
    txt(s, title, x + 24, 272, 318, 44, 22, C.ink, true);
    rule(s, 321, x + 24, 318);
  }

  function chart(s, position, categories, values, options) {
    const colors = ['#AEC9EE', '#6EA9F4', C.blue];
    return s.charts.add('bar', {
      position,
      categories,
      series: [{
        name: options.name,
        values: values.map(v => Number(v.toPrecision(10))),
        fill: C.blue,
        points: values.map((_, i) => ({ idx: i, fill: colors[i] })),
      }],
      barOptions: { direction: 'column', grouping: 'clustered', gapWidth: 125 },
      hasLegend: false,
      chartFill: 'none',
      plotAreaFill: 'none',
      chartLine: { fill: 'none', width: 0 },
      plotAreaLine: { fill: 'none', width: 0 },
      xAxis: {
        visible: true, tickLabelPosition: 'low', majorGridlines: null,
        line: { fill: C.line, width: 1 },
        textStyle: { fontSize: 18, typeface: 'Arial', fill: C.gray },
      },
      yAxis: {
        visible: false, line: { fill: 'none', width: 0 }, majorGridlines: null,
        min: 0, max: options.max, numberFormatCode: options.format,
      },
      dataLabels: {
        showValue: true, position: 'outEnd', numberFormatCode: options.format,
        textStyle: { fontSize: 24, bold: true, typeface: 'Arial', fill: C.ink },
      },
    });
  }

  let s = slide(1, 'Социальная коммерция', '', C.navy);
  txt(s, 'VK Заказ\nрядом', 64, 120, 643, 248, 100, C.white, true);
  txt(s, 'Покупка у малого бизнеса\nиз шопса или переписки', 69, 386, 610, 105, 34, C.light);
  txt(s, 'Стратегия для ВКонтакте\nМосква · Ноябрь 2026', 69, 542, 560, 62, 20, C.light);
  s.images.add({
    blob: cover, contentType: 'image/png', alt: 'Иллюстрация синей керамической чашки',
    fit: 'cover', geometry: 'roundRect', borderRadius: 21,
    position: { left: 718, top: 83, width: 498, height: 556 },
  });
  rect(s, 752, 508, 430, 103, C.white, 16);
  txt(s, 'Заказ № 104 оформлен', 773, 517, 390, 42, 27, C.ink, true);
  txt(s, 'Синяя чашка · 2 000 ₽ · Самовывоз', 773, 563, 390, 25, 19, C.gray);
  note(s, 'Концепция «VK Заказ рядом». Цель кейса — увеличить число бизнесов, продающих внутри ВКонтакте. Заказы собственных продавцов — основной ориентир, подключение инструментов — дополнительный. Иллюстрация чашки создана с помощью ImageGen, магазин и заказ вымышлены. Источники: бриф, с. 20; Q&A, 13:31, 22:56, 45:02. https://vkvideo.ru/video-92204627_456240708');

  s = slide(2, 'Команда', team);
  txt(s, 'Москва', 64, 201, 1000, 63, 40, C.textBlue, true);
  const names = ['Якунченков Кирилл', 'Македонский Александр', 'Графов Григорий', 'Гурцев Владимир'];
  names.forEach((name, i) => {
    const x = i % 2 === 0 ? 64 : 656;
    const y = i < 2 ? 352 : 490;
    rule(s, y, x, 552);
    txt(s, name, x, y + 18, 552, 61, 32, C.ink, true);
  });
  note(s, 'Город очной защиты — Москва. Название команды и состав предоставлены участником.');

  s = slide(3, 'Резюме решения', 'Покупатель подтверждает заказ\nв переписке с магазином');
  rect(s, 64, 222, 470, 404, C.navy, 21);
  txt(s, number(evidence.warm_at_least_10_opens), 91, 247, 400, 112, 99, C.white, true);
  txt(s, 'сообществ с каталогом\nи чекаутом получили\n≥10 открытий из контента\nи 0 заказов за месяц', 95, 367, 410, 143, 27, C.white, true);
  rule(s, 537, 95, 408, '#426389');
  txt(s, 'Синтетический датасет VK Case Champ\nЛист «Бизнесы» · порог для отбора', 95, 551, 415, 59, 17, C.light);
  const summary = [
    ['Кого подключаем', 'Мастерские и малые магазины с товарами\nв наличии и вопросами о покупке в чате.'],
    ['Что меняется', 'Продавец отправляет черновик из каталога.\nПокупатель подтверждает условия в VK.'],
    ['Зачем VK', 'Больше сообществ с заказами. Магазин VK\nведёт заказы, Маркет помогает найти товар.'],
  ];
  summary.forEach(([label, body], i) => {
    const y = 230 + 132 * i;
    txt(s, label, 578, y, 637, 35, 24, C.textBlue, true);
    txt(s, body, 578, y + 42, 637, 74, 25, C.ink);
    if (i < 2) rule(s, y + 122, 578, 638);
  });
  note(s, `В листе «Бизнесы» критерий «товарное или смешанное, активный каталог, чекаут, ≥1 открытия из контента, 0 заказов» даёт ${number(evidence.warm_zero_orders)} сообщества. Порог ≥10 открытий выделяет ${number(evidence.warm_at_least_10_opens)} сообществ и концентрирует ${pct(evidence.strict_opening_share, 1)} открытий этой группы. Это способ найти кандидатов для изучения, причину отсутствия заказов проверяем в живых диалогах с согласия продавцов. Начинаем с мастерских и магазинов изделий, у которых покупатели спрашивают о варианте, наличии и самовывозе. Первый пилот тестирует передачу согласованных условий из переписки в штатный заказ. Вход из шопса сохраняет существующую карточку и доступ к сообщениям.`);

  s = slide(4, 'Данные и сегмент', 'Заказы чаще есть там,\nгде открывают карточки');
  txt(s, 'Сообщества с ≥1 заказом за месяц', 64, 220, 704, 39, 28, C.ink, true);
  txt(s, `${number(evidence.checkout_and_catalog)} сообществ с активным каталогом и чекаутом`, 64, 266, 706, 32, 20, C.gray);
  const cohorts = evidence.cohort_stats;
  chart(s, { left: 61, top: 305, width: 690, height: 262 },
    cohorts.map(c => `${c.openings}  (n = ${number(c.communities)})`),
    cohorts.map(c => c.selling_rate),
    { format: '0.0%', max: 0.58, name: 'Доля сообществ с заказом' });
  txt(s, 'Открытия карточек из контента на сообщество', 68, 581, 680, 30, 20, C.gray);
  txt(s, 'Синтетические данные за месяц. Причину различий проверяем в пилоте.', 64, 625, 1152, 33, 17, C.gray);
  rect(s, 787, 221, 429, 388, C.pale, 20);
  txt(s, pct(evidence.strict_opening_share), 816, 247, 365, 80, 68, C.textBlue, true);
  txt(s, `открытий приходится на ${number(evidence.warm_at_least_10_opens)}\nиз ${number(evidence.warm_zero_orders)} сообществ с открытиями\nи без заказов`, 821, 332, 368, 104, 22, C.ink);
  rule(s, 452, 821, 363);
  txt(s, `${number(evidence.ready_zero_orders_zero_content_opens)} без открытий и заказов.\nДля них отдельно проверяем,\nкак привлечь покупателей.`, 821, 473, 368, 101, 22, C.gray);
  note(s, `Лист «Бизнесы». Всего ${number(evidence.goods_communities)} товарных и смешанных сообществ, чекаут подключён у ${number(evidence.checkout_enabled)} (${number(evidence.checkout_pct, 1)}%), за месяц ≥1 заказа у ${number(evidence.selling_in_month)} (${number(evidence.selling_pct, 1)}%). В подгруппе с каталогом и чекаутом от ${cohorts[0].selling} бизнесов с заказами карточки из контента не открывали. Учитываются только открытия из контента, а чекаут — на конец месяца. Отличия могут объясняться другими источниками заказов, размером магазина и ассортиментом. В дополнении есть чувствительность порога и карта источников открытий. Сначала проверяем спрос и путь отдельного заказа, затем эффект интерфейса.`);

  s = slide(5, 'Альтернативы', 'Маркет помогает найти товар,\nа Магазин VK ведёт заказы');
  txt(s, 'Ozon обслуживает спрос на маркетплейсе, Авито — поиск по объявлениям.\nVK помогает купить у бизнеса, которого нашли по контенту или знают по сообществу.', 64, 198, 1152, 66, 23, C.gray);
  const values = [
    ['Критерий', 'Главная Маркета', 'Партнёрский маршрут', 'Заказ в сообществе'],
    ['Откуда спрос', 'Поиск покупателя\nв каталоге', 'Контент с товарами\nпартнёра', 'Подписка, шопс\nи диалог'],
    ['Что развиваем', 'Поиск, ранжирование\nи повторные визиты', 'Ассортимент и переход\nна чекаут партнёра', 'Согласованные условия\nв штатном заказе'],
    ['Чей заказ', 'Собственный\nпродавец VK', 'Партнёр. Отдельный\nпоказатель', 'Собственный\nпродавец VK'],
    ['Приоритет', 'Сохраняем поиск.\nГлавная — отдельный тест', 'Сохраняем\nпартнёрские продажи', 'Первый пилот'],
  ];
  const table = s.tables.add({
    rows: 5, columns: 4, left: 64, top: 277, width: 1152, height: 298,
    columnWidths: [198, 318, 318, 318], values,
  });
  table.borders.assign({ fill: C.white, width: 3, style: 'solid' });
  for (let row = 0; row < 5; row++) {
    for (let column = 0; column < 4; column++) {
      const cell = table.getCell(row, column);
      cell.fill = row === 0 ? (column === 3 ? C.blue : C.navy) : (column === 3 ? C.softBlue : C.pale);
      cell.text.style = {
        fontSize: row === 0 ? 20 : 19, bold: row === 0 || column === 0 || row === 4,
        color: row === 0 ? C.white : C.ink, verticalAlignment: 'middle',
      };
      cell.text.typeface = 'Arial';
    }
  }
  txt(s, 'Витрины дают 39,1% открытий карточек, главная — 0,2%. Её вклад проверим по заказам.\nProdamus уже отправляет счета в чат. Проверяем черновик заказа Магазина VK из переписки.\nWeixin Mini Shops связывает контент, общение и чекаут. Источники — в отчёте.', 64, 588, 1152, 74, 18, C.ink);
  note(s, 'Сравниваем по источнику спроса, затратам на развитие и связи с метрикой кейса. Витрины сообществ дают 39,1% известных открытий, лента и клипы 18,6%, главная Маркета 0,2%, «Другое» 40,2%, поиск 1,9%. Проценты описывают доли от всех 193,5 млн открытий собственных карточек. Доля заказов по поверхностям неизвестна. Главную тестируем по общим дополнительным заказам при сопоставимом бюджете. Ozon получает заказы через Ozon Seller. Prodamus уже отправляет состав покупки и счёт в переписку; отдельно принимает оплату по заказу, который уже оформлен в VK. Источники: https://prodamus.ru/blog/kak-prinimat-platezhi-iz-vkontakte-s-pomoschyu-prodamus и https://seller.ozon.ru/media/boost/kak-rabotaet-integraciya-ozon-i-vkontakte/. Weixin связывает витрины, контент и общение; его результаты на VK не экстраполируем. Сначала сверяем возможности кабинета продавца и доступность предзаполнения.');

  s = slide(6, 'Путь бизнеса и покупателя', 'От первого шопса до выдачи заказа');
  const x = [64, 457, 850];
  ['Продавец готовит товар', 'Продавец отвечает в чате', 'Покупатель подтверждает'].forEach((label, i) => {
    txt(s, label, x[i], 202, 364, 39, 23, C.textBlue, true);
  });
  phone(s, x[0], 'Магазин сообщества');
  txt(s, 'Синяя чашка · 2 000 ₽\nВ наличии: 1 шт.\nСамовывоз в мастерской', 87, 338, 319, 101, 22, C.ink);
  button(s, 'Опубликовать шопс', 87, 479, 320);

  phone(s, x[1], 'Керамика Лето');
  rect(s, 480, 339, 268, 41, C.softBlue, 10);
  txt(s, 'Есть синяя? Заберу завтра.', 488, 342, 257, 34, 17, C.ink);
  txt(s, 'Черновик из каталога', 480, 397, 320, 32, 21, C.ink, true);
  txt(s, 'Синяя чашка · 2 000 ₽', 480, 434, 320, 29, 18, C.gray);
  button(s, 'Отправить покупателю', 480, 479, 320);

  phone(s, x[2], 'Проверьте условия');
  txt(s, 'Синяя чашка · 2 000 ₽\nСамовывоз завтра\nОплата при получении', 873, 338, 319, 101, 22, C.ink);
  button(s, 'Подтвердить заказ', 873, 479, 320);

  txt(s, 'Из шопса можно сразу открыть чекаут. Если есть вопрос, продавец присылает черновик.\nПосле подтверждения заказ № 104 появляется в чате. Там же покупатель видит «Готов к выдаче».\nДля магазинов без обращений отдельно тестируем шаблоны шопсов и продвижение.', 64, 561, 1152, 95, 19, C.gray);
  note(s, '1. VK приглашает подходящие сообщества в кабинете магазина. Продавец сверяет остаток и условия, публикует шопс по шаблону с одним прикреплённым товаром. 2. Если покупателя устраивает карточка, работает штатный чекаут, товара достаточно для прямого оформления. Если есть вопрос, продавец выбирает товар и вариант, указывает количество, время и способ получения и посылает черновик из переписки. 3. При подтверждении сервер ещё раз проверяет цену и наличие, создаёт один штатный заказ и возвращает номер. Продавец готовит и выдаёт товар, покупатель видит изменения в чате и заказах. Самовывоз с оплатой при получении — первый вариант, другие способы зависят от настроек и статуса продавца. Если условия изменились, покупателю показываем новый вариант для подтверждения. Это макеты. Порядок кнопок и число действий проверяем в живом интерфейсе.');

  s = slide(7, 'Обоснование и экономика', 'Сначала проверяем прирост заказов');
  txt(s, `Дополнительные заказы за 30 дней\nна ${number(model.reference_invited_communities)} приглашённых сообществ`, 64, 199, 626, 83, 28, C.ink, true);
  const orders = [low, base, high].map(v => v.monthly_orders_per_reference_invites);
  chart(s, { left: 62, top: 291, width: 628, height: 254 },
    ['Осторожный', 'Базовый', 'Верхний'], orders,
    { format: '0', max: Math.max(...orders) * 1.19, name: 'Дополнительные заказы' });
  txt(s, `База: ${pct(base.adoption)} подключатся × ${number(base.orders_per_adopter, 2)} заказа\nна подключившегося = +${number(base.monthly_orders_per_reference_invites)} на ${number(model.reference_invited_communities)} приглашённых.`, 64, 559, 627, 72, 20, C.gray);
  rect(s, 730, 206, 486, 428, C.pale, 20);
  txt(s, 'Что получает бизнес', 760, 229, 424, 43, 26, C.ink, true);
  txt(s, `В базе +${number(base.monthly_selling_per_reference_invites)} сообществ с заказом\nи ≈${number(base.monthly_net_merchant_sales_per_reference_invites)} новых исполненных продаж.\nПример вклада продавца — ${number(model.seller_contribution_per_completed_order_without_service_rub)} ₽\nс исполненного заказа на ${number(model.economics.aov_rub)} ₽.`, 760, 287, 423, 132, 21, C.ink);
  rule(s, 438, 760, 424);
  txt(s, 'Условие окупаемости для VK', 760, 457, 424, 40, 26, C.ink, true);
  const payback = base.monthly_order_hurdle === null
    ? 'Покрытие затрат требует вклада\nиз других источников.'
    : `Комиссия окупит проект от ${number(base.monthly_order_hurdle / 1000, 1)} тыс.\nдоп. заказов в месяц. В сценарии\nна ${number(model.reference_goods_communities / 1000)} тыс. сообществ — ${number(base.monthly_incremental_orders_at_scale)} в месяц.`;
  txt(s, payback, 760, 514, 424, 95, 21, C.ink);
  txt(s, 'Все прогнозные числа — допущения модели. Формулы и чувствительность — в отчёте.', 64, 641, 1152, 24, 16, C.gray);
  note(s, `Сценарии на ${number(model.reference_invited_communities)} случайно выбранных подходящих сообществ, которым предложат инструмент. База: 30% подключатся, 0,25 дополнительного заказа на активировавшее сообщество. +30 с заказом — допущение о приросте доли с заказом на 10 п. п. среди активировавших. ≈34 новые исполненные продажи — 75 × 75% исполнения × 60% продаж сверх привычных каналов. Проверяем последнюю долю по продажам во всех каналах на подвыборке. У продавца 2 000 × 35% − 100 = 600 ₽ до труда, налогов и постоянных затрат, или 540 ₽ с условной комиссией 3%. Вклад VK 30 ₽ на исполненный заказ с платным сервисом; при доле 15% от всех дополнительных заказов — 4,5 ₽ в среднем. При 2,4 млн ₽ разработки и 150 тыс. ₽ поддержки в месяц порог 77,8 тыс. дополнительных заказов в месяц. 100 000 сообществ — условная база: 210 заказов в месяц с широким фильтром или 35 со строгим. Истинный охват, расходы, доход от рекламы и перенос заказов требуют данных пилота.`);

  s = slide(8, 'Решение и пилот', `${number(pilot.pre_experiment_budget_rub / 1000)} тыс. ₽ на исследование и прототип`, C.navy);
  txt(s, 'План на 90 дней. Запуск A/B-теста зависит от результатов прототипа и доступной базы.', 64, 173, 1152, 42, 21, C.light);
  const phases = [
    ['Дни 1–14', 'Проверяем барьер', '8 интервью и 5 тестов.\nСверяем, как сейчас\nоформляют заказ из чата.'],
    ['Дни 15–40', 'Проверяем прототип', '30 продавцов.\nОстатки, подтверждение,\nвыдача и нагрузка поддержки.'],
    ['Дни 41–90', 'Измеряем эффект', 'При достаточной выборке —\nA/B по продавцам, 30 дней\nи ещё 14 дней на статусы.'],
  ];
  phases.forEach(([when, label, body], i) => {
    const left = 64 + i * 393;
    txt(s, when, left, 238, 359, 45, 25, C.light, true);
    txt(s, label, left, 292, 359, 43, 26, C.white, true);
    txt(s, body, left, 343, 359, 106, 21, C.light);
  });
  rule(s, 470, 64, 1152, '#426389');
  txt(s, `+${number(pilot.minimum_orders_per_invited * model.reference_invited_communities)} заказов на ${number(model.reference_invited_communities)} приглашённых`, 64, 493, 1152, 57, 37, C.white, true);
  txt(s, 'Порог для продолжения. Проверяем достоверность прироста, выдачу, отмены и перенос продаж.\nВыход на масштаб зависит от вклада для VK после затрат.', 64, 557, 1152, 58, 21, C.light);
  txt(s, 'ИИ: Claude и ChatGPT/Codex — анализ и материалы, Whisper — расшифровка, ImageGen — обложка. Расчёты сверены с XLSX.', 64, 635, 1152, 28, 15, C.light);
  note(s, `До дня 40 бюджетный лимит ${number(pilot.pre_experiment_budget_rub)} ₽: ${number(pilot.research_rub)} исследование, ${number(pilot.prototype_rub)} прототип, ${number(pilot.instrumentation_and_qa_rub)} аналитика событий и QA. Это предложение, расходы и интервью ещё предстоят. При запуске держим дистрибуцию одинаковой, назначаем один вариант на владельца, учитываем все назначенные сообщества. Цель — не менее +0,075 валидного оформленного заказа на сообщество за 30 дней при нижней границе 95%-го интервала выше нуля. Оцениваем исполнение до 14-го дня после окна, отмены, жалобы, дубли и вклад после затрат. Размер теста по живой дисперсии и числу независимых продавцов. Иллюстрация при дисперсии 0,50 — примерно ${number(pilot.sample_sizes[1].per_arm_with_reserve)} в группу с резервом до поправок на кластеризацию. Данные A/B и модель помогают принять решение о следующем этапе, а не дают заранее оценку реального эффекта. Полный отчёт об использовании ИИ в аналитическом приложении.`);
  return { slides: p.slides.items.length };
}
// Live editor entry point.
const fs = await import('node:fs/promises');
const evidence = JSON.parse(await fs.readFile('materials/presentation/evidence.json', 'utf8'));
const cover = await fs.readFile('materials/presentation/ceramic-cover.png');
await artifactSession.run(async ({ presentation, session }) => {
  nodeRepl.write(await buildStrategyDeck(presentation, evidence, Uint8Array.from(cover).buffer));
  nodeRepl.write({ sessionId: session.sessionId });
}, { artifactType: 'presentation', artifactRef: 'artifact_hDtOzhxchhgyKGHdSiET6ervTH0Fuzvk' });
