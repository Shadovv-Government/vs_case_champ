import { C, SIZE, FONT, DISPLAY, ICONS, iconFile, box, txt, pic, slide, panel, note, separator, dot, button, icon, ring, profitLine, scenarioChart, int, pct } from './layout.mjs';
import { notes } from './notes.mjs';
export { SIZE, FONT, DISPLAY };
export const ASSETS=['cover.jpg','aurora.jpg','ceramics.jpg','team.jpg','flow.jpg','productportrait.jpg','vk-logo.png',
  ...ICONS.map(([id,color])=>iconFile(id,color))];

function cover(p,a){
  const s=slide(p,a,1,'VK Case Champ 2026',null,'cover.jpg',0);
  pic(s,a,'vk-logo.png',66,119,63,63,'Официальный знак VK');
  txt(s,'VK Заказ\nрядом',52,205,695,217,98,C.ink,true);
  txt(s,'От вопроса о товаре\nдо заказа в VK',58,439,572,100,34,C.ink);
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
  const s=slide(p,a,3,'Резюме','Товар находят в привычных местах','aurora.jpg',52);
  const colors=[C.ice,C.blue,'#F7F9FF',C.violet];
  const labels=['Витрина сообщества','Лента и клипы','Главная Маркета','Поиск и «Другое»'];
  panel(s,63,191,548,466);
  txt(s,'Где открывают карточки',82,206,510,41,26,C.ink,true);
  ring(s,174,242,325,'Доля открытий карточек, %',labels,e.market_pct,colors,76);
  txt(s,pct(e.market_pct[0]+e.market_pct[1]),217,351,242,84,59,C.ink,true,'center');
  txt(s,'витрины, лента\nи клипы',232,438,213,64,21,C.dim,false,'center');
  txt(s,'193,5 млн открытий в данных кейса',82,604,511,38,21,C.dim,false,'center');
  panel(s,634,191,581,290);
  labels.forEach((label,i)=>{
    const y=208+i*62;
    dot(s,660,y+22,13,colors[i]);
    txt(s,label,682,y+5,385,48,24,C.ink,i<2);
    txt(s,pct(e.market_pct[i]),1050,y+5,137,48,24,colors[i],true,'right');
    if(i<3)separator(s,665,y+58,519);
  });
  panel(s,634,502,581,155,'#142E56');
  icon(s,a,'basket',655,525,38);
  txt(s,'Роль Маркета',706,521,481,45,28,C.ice,true);
  txt(s,'Хранит карточки, даёт поиск\nи оформляет заказ.',654,578,530,58,25);
  return s;
}
function problem(p,a,o){
  const s=slide(p,a,4,'Проблематика','Чекаут есть. Заказов за месяц нет','flow.jpg',18);
  txt(s,'Два сегмента с активными товарами в синтетических данных',58,164,1152,42,24,C.dim);
  const segments=[
    {x:62,n:o.quiet,part:o.quiet_with_product_posts,color:C.ice,label:'Без открытий из контента',detail:'выпустили товарный\nпост или клип',tail:'Проверяем товарную публикацию'},
    {x:648,n:o.warm,part:o.warm_under_10,color:C.violet,label:'С открытиями из контента',detail:'получили всего\n1–9 открытий',tail:'Для пилота ищем обращения о покупке'},
  ];
  for(const g of segments){
    panel(s,g.x,224,568,432);
    box(s,g.x+26,244,56,4,g.color,2);
    txt(s,int(g.n),g.x+16,265,351,97,75,C.ink,true);
    txt(s,g.label,g.x+19,366,519,47,24,C.dim,true);
    separator(s,g.x+24,422,306);
    ring(s,g.x+351,266,205,g.label,[g.detail.replace('\n',' '),'Остальные'],[g.part,g.n-g.part],[g.color,'#384A6E'],78);
    txt(s,pct(100*g.part/g.n),g.x+371,344,164,47,26,g.color,true,'center');
    txt(s,int(g.part),g.x+19,447,144,83,54,g.color,true);
    txt(s,g.detail,g.x+158,450,348,76,25);
    box(s,g.x+22,576,524,53,'#243B65',10);
    txt(s,g.tail,g.x+30,578,505,49,21,C.ink,true);
  }
  return s;
}
function strategy(p,a){
  const s=slide(p,a,5,'Выбор стратегии','Два теста для разных продавцов','team.jpg',52);
  const rows=[
    {id:'chat',tag:'ТЕСТ 1',state:'Уже спрашивают о товаре',action:'Заказ из диалога',metric:'Метрика — заказы из всех входов',fill:'#162F5A',color:C.ice},
    {id:'tag',tag:'ТЕСТ 2',state:'Есть просмотры обычных постов',action:'Товар к следующему посту',metric:'Метрика — открытия и заказы',fill:'#202C55',color:C.violet},
    {id:'sliders',tag:'РЕЗЕРВ',state:'Настройки блокируют продажу',action:'Подсказка настройки',metric:'Метрика — устранённый барьер и заказ',fill:'#171F37',color:C.dim},
  ];
  rows.forEach((row,i)=>{
    const y=185+i*156;
    panel(s,63,y,758,137,row.fill);
    dot(s,86,y+45,52,'#304571'); icon(s,a,row.id,98,y+57,28,row.color);
    txt(s,row.tag,153,y+11,130,29,17,row.color,true);
    txt(s,row.state,286,y+11,509,29,19,C.dim);
    txt(s,row.action,153,y+44,652,53,34,C.ink,true);
    txt(s,row.metric,153,y+99,650,29,20,C.dim);
  });
  pic(s,a,'productportrait.jpg',848,185,367,449,'Редакционное фото керамики',21);
  box(s,848,520,367,114,'#080E25/91',16);
  txt(s,'Одна карточка\nдля поста и диалога',866,532,328,78,26,C.ink,true);
  return s;
}
function chat(p,a){
  const s=slide(p,a,6,'Концепция','Заказ начинается в чате','flow.jpg',19);
  panel(s,61,183,1159,482,'#0B152C');
  box(s,62,183,1157,66,'#182D51',18);
  pic(s,a,'ceramics.jpg',84,194,47,47,'Аватар сообщества Керамика Лето',23);
  txt(s,'Керамика Лето',143,191,563,47,26,C.ink,true);
  txt(s,'Предпросмотр сценария',866,198,324,39,19,C.dim,false,'right');
  box(s,627,253,1,390,C.stroke);
  box(s,93,266,495,42,'#233D71',14);
  txt(s,'Есть синяя чашка? Заберу сегодня.',102,269,478,36,20,C.ink,true,'right');
  box(s,83,318,453,42,'#222F4E',14);
  txt(s,'Да, есть. Отправляю предложение.',93,321,427,36,20,C.ink);
  box(s,83,373,504,180,'#172B4B',15,C.stroke);
  pic(s,a,'ceramics.jpg',101,389,112,112,'Фото синей чашки',12);
  icon(s,a,'basket',229,390,27,C.ice);
  txt(s,'Синяя чашка',261,383,302,43,27,C.ink,true);
  txt(s,'Самовывоз сегодня',224,427,343,33,19,C.dim);
  txt(s,'2 000 ₽',224,459,166,53,31,C.ink,true);
  button(s,'Купить',410,480,155,50);
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
  icon(s,a,'lock',671,393,24,C.dim);
  txt(s,'Контакты для связи по заказу',705,385,454,43,18,C.dim);
  button(s,'Подтвердить заказ',672,445,500,46);
  box(s,651,530,545,103,'#123B3B',15,'#438D79');
  dot(s,672,548,56,'#155B4B');
  icon(s,a,'check',683,559,34,C.mint);
  txt(s,'Заказ № 104 оформлен',742,538,440,44,28,C.mint,true);
  txt(s,'Самовывоз · оплата при получении',742,584,435,36,19,C.ink);
  return s;
}
function economics(p,a,m){
  const s=slide(p,a,7,'Экономика','Сколько заказов нужно для окупаемости','aurora.jpg',50);
  panel(s,62,189,765,462);
  txt(s,'Результат первого года, млн ₽',79,199,719,41,26,C.ink,true);
  const orders=[0,10,20,30,40,50,60];
  const results=orders.map(n=>Number(((n*1000*m.net_per_order*m.active_months-m.year_cost)/1e6).toFixed(1)));
  profitLine(s,87,261,711,320,orders.map(String),results);
  txt(s,'Дополнительные оформления, тыс. в месяц',86,592,712,37,20,C.dim,false,'center');
  panel(s,850,189,365,247,'#10365E');
  txt(s,'42 тыс.',865,212,331,116,68,C.ice,true);
  txt(s,'оформлений в месяц\nдля окупаемости',868,341,314,71,26,C.ink,true);
  panel(s,850,458,365,193,'#282B4B');
  txt(s,'−1,7 млн ₽',864,477,328,85,47,C.rose,true);
  txt(s,'при 25 тыс. в месяц\nСценарий первого года',868,565,324,63,21,C.dim);
  return s;
}
function pilot(p,a,e){
  const s=slide(p,a,8,'Ожидаемый результат','Пилот измеряет заказы и продавцов','flow.jpg',16);
  panel(s,63,187,755,468);
  const legends=[['Доп. заказы',C.blue],['Доп. сообщества с заказом',C.ice]];
  legends.forEach(([label,color],i)=>{
    const x=90+i*242; dot(s,x,218,15,color); txt(s,label,x+21,203,i?440:222,43,21,C.ink,true);
  });
  scenarioChart(s,84,265,716,322,e);
  txt(s,'На 1 000 сообществ · условные сценарии',80,605,714,38,21,C.dim,false,'center');
  panel(s,842,187,373,468,'#152952');
  const stages=[['28 дней','Заказы VK против контроля'],['+28 дней','Исполнение и возвраты']];
  stages.forEach(([big,small],i)=>{
    const y=210+i*160;
    txt(s,big,857,y,335,82,51,C.ice,true);
    txt(s,small,861,y+85,330,58,23,C.ink);
    separator(s,864,y+137,326);
  });
  icon(s,a,'check',862,545,29,C.mint);
  txt(s,'Сверка продаж\nпо всем каналам',902,528,281,94,25,C.ink,true);
  return s;
}
export async function buildSlides(p,{assets:a,evidence:e},indices=[1,2,3,4,5,6,7,8]){
  const makers=[()=>cover(p,a),()=>team(p,a),()=>summary(p,a,e),()=>problem(p,a,e.observed),
    ()=>strategy(p,a),()=>chat(p,a),()=>economics(p,a,e.model),()=>pilot(p,a,e)];
  for(const n of indices)note(makers[n-1](),notes[n-1]);
  return p.slides.items.length;
}
