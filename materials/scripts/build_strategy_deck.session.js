// Execute through artifactSession.run in the presentation editor.
// All slide content is native and editable. Sizes and fonts use CSS px.
async function buildStrategyDeck(p, evidence) {
  const projection = evidence.projection;
  const { low, base, high } = projection.scenarios;
  const number = (value, digits = 0) => new Intl.NumberFormat('ru-RU', {
    minimumFractionDigits: digits, maximumFractionDigits: digits
  }).format(value);
  const orders = (scenario) => number(scenario.monthly_incremental_orders_at_scale);
  const marketShare = (name) => evidence.traffic[name].share_pct / 100;
  if (p.slides.items.length) p.slides.delete(p.slides.items.map((_, i) => i));
  const C = { blue:'#0077FF', ink:'#142438', gray:'#66778C', pale:'#F2F6FB', line:'#DCE5EF', white:'#FFFFFF', navy:'#092749', light:'#D9E9FF', green:'#168A65' };
  function rect(s,x,y,w,h,fill,r=0,line='none') {return s.shapes.add({geometry:r?'roundRect':'rect',position:{left:x,top:y,width:w,height:h},fill,line:{fill:line,width:line==='none'?0:1,style:'solid'},...(r?{borderRadius:r}:{})});}
  function txt(s,text,x,y,w,h,size=26,color=C.ink,bold=false,align='left') { const q=rect(s,x,y,w,h,'none');q.text=text;q.text.style={fontSize:size,color,bold,alignment:align,verticalAlignment:'middle'};q.text.typeface='Arial';return q; }
  function rule(s,y,x=64,w=1152,color=C.line){rect(s,x,y,w,1,color);}
  function slide(n,section,title,bg=C.white) {const s=p.slides.add();s.size={width:1280,height:720};s.background.fill=bg;const dark=bg===C.navy||bg===C.blue;txt(s,'VK CASE CHAMP 2026',64,28,420,28,17,dark?C.light:C.gray,true);txt(s,section.toUpperCase(),750,28,466,28,16,dark?C.light:C.gray,false,'right');if(title)txt(s,title,64,86,1152,98,43,dark?C.white:C.ink,true);rule(s,666,64,1152,dark?'#426389':C.line);txt(s,'Теневое Правительство',64,677,680,22,14,dark?C.light:C.gray);txt(s,String(n).padStart(2,'0')+' / 08',1090,677,126,22,14,dark?C.light:C.gray,false,'right');return s;}
  function note(s,t){s.speakerNotes.text=t;}
  function button(s,text,x,y,w,h=40){rect(s,x,y,w,h,C.blue,10);txt(s,text,x+8,y+2,w-16,h-4,18,C.white,true,'center');}
  function phone(s,x,y,w,h,title){rect(s,x,y,w,h,C.pale,24,C.line);rect(s,x+8,y+8,w-16,h-16,C.white,20);rect(s,x+108,y+14,w-216,5,C.line,2);txt(s,title,x+22,y+32,w-44,32,22,C.ink,true);rule(s,y+78,x+20,w-40);}
  function chart(s,position,categories,values,opts={}){
    values=values.map(v=>Number(v.toPrecision(10))); // portable Excel precision; notes retain formulas
    return s.charts.add('bar',{position,categories,series:[{name:opts.name||'Значение',values,fill:C.blue,points:values.map((_,i)=>({idx:i,fill:(opts.colors||[])[i]||C.blue}))}],barOptions:{direction:opts.direction||'bar',grouping:'clustered',gapWidth:opts.gapWidth||80},hasLegend:false,chartFill:'none',plotAreaFill:'none',chartLine:{fill:'none',width:0},plotAreaLine:{fill:'none',width:0},xAxis:{visible:true,tickLabelPosition:'low',majorGridlines:null,line:{fill:'none',width:0},textStyle:{fontSize:18,typeface:'Arial',fill:C.gray}},yAxis:{visible:false,textStyle:{fontSize:21,typeface:'Arial',fill:C.ink},line:{fill:'none',width:0},majorGridlines:null,min:0,max:opts.max,numberFormatCode:opts.format||'0.0'},dataLabels:{showValue:true,position:'outEnd',numberFormatCode:opts.format||'0.0',textStyle:{fontSize:24,bold:true,typeface:'Arial',fill:C.ink}}});
  }
  let s=slide(1,'Стратегия социальной коммерции','',C.blue);
  txt(s,'VK Заказ\nрядом',64,156,720,214,88,C.white,true);
  txt(s,'Оформление покупки\nв привычном общении с бизнесом',68,399,650,96,31,C.white);
  txt(s,'Концепция для собственных продавцов VK',68,579,710,34,21,C.light);
  // Editable order card: an interface concept, not a screenshot of an existing product.
  rect(s,858,168,358,410,C.white,24);
  txt(s,'КЕРАМИКА ЛЕТО',886,192,300,28,15,C.gray,true);
  txt(s,'Заказ № 104',886,241,302,46,34,C.ink,true);
  txt(s,'Чашка ручной работы\n1 шт. · 2 000 ₽',886,316,300,72,25,C.ink);
  rule(s,411,886,302);
  txt(s,'Самовывоз\nОплата при получении',886,432,302,64,20,C.gray);
  button(s,'Заказ оформлен',886,515,302,40);
  note(s,'Рабочее название концепции, не название существующего продукта VK. Макет интерфейса иллюстративный. Цель: дополнительные оформленные заказы собственных продавцов внутри VK; рост числа бизнесов с инструментами продаж — промежуточная метрика. Источники: sources/case-brief.pdf, с.20; Q&A https://vkvideo.ru/video-92204627_456240708, 13:31, 22:56, 45:02.');

  s=slide(2,'Команда','Теневое Правительство');
  txt(s,'ГОРОД',64,207,200,28,17,C.gray,true);
  txt(s,'Москва',64,246,1000,58,41,C.blue,true);
  const names=['Якунченков Кирилл','Македонский Александр','Графов Григорий','Гурцев Владимир'];
  names.forEach((name,i)=>{const x=i%2===0?64:656,y=i<2?370:510;txt(s,String(i+1).padStart(2,'0'),x,y,58,40,23,C.blue,true);txt(s,name,x+72,y-4,482,60,31,C.ink,true);rule(s,y+83,x,552);});
  note(s,'Состав и название команды предоставлены участником. Роли намеренно не указаны по его просьбе. Город Москва подтверждён участником.');

  s=slide(3,'Резюме решения','Заказ в контексте сообщества');
  txt(s,number(evidence.warm_zero_orders),64,208,420,114,100,C.blue,true);
  txt(s,'сообщества в синтетической\nвыборке для исследования',70,332,445,74,28,C.ink,true);
  txt(s,'Есть каталог, чекаут и открытия\nкарточек. За месяц — 0 заказов.',70,432,445,75,24,C.gray);
  txt(s,`Медиана — ${evidence.warm_median_opens} открытия за месяц.\nУ ${evidence.warm_at_least_10_opens} сообществ ≥10 открытий.`,70,548,445,60,20,C.gray);
  const rows=[['Первый сегмент','Товарные сообщества с каталогом,\nоткрытиями карточек и без заказов'],['Предложение','Из шопса или переписки к заказу\nс заполненным товаром и условиями'],['Роль Маркета','Сохраняем каталог, поиск и витрины.\nПервый пилот — в контенте и чате.']];
  rows.forEach((a,i)=>{const y=211+i*132;txt(s,a[0].toUpperCase(),572,y,632,24,16,C.blue,true);txt(s,a[1],572,y+33,632,76,26,C.ink);if(i<2)rule(s,y+116,572,632);});
  txt(s,'Пилот 90 дней: проверяем прирост заказов на бизнес',572,614,632,30,20,C.blue,true);
  note(s,'Датасет VK Case Champ, лист «Бизнесы». Товарное или смешанное сообщество, активный каталог, чекаут, открытия из контента и ноль заказов дают 233 строки. При пороге десять открытий остаётся 39, медиана исходной группы — два открытия. Для рекрутинга живых продавцов проверяем остатки и наличие реальных обращений о товаре. Основная метрика по Q&A 13:31 — оформленные заказы. Данные за месяц не показывают историю первой продажи.');

  s=slide(4,'Проблематика','Инструменты включены, заказы редки');
  txt(s,number(evidence.checkout_pct,1)+'%',64,202,290,91,70,C.blue,true);
  txt(s,'включили чекаут',68,296,310,35,23,C.ink);
  txt(s,number(evidence.selling_pct,1)+'%',389,202,290,91,70,C.ink,true);
  txt(s,'получили ≥1 заказа',393,296,328,35,23,C.ink);
  txt(s,`Датасет VK, лист «Бизнесы», ${number(evidence.goods_communities)} сообществ.\nЧекаут на конец периода, заказы за месяц.`,68,349,650,59,18,C.gray);
  txt(s,'ОТКУДА ОТКРЫВАЮТ КАРТОЧКИ МАРКЕТА',64,441,670,28,17,C.gray,true);
  chart(s,{left:55,top:478,width:676,height:168},['Главная Маркета','Лента и клипы','Витрина сообщества'],[marketShare('Главная Маркета Вконтакте'),marketShare('Лента')+marketShare('Клипы'),marketShare('Витрина магазина')],{format:'0.0%',max:0.55,colors:['#B3C8E3','#7DAFF1',C.blue],gapWidth:90,name:'Доля открытий'});
  rect(s,780,208,436,425,C.pale,18);
  txt(s,'Два возможных барьера',810,234,376,44,29,C.ink,true);
  txt(s,`${number(evidence.ready_zero_orders_zero_content_opens)} с каталогом и чекаутом\nза месяц без заказов\nи открытий из контента.`,810,302,376,130,26,C.ink);
  txt(s,'Для них проверяем спрос.\nГде интерес уже есть,\nпроверяем оформление.',810,483,376,112,23,C.gray);
  note(s,'Датасет VK Case Champ, листы «Бизнесы» и «Маркет Вконтакте — источники». Чекаут 3 826 / 4 158 на конец периода, сообщества с заказом 285 / 4 158 за месяц. Активный каталог и чекаут есть у 3 637. Из этой группы 3 126 имеют ноль заказов и открытий из контента. Последний признак охватывает только контент. Открытия карточек собственных продавцов: витрины 39,1%, лента и клипы 18,6%, главная 0,2%, поиск 1,9%, «Другое» 40,2%. Заказ можно оформить с оплатой вне VK. Источники и таймкоды в приложении.');

  s=slide(5,'Возможные пути','Приоритет — продажи знакомому сообществу');
  txt(s,'Маркетплейс даёт логистику; классифайд — поиск сделки; свой сайт — контроль.\nПредлагаемая роль VK — покупка у знакомого бизнеса через контент и общение.',64,188,1152,72,24,C.gray);
  const vals=[['Критерий','Центральный каталог','Партнёрский чекаут','Заказ в сообществе'],['Где берём спрос','Поиск и новая привычка','Контент и ассортимент\nпартнёра','Контент, подписка\nи диалог'],['Что нужно развивать','Каталог, ранжирование,\nпривлечение','Передачу заказа\nпартнёру','Переход к заказу\nи работу продавца'],['Связь с целью кейса','Собственные продавцы;\nспрос надо доказать','Заказы партнёра;\nсчитаем отдельно','Заказы собственных\nпродавцов VK'],['Решение','Сохранить, проверять\nотдельным тестом','Сохранить как\nдополнительный путь','Первый пилот']];
  const tb=s.tables.add({rows:5,columns:4,left:64,top:281,width:1152,height:286,columnWidths:[225,309,309,309],values:vals});
  tb.borders.assign({fill:C.white,width:3,style:'solid'});
  for(let r=0;r<5;r++)for(let c=0;c<4;c++){const cell=tb.getCell(r,c);cell.fill=r===0?(c===3?C.blue:C.navy):(c===3?'#E9F2FF':C.pale);cell.text.style={fontSize:r===0?20:19,bold:r===0||c===0||r===4,color:r===0?C.white:C.ink,verticalAlignment:'middle'};cell.text.typeface='Arial';}
  txt(s,'Weixin связывает контент и покупки. В VK шопсы уже привлекают спрос для Ozon.\nПроверяем этот путь для собственных продавцов. Источники — в приложении.',64,589,1152,59,20,C.ink);
  note(s,'Сравнение путей — качественная оценка команды по одинаковым критериям, не результат эксперимента. Отдельный каталог не предлагаем закрывать: он сохраняет роль поиска и повторного входа; приоритет инвестиций — контекстный путь заказа. Маркет — общий товарный и заказный слой с витринами/поиском, без копирования складской логистики маркетплейса. Бенчмарк: Tencent Q3 2024 results presentation, https://static.www.tencent.com/uploads/2024/11/13/ccffd154b896b6c3e1ae65c13b73761d.pdf: Mini Shops uses Weixin social interactions, content services and payment capabilities. Инференс команды — применить принцип связности, не переносить китайские показатели роста. Российский аналог контентного привлечения: шопсы VK; источник Q&A 08:47–09:31,49:03. Прикрепление товаров к постам и клипам уже существует; это не наша новая функция. Исследование остальных кейсов: notebooks/02_social_commerce_benchmarks.ipynb и research/data/cases.csv. Meta и Pinterest меняли отдельные функции оплаты; это не доказывает провал любого каталога.');

  s=slide(6,'Концепция','Единый заказ в контенте и переписке');
  const steps=[['01','Подключить продавца'],['02','Собрать заказ в диалоге'],['03','Оформить и вернуться']];
  steps.forEach((a,i)=>{const x=64+i*393;txt(s,a[0],x,190,48,34,22,C.blue,true);txt(s,a[1],x+53,190,324,34,23,C.ink,true);});
  const xs=[64,457,850],y=243,w=366,h=328;
  phone(s,xs[0],y,w,h,'Магазин сообщества');
  txt(s,'Готовность к заказам',86,329,320,32,21,C.ink,true);
  txt(s,'✓  Товары и остатки\n✓  Получение: самовывоз\n✓  Оплата: при получении',86,374,320,90,20,C.ink);
  button(s,'Опубликовать товар',86,493,322,43);
  phone(s,xs[1],y,w,h,'Керамика Лето');
  rect(s,479,335,280,44,'#E9F2FF',12);txt(s,'Есть такая чашка?',491,341,254,30,20,C.ink);
  txt(s,'Чашка ручной работы',479,397,322,30,21,C.ink,true);
  txt(s,'2 000 ₽  ·  1 шт. в наличии',479,436,322,30,20,C.gray);
  button(s,'Оформить заказ',479,493,322,43);
  phone(s,xs[2],y,w,h,'Ваш заказ № 104');
  txt(s,'2 000 ₽',872,332,322,44,32,C.ink,true);
  txt(s,'Получение: самовывоз\nОплата: при получении\nСтатус: продавец подтвердил',872,394,322,84,19,C.ink);
  button(s,'Написать продавцу',872,493,322,43);
  txt(s,'Продавец выбирает товар из каталога и публикует шопс по шаблону.\nИз шопса или чата покупатель открывает заполненный заказ и подтверждает условия.\nПри слабом спросе тестируем продвижение. Оплата и доставка — по выбору продавца.',64,574,1152,80,18,C.gray);
  note(s,'Кабинет предлагает выбрать один доступный товар из каталога и публиковать его по шаблону шопса. Покупатель открывает предзаполненный заказ из публикации или сообщения и подтверждает условия. Два действия возможны при сохранённых данных и доступном варианте получения. При вопросах продавец добавляет тот же заказ в диалог. После исполнения покупатель может повторить заказ. Слабый спрос — отдельный тест контента и продвижения. Сотрудничество с авторами проверяем после атрибуции и экономики. Остатки, статусы и способы оплаты требуют проверки интерфейса. Экраны иллюстрируют концепцию.');

  s=slide(7,'Обоснование и экономика','Сценарии роста заказов и окупаемости');
  const economics = projection.economics;
  txt(s,`НА ${number(projection.reference_goods_communities)} ТОВАРНЫХ СООБЩЕСТВ. УСЛОВНЫЙ МАСШТАБ`,64,179,1152,28,17,C.blue,true);
  txt(s,'Базовый сценарий',64,227,560,43,29,C.ink,true);
  txt(s,`${number(projection.eligible)} подходят × ${number(base.reach*100)}% увидят предложение\n× ${number(base.adoption*100)}% подключатся × ${number(base.orders_per_adopter,2)} заказа на участника\n= ${orders(base)} дополнительных заказов в месяц`,64,285,565,120,22,C.ink);
  rule(s,419,64,560);
  txt(s,`≈${number(base.monthly_incremental_selling_communities_at_scale)} дополнительных бизнесов с заказом в месяц.\nПродавцу: ${number(projection.seller_contribution_per_completed_order_with_service_rub)} ₽ вклада с исполненного заказа\nна ${number(economics.aov_rub)} ₽ при комиссии сервиса ${number(economics.service_fee*100)}%.`,64,433,565,100,21,C.ink);
  const payback = base.monthly_order_hurdle === null
    ? 'В этом сценарии платный сервис не покрывает затраты.'
    : `Комиссия покрывает затраты от ${number(base.monthly_order_hurdle/1000,1)} тыс. заказов/мес.\nПри ${number(base.paid_share*100)}% заказов с оплатой через сервис.`;
  txt(s,payback,64,552,575,81,19,C.gray);
  txt(s,'Дополнительные заказы в месяц',660,225,555,44,27,C.ink,true);
  const scenarioOrders=[low,base,high].map(v=>Math.round(v.monthly_incremental_orders_at_scale));
  chart(s,{left:660,top:283,width:545,height:250},['Осторожный','Базовый','Верхний'],scenarioOrders,{direction:'column',format:'0',max:Math.max(...scenarioOrders)*1.25,colors:['#B3C8E3',C.blue,'#B3C8E3'],gapWidth:130,name:'Дополнительные заказы в месяц'});
  txt(s,'После выхода на масштаб. Все эффекты — допущения.\nМодель на 12 месяцев и формулы — в приложении.',660,548,555,76,18,C.gray);
  note(s,'Модель воспроизводится через materials/scripts/strategy_model.py и materials/presentation/scenario_inputs.json. В базовом сценарии на 100 000 товарных и смешанных сообществ доля подходящих 233 / 4 158. Около 5 604 подходят, 2 802 увидят предложение, 841 подключится. Допущение 0,25 заказа на участника даёт 210 дополнительных оформленных заказов в месяц на масштабе. Прирост доли с заказом у участников на 10 п. п. даёт 84 дополнительных бизнеса с заказом в этом месяце. Годовой результат при разгоне — около 1 156 заказов и −4,19 млн ₽ для VK. При чеке 2 000 ₽ вклад продавца до труда, налогов и постоянных затрат составляет 600 ₽ без платного сервиса и 540 ₽ с сервисом. Вклад VK — 30 ₽ с завершённой покупки через добровольный сервис. При 15% таких заказов вклад составляет 4,5 ₽ на дополнительный заказ. Постоянные расходы 150 тыс. ₽ в месяц плюс 2,4 млн ₽ разработки, распределённые на 12 месяцев, требуют около 77,8 тыс. заказов в месяц на масштабе. Прибыль от рекламы и перенос заказов между каналами требуют самостоятельных измерений. Порог окупаемости на слайде относится к 12 месяцам на постоянном масштабе, а годовой результат учитывает разгон.');

  s=slide(8,'Выводы и ожидаемый результат','90 дней до решения о масштабировании',C.navy);
  const phases=[['01–30','Проверка барьера','8 интервью с продавцами\n5 тестов оформления\nСобытия и правила оплаты'],['31–60','Рабочий прототип','30 продавцов в пилоте\nОстатки, заказ и статусы\nПроверка поддержки'],['61–90','Контрольный тест','Случайное распределение\nпо сообществам\nРазмер — по дисперсии заказов']];
  phases.forEach((a,i)=>{const x=64+i*393;txt(s,a[0],x,208,354,59,43,C.light,true);txt(s,a[1],x,288,354,40,27,C.white,true);txt(s,a[2],x,351,354,106,23,C.light);});
  rule(s,493,64,1152,'#426389');
  txt(s,'Что считаем успехом',64,518,360,39,27,C.white,true);
  txt(s,'Прирост оформленных заказов на бизнес.\nУчитываем отмены и перенос продаж из чата.',64,573,555,66,21,C.light);
  txt(s,'Решение после теста',674,518,542,39,27,C.white,true);
  txt(s,'Сопоставляем эффект с затратами.\nПри слабом спросе проверяем дистрибуцию.',674,573,542,66,21,C.light);
  note(s,'Этапы предстоит пройти. Интервью и 30 продавцов нужны для проверки сценария и прототипа. Затем случайно назначить условия на уровне бизнеса и измерять все назначенные сообщества в течение 28 дней. При нескольких магазинах одного владельца назначать одно условие. Размер теста рассчитать по дисперсии заказов и минимальному практически значимому эффекту. Главная метрика — валидные оформленные заказы на бизнес. Дополнительные метрики — бизнесы с заказом, исполнение, отмены, жалобы, поддержка и перенос продаж из переписки. Поток без наблюдаемого интереса тестировать отдельно с инструментом контента и дистрибуции. Масштабирование требует измеримого эффекта и проверенной экономики.');
  return {slides:p.slides.items.length};
}
// Live editor entry point.
const fs = await import('node:fs/promises');
const evidence = JSON.parse(await fs.readFile('materials/presentation/evidence.json', 'utf8'));
await artifactSession.run(async ({presentation,session}) => {
  nodeRepl.write(await buildStrategyDeck(presentation,evidence));
  nodeRepl.write({sessionId:session.sessionId});
}, {artifactType:'presentation',artifactRef:'artifact_hDtOzhxchhgyKGHdSiET6ervTH0Fuzvk'});
