export const SIZE = {width:1280,height:720};
export const FONT = 'Golos Text';
export const DISPLAY = FONT;
export const C={ink:'#F7F9FF',dim:'#BBC9E4',blue:'#518CFF',ice:'#7BE9FF',violet:'#AB95FF',bg:'#080E25',panel:'#101C38',field:'#1D2D4E',stroke:'#354768',mint:'#53E5A5',rose:'#FF9DAD'};
export const frame=(left,top,width,height)=>({left,top,width,height});
export const silent={style:'solid',fill:'none',width:0};
export const int=x=>new Intl.NumberFormat('ru-RU').format(x);
export const pct=x=>new Intl.NumberFormat('ru-RU',{maximumFractionDigits:1}).format(x)+'%';
export const millions=x=>new Intl.NumberFormat('ru-RU',{minimumFractionDigits:1,maximumFractionDigits:1})
  .format(x/1e6).replace('-','−')+' млн ₽';
export function box(s,x,y,w,h,fill,round=0,stroke='none',geometry) {
  return s.shapes.add({geometry:geometry??(round?'roundRect':'rect'),position:frame(x,y,w,h),fill,
    line:stroke==='none'?silent:{fill:stroke,width:1.2,style:'solid'},...(round?{borderRadius:round}:{})});
}
export function txt(s,text,x,y,w,h,size=25,color=C.ink,bold=false,align='left') {
  const el=box(s,x,y,w,h,'none',0,'none','textbox');
  const copy=String(text)
    .replace(/(?<!\p{L})([авикосуя]) (?=\S)/giu,'$1\u00a0')
    .replace(/(\d) (?=(?:\d{3}(?!\d)|тыс\.|млн(?!\p{L})|₽|п\. п\.))/gu,'$1\u00a0')
    .replace(/п\. п\./g,'п.\u00a0п.');
  el.name=copy.split('\n')[0];el.text=copy;
  el.text.style={fontSize:size,color,bold,alignment:align,verticalAlignment:'middle'};
  el.text.typeface=FONT;
  return el;
}
export function pic(s,assets,name,x,y,w,h,alt,round=0){
  const z=typeof assets[name]==='string'?{path:assets[name]}:{blob:assets[name],contentType:name.endsWith('.jpg')?'image/jpeg':'image/png'};
  return s.images.add({...z,alt,fit:'cover',position:frame(x,y,w,h),...(round?{geometry:'roundRect',borderRadius:round}:{})});
}
export function slide(p,a,n,kicker,title,bg='flow.jpg',shade=35){
  const s=p.slides.add();s.size=SIZE;s.background.fill=C.bg;
  pic(s,a,bg,0,0,1280,720,'Фон с синими световыми переливами');
  if(shade)box(s,0,0,1280,720,`#080E25/${shade}`);
  txt(s,kicker.toUpperCase(),56,25,1000,37,21,C.ice,true);
  txt(s,String(n).padStart(2,'0')+' / 08',1084,25,133,37,19,C.dim,true,'right');
  box(s,64,75,1152,1,'#6F88B8/45');
  if(title)txt(s,title,55,90,1166,79,54,C.ink,true);
  return s;
}
export function panel(s,x,y,w,h,fill='#101C38/95'){
  return box(s,x,y,w,h,fill,22,'#4D618B/68');
}
export function note(s,value){s.speakerNotes.text=value;}
export function separator(s,x,y,w,color='#6F88B8/38'){box(s,x,y,w,1,color);}
export function dot(s,x,y,d,fill){box(s,x,y,d,d,fill,0,'none','ellipse');}
export function button(s,text,x,y,w,h,fill='#2664F0'){
  box(s,x,y,w,h,fill,10);
  txt(s,text,x,y,w,h,19,C.ink,true,'center');
}
export const iconFile=(id,color)=>`icons/${id}-${color.slice(1).toLowerCase()}.png`;
export const ICONS=[
  ['basket',C.ice],['chat',C.ice],['tag',C.violet],['sliders',C.dim],['next',C.ice],
  ['next',C.dim],['pin',C.ice],['lock',C.dim],['check',C.mint],
];
export function iconSvg(id,color){
  const paths={
    chat:'<path d="M20 11.5a7.8 7.8 0 0 1-8 7.5H5l1.4-3A7.3 7.3 0 0 1 4 11.5a8 8 0 0 1 16 0Z"/><path d="M8.5 11.5h7"/>',
    tag:'<path d="M4 4h7l9 9-7 7-9-9Z"/><circle cx="8" cy="8" r="1"/>',
    sliders:'<path d="M4 7h16M4 12h16M4 17h16"/><circle cx="8" cy="7" r="2" fill="#192843"/><circle cx="15" cy="12" r="2" fill="#192843"/><circle cx="10" cy="17" r="2" fill="#192843"/>',
    check:'<path d="m5 12 4.2 4.2L19 7"/>',
    basket:'<path d="M4 10h16l-2 9H6zM8 10l4-6 4 6"/>',
    lock:'<rect x="6" y="10" width="12" height="9" rx="2"/><path d="M9 10V8a3 3 0 0 1 6 0v2"/>',
    pin:'<path d="M18 10c0 5-6 9-6 9s-6-4-6-9a6 6 0 1 1 12 0Z"/><circle cx="12" cy="10" r="2"/>',
    next:'<path d="M5 12h14m-5-5 5 5-5 5"/>',
  };
  return `<svg xmlns="http://www.w3.org/2000/svg" width="96" height="96" viewBox="0 0 24 24"><g fill="none" stroke="${color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">${paths[id]}</g></svg>`;
}
export function icon(s,a,id,x,y,d,color=C.ice){
  return pic(s,a,iconFile(id,color),x,y,d,d,id);
}
const chartText={fontSize:20,fill:C.dim,typeface:FONT};
const common={chartFill:'none',plotAreaFill:'none',chartLine:silent,plotAreaLine:silent,hasLegend:false};
export function ring(s,x,y,d,name,labels,values,colors,hole=76){
  const chart=s.charts.add('doughnut',{...common,position:frame(x,y,d,d),categories:labels,
    series:[{name,values,points:values.map((_,idx)=>({idx,fill:colors[idx],line:silent}))}],
    doughnutOptions:{holeSize:hole,firstSliceAngle:270}});
  // LibreOffice uses a smaller default hole. Reserve the centre for the label in both renderers.
  const center=d*.9*hole/100;
  dot(s,x+(d-center)/2,y+(d-center)/2,center,C.panel);
  return chart;
}
export function profitLine(s,x,y,w,h,categories,values){
  const min=Math.min(-6,2*Math.floor(Math.min(...values)/2));
  const max=Math.max(2,2*Math.ceil(Math.max(...values)/2));
  const majorUnit=2*Math.max(1,Math.ceil((max-min)/8));
  return s.charts.add('line',{...common,position:frame(x,y,w,h),categories,
    series:[{name:'Безубыточность',values:values.map(()=>0),line:{style:'dashed',fill:'#A4B4DD',width:1.4}},
      {name:'Результат за первый год, млн ₽',values,line:{style:'solid',fill:C.ice,width:4},marker:{symbol:'circle',size:8,fill:C.ice}}],
    lineOptions:{smooth:false},
    xAxis:{visible:true,tickLabelPosition:'low',textStyle:chartText,line:silent},
    yAxis:{visible:true,min,max,majorUnit,numberFormatCode:'0;−0;0',textStyle:chartText,line:silent,majorGridlines:{style:'solid',fill:'#395074',width:1}}});
}
export function scenarioChart(s,x,y,w,h,e){
  const max=Math.ceil(Math.max(...e.scenarios.flatMap(v=>[v.order_lift,v.seller_lift]))*1.176);
  return s.charts.add('bar',{...common,position:frame(x,y,w,h),categories:e.scenarios.map(v=>v.label),
    series:[{name:'Прирост заказов',values:e.scenarios.map(v=>v.order_lift),fill:C.blue},
      {name:'Прирост сообществ с заказом',values:e.scenarios.map(v=>v.seller_lift),fill:C.ice}],
    barOptions:{direction:'column',grouping:'clustered',gapWidth:66,overlap:-14},
    xAxis:{visible:true,tickLabelPosition:'low',textStyle:chartText,line:silent},
    yAxis:{visible:false,min:0,max,line:silent,majorGridlines:null},
    dataLabels:{showValue:true,position:'outEnd',numberFormatCode:'+0',textStyle:{fontSize:23,typeface:DISPLAY,fill:C.ink}}});
}
