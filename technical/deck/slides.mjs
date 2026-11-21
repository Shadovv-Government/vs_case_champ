import { C, SIZE, FONT, DISPLAY, ICONS, iconFile, box, txt, pic, slide, panel, note, separator, dot, button, icon, ring, profitLine, scenarioChart, int, pct, millions } from './layout.mjs';
import { notesFor } from './notes.mjs';
export { SIZE, FONT, DISPLAY };
export const ASSETS=['cover.jpg','aurora.jpg','ceramics.jpg','team.jpg','flow.jpg','vk-logo.png',
  ...ICONS.map(([id,color])=>iconFile(id,color))];

function cover(p,a){
  const s=slide(p,a,1,'VK Case Champ 2026',null,'cover.jpg',0);
  pic(s,a,'vk-logo.png',66,119,63,63,'Официальный знак VK');
  txt(s,'VK Заказ\nрядом',52,205,695,217,98,C.ink,true);
  txt(s,'Как малому бизнесу продавать\nиз чатов и постов ВКонтакте',58,439,570,100,31,C.ink);
  txt(s,'Теневое Правительство',59,618,518,36,23,C.dim,true);
  return s;
}
function team(p,a){
  const s=slide(p,a,2,'Команда',null,'team.jpg',44);
  txt(s,'Теневое Правительство',56,108,1000,89,61,C.ink,true);
  txt(s,'Москва',59,194,406,50,32,C.ice,true);
  const names=[['Якунченков','Кирилл'],['Македонский','Александр'],['Графов','Григорий'],['Гурцев','Владимир']];
  names.forEach(([surname,firstName],i)=>{
    const x=i%2?673:63, y=i<2?300:471;
    separator(s,x,y-12,538,'#75B6FF/73');
    txt(s,surname,x-6,y,550,74,55,C.ink,true);
    txt(s,firstName,x-4,y+76,553,45,34,C.ice);
  });
  return s;
}
function summary(p,a,e){
  const s=slide(p,a,3,'Резюме','Больше продавцов с заказами в VK','aurora.jpg',52);
  const colors=[C.ice,C.blue,C.ink,'#8C9FBE',C.violet];
  const labels=['Витрины','Лента и клипы','Главная Маркета','Поиск','«Другое»'];
  const shares=[...e.market_pct.slice(0,3),e.market_totals.search_pct,e.market_totals.other_pct];
  panel(s,63,191,548,466,C.panel);
  txt(s,'Где открывают карточки товаров',84,206,510,41,27,C.ink,true);
  ring(s,77,265,254,'Доля открытий карточек, %',labels,shares,colors,76);
  txt(s,pct(shares[0]+shares[1]),129,342,149,76,44,C.ink,true,'center');
  txt(s,'витрины, лента\nи клипы',126,409,155,59,17,C.dim,false,'center');
  labels.forEach((label,i)=>{
    const y=267+i*52;
    dot(s,333,y+13,10,colors[i]);
    txt(s,label,345,y,180,36,18,C.ink,i<2);
    txt(s,pct(shares[i]),515,y,78,36,19,colors[i],true,'right');
    if(i<4)separator(s,333,y+43,252);
  });
  const trafficTotal=new Intl.NumberFormat('ru-RU',{maximumFractionDigits:1}).format(e.market_totals.opens/1e6);
  txt(s,trafficTotal+' млн открытий в синтетических данных кейса',69,586,536,46,18,C.dim,false,'center');
  panel(s,634,191,581,290);
  txt(s,'Малые магазины и мастерские',657,218,531,45,28,C.ice,true);
  txt(s,'Из чата покупатель оформляет заказ\nна уже согласованных условиях.',657,280,531,70,23);
  separator(s,658,367,529);
  txt(s,'Тем, чьи посты уже читают, подсказываем,\nкак прикрепить свой товар к новой записи.',657,384,530,70,23);
  panel(s,634,502,581,155,'#142E56');
  icon(s,a,'basket',655,518,35);
  txt(s,'Роль Маркета',704,513,481,43,27,C.ice,true);
  txt(s,'Маркет оставляем для поиска и рекомендаций.\nЗаказ оформляется в магазине сообщества.',657,565,534,68,21);
  return s;
}
function problem(p,a,o){
  const s=slide(p,a,4,'Проблематика',int(o.quiet+o.warm)+' сообществ с чекаутом без заказов','flow.jpg',43);
  txt(s,'Две группы с активными товарами из '+int(o.goods)+' товарных и смешанных сообществ',58,164,1152,42,23,C.dim);
  const segments=[
    {x:62,n:o.quiet,part:o.quiet_with_product_posts,color:C.ice,label:'Без открытий из контента',detail:'выпустили товарный\nпост или клип',tail:int(o.quiet_with_normal_views_without_product_posts)+' получили просмотры обычного контента\nи не публиковали товарный'},
    {x:648,n:o.warm,part:o.warm_under_10,color:C.violet,label:'С открытиями из контента',detail:'получили от 1 до 9\nоткрытий карточек',tail:'На '+int(o.warm_at_least_10)+' сообществ с 10 и более открытиями\nпришлось '+pct(100*o.warm_high_opening_share)+' открытий группы'},
  ];
  for(const g of segments){
    panel(s,g.x,224,568,432,C.panel);
    box(s,g.x+26,244,56,4,g.color,2);
    txt(s,int(g.n),g.x+16,265,351,97,75,C.ink,true);
    txt(s,g.label,g.x+19,366,519,47,24,C.dim,true);
    separator(s,g.x+24,422,306);
    ring(s,g.x+351,266,205,g.label,[g.detail.replace('\n',' '),'Остальные'],[g.part,g.n-g.part],[g.color,'#384A6E'],78);
    txt(s,pct(100*g.part/g.n),g.x+371,332,164,45,26,g.color,true,'center');
    txt(s,'от группы',g.x+371,376,164,24,16,C.dim,false,'center');
    txt(s,int(g.part),g.x+19,447,144,83,54,g.color,true);
    txt(s,g.detail,g.x+158,450,348,76,25);
    box(s,g.x+22,576,524,53,'#243B65',10);
    txt(s,g.tail,g.x+30,576,503,53,17,C.ink,true);
  }
  txt(s,'Лист «Бизнесы», синтетические данные. Товары и чекаут на конец месяца. Заказы и открытия за месяц.',62,670,1155,29,18,C.ink);
  return s;
}
function strategy(p,a){
  const s=slide(p,a,5,'Выбор стратегии','Сначала тестируем заказ из чата','team.jpg',52);
  const rows=[
    {id:'chat',tag:'ТЕСТ 1',state:'Покупатели спрашивают о товаре',action:'Заказ из чата',business:'Продавец вводит меньше данных вручную',metric:'Для VK измеряем прирост заказов внутри платформы',fill:'#162F5A',color:C.ice},
    {id:'tag',tag:'ТЕСТ 2',state:'У постов есть охват, товарных меток мало',action:'Товар к следующему посту',business:'Подсказка помогает продавцу прикрепить товар',metric:'Для VK измеряем прирост открытий карточек и заказов',fill:'#202C55',color:C.violet},
    {id:'sliders',tag:'РЕЗЕРВ',state:'Есть товар и вопросы, чекаут не подключён',action:'Помощь с подключением чекаута',business:'Продавец начинает принимать заказы в VK',metric:'Для VK отдельно считаем подключения и первые заказы',fill:'#171F37',color:C.dim},
  ];
  rows.forEach((row,i)=>{
    const y=185+i*158;
    panel(s,63,y,758,144,row.fill);
    dot(s,86,y+45,52,'#304571'); icon(s,a,row.id,98,y+57,28,row.color);
    txt(s,row.tag,153,y+8,130,29,17,row.color,true);
    txt(s,row.state,286,y+8,508,29,18,C.dim);
    txt(s,row.action,153,y+38,650,48,32,C.ink,true);
    txt(s,row.business,153,y+87,648,27,20,C.ink);
    txt(s,row.metric,153,y+111,648,28,18,C.dim);
  });
  panel(s,842,185,374,460,'#132448');
  txt(s,'Как покупают',862,208,334,52,27,C.ice,true);
  const channels=[
    ['Ozon','Поиск в каталоге маркетплейса'],
    ['Авито','Объявление и чат с продавцом'],
    ['Сайт продавца','Трафик привлекает продавец'],
    ['VK','От поста или чата до заказа в VK'],
  ];
  channels.forEach(([channel,description],i)=>{
    const y=271+i*86;
    txt(s,channel,863,y,330,35,22,i===3?C.ice:C.ink,true);
    txt(s,description,863,y+34,334,43,18,C.dim);
    if(i<3)separator(s,864,y+80,322);
  });
  txt(s,'В отчёте сравниваем инструменты VK, Prodamus, Weixin и TikTok Shop.',63,670,1151,29,18,C.ink);
  return s;
}
function chat(p,a){
  const s=slide(p,a,6,'Концепция','Заказ начинается в чате','flow.jpg',43);
  panel(s,61,183,1159,460,'#0B152C');
  box(s,62,183,1157,66,'#182D51',18);
  pic(s,a,'ceramics.jpg',84,194,47,47,'Аватар сообщества Керамика Лето',23);
  txt(s,'Керамика Лето',143,191,563,47,26,C.ink,true);
  txt(s,'Макет сценария',866,198,324,39,19,C.dim,false,'right');
  box(s,627,253,1,376,C.stroke);
  box(s,93,266,495,42,'#233D71',14);
  txt(s,'Есть синяя чашка? Заберу сегодня.',102,269,478,36,20,C.ink,true,'right');
  box(s,83,318,453,42,'#222F4E',14);
  txt(s,'Есть. Можно забрать сегодня до 19:00.',93,321,427,36,20,C.ink);
  box(s,83,373,504,180,'#172B4B',15,C.stroke);
  pic(s,a,'ceramics.jpg',101,389,112,112,'Фото синей чашки',12);
  icon(s,a,'basket',229,390,27,C.ice);
  txt(s,'Синяя чашка',261,383,302,43,27,C.ink,true);
  txt(s,'Самовывоз сегодня до 19:00',224,427,343,33,19,C.dim);
  txt(s,'2 000 ₽',224,459,166,53,31,C.ink,true);
  button(s,'Оформить',410,480,155,50);
  icon(s,a,'next',598,470,25,C.ice);
  box(s,83,581,504,47,'#17243D',12,C.stroke);
  txt(s,'Сообщение…',99,583,398,44,18,C.dim);
  icon(s,a,'next',540,594,23,C.dim);

  box(s,651,263,545,247,'#152443',14,C.stroke);
  icon(s,a,'pin',670,280,26,C.ice);
  txt(s,'Данные для заказа',705,272,449,41,26,C.ink,true);
  box(s,672,320,237,58,C.field,10);
  box(s,922,320,250,58,C.field,10);
  txt(s,'Имя',677,320,224,24,15,C.dim);
  txt(s,'Анна',677,341,224,34,21,C.ink,true);
  txt(s,'Телефон',928,320,228,24,15,C.dim);
  txt(s,'+7 ••• ••• 12 34',928,341,228,34,21,C.ink,true);
  txt(s,'Самовывоз до 19:00. 2 000 ₽ при получении.',671,385,500,43,18,C.dim);
  button(s,'Подтвердить заказ',672,445,500,46);
  box(s,651,530,545,103,'#123B3B',15,'#438D79');
  dot(s,672,548,56,'#155B4B');
  icon(s,a,'check',683,559,34,C.mint);
  txt(s,'Заказ № 104 оформлен',742,538,440,44,28,C.mint,true);
  txt(s,'Сегодня до 19:00. Оплата при получении.',742,584,435,36,18,C.ink);
  box(s,62,650,1156,59,'#0B152C',12);
  txt(s,'Продавец',73,653,123,24,17,C.ice,true);
  txt(s,'VK Education для новых продавцов и кабинет для действующих. Затем продавцы настраивают товар и чекаут.',194,653,1014,24,17);
  txt(s,'Покупатель',73,680,123,24,17,C.ice,true);
  txt(s,'Из шопса покупатель идёт сразу к оформлению. В чате сначала согласует условия с продавцом.',194,680,1014,24,17);
  return s;
}
function economics(p,a,m){
  const s=slide(p,a,7,'Экономика','Что нужно для окупаемости сервиса','aurora.jpg',50);
  txt(s,'Модель платной сверки оплат и возвратов по номеру заказа',58,163,1152,40,23,C.dim);
  panel(s,62,213,765,438);
  txt(s,'Результат VK за первый год, млн ₽',79,224,719,41,26,C.ink,true);
  const orders=[0,10,20,30,40,50,60];
  const results=orders.map(n=>Number(((n*1000*m.net_per_order*m.active_months-m.year_cost)/1e6).toFixed(1)));
  profitLine(s,87,271,711,289,orders.map(String),results);
  txt(s,'Дополнительные заказы до отмен и возвратов, тыс. в месяц',78,574,733,44,19,C.dim,false,'center');
  panel(s,850,213,365,150,'#10365E');
  const threshold=m.breakeven_monthly_orders;
  txt(s,threshold===null?'Вклад ≤0 ₽':int(threshold/1000)+' тыс.',866,221,330,69,49,C.ice,true);
  txt(s,threshold===null?'Нужна другая модель дохода':'дополнительных заказов\nв месяц для окупаемости',871,292,330,60,23,C.ink);
  panel(s,850,375,365,112,'#282B4B');
  txt(s,millions(m.example_year_result),867,379,328,55,39,C.rose,true);
  txt(s,'при '+int(m.example_monthly_orders/1000)+' тыс. доп. заказов в месяц',871,437,330,39,18,C.dim);
  panel(s,850,499,365,152,'#172A4A');
  txt(s,int(m.seller_contribution_with_service)+' ₽ у продавца',867,509,335,49,27,C.ice,true);
  txt(s,'Комиссия '+pct(100*m.fee_rate)+'. Без неё '+int(m.seller_contribution)+' ₽.\nДо учёта труда, налогов и\nпостоянных расходов.',871,557,330,80,18,C.dim);
  txt(s,'При чеке '+int(m.aov_rub)+' ₽ вклад VK составляет '+int(m.net_per_order)+' ₽ с заказа. Затраты за год — '+millions(m.year_cost)+'. Пилот бесплатный.',63,670,1150,29,18,C.ink);
  return s;
}
function pilot(p,a,e){
  const plan=e.pilot;
  const s=slide(p,a,8,'План на 90 дней','Два теста при достаточной выборке','flow.jpg',43);
  panel(s,63,187,755,468);
  txt(s,'Заказ из чата. Три сценария',83,201,709,43,26,C.ink,true);
  const legends=[['Прирост заказов',C.blue],['Прирост сообществ с заказом',C.ice]];
  legends.forEach(([label,color],i)=>{
    const x=90+i*242; dot(s,x,263,15,color); txt(s,label,x+21,249,i?440:222,43,20,C.ink,true);
  });
  scenarioChart(s,84,290,716,295,e);
  const baseline=1_000*e.control.share_with_orders*e.control.orders_per_selling_community;
  txt(s,'За '+int(plan.observation_days)+' дней на 1 000 сообществ при '+int(baseline)+' заказах в контроле',80,600,714,39,19,C.dim,false,'center');
  panel(s,842,187,373,468,'#152952');
  const stages=[
    ['До '+int(plan.budget_total_rub/1000)+' тыс. ₽','На аудит и прототип\nза первые 34 дня.'],
    [int(plan.observation_days)+' + '+int(plan.followup_days)+' дней','Считаем заказы, затем\nотслеживаем их исполнение.'],
    ['Порог прироста','На 1 000 сообществ нужно\n+'+int(plan.orders_per_1000_gate)+' заказов в тесте чата\nи +'+int(plan.post_orders_per_1000_gate)+' в тесте подсказки.'],
  ];
  stages.forEach(([big,small],i)=>{
    const y=205+i*144;
    txt(s,big,859,y,337,62,33,C.ice,true);
    txt(s,small,861,y+64,331,i===2?81:60,20,C.ink);
    if(i<2)separator(s,864,y+129,326);
  });
  txt(s,'Для расширения нужен значимый прирост. Предел роста доли отмен — '+int(plan.cancel_margin_pp)+' п. п., доли жалоб — '+int(plan.complaint_margin_pp)+' п. п.',63,670,1150,29,18,C.ink);
  return s;
}
export async function buildSlides(p,{assets:a,evidence:e},indices=[1,2,3,4,5,6,7,8]){
  const makers=[()=>cover(p,a),()=>team(p,a),()=>summary(p,a,e),()=>problem(p,a,e.observed),
    ()=>strategy(p,a),()=>chat(p,a),()=>economics(p,a,e.model),()=>pilot(p,a,e)];
  const notes=notesFor(e);
  for(const n of indices)note(makers[n-1](),notes[n-1]);
  return p.slides.items.length;
}
