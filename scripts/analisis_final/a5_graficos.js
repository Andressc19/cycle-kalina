/* A5 · Tablero Kalina — gráficos Chart.js (C1: creación perezosa y resize al mostrar). */
"use strict";
const PEND={};
function visible(id){const s=document.getElementById(id).closest(".sec");return !!s&&s.classList.contains("activa");}
function pinta(id,cfg){
  if(!visible(id)){PEND[id]=cfg;return null;}
  const el=document.getElementById(id);
  if(el.__ch){el.__ch.data=cfg.data;el.__ch.options=cfg.options;el.__ch.update("none");return el.__ch;}
  el.__ch=new Chart(el,cfg);return el.__ch;
}
function activarSec(id){
  document.querySelectorAll(".pest-btn").forEach((o)=>o.classList.toggle("activa",o.dataset.sec===id));
  document.querySelectorAll(".sec").forEach((o)=>o.classList.toggle("activa",o.id===id));
  requestAnimationFrame(()=>{
    for(const k of Object.keys(PEND)){
      if(visible(k)){const el=document.getElementById(k);el.__ch=new Chart(el,PEND[k]);delete PEND[k];}
    }
    document.querySelectorAll("#"+id+" canvas").forEach((c)=>{if(c.__ch)c.__ch.resize();});
  });
}
function cfgDisp(ps,xc,yc){
  const ds=[];
  for(const c of CLASES){
    const sub=sel(ps,(p)=>p.clase_trazo===c); if(!sub.length) continue;
    const data=[], bg=[], bd=[], bw=[];
    for(const p of sub){
      const x=coord(p,xc), y=coord(p,yc); if(x===null||y===null) continue;
      data.push({x:x,y:y,id:p.id_punto,clase:c,eta:p.eta_pct});
      const fr=p.fuera_rango===true; bg.push(fr?"rgba(0,0,0,0)":col(c)); bd.push(col(c)); bw.push(fr?1.5:0);
    }
    if(!data.length) continue;
    ds.push({label:etq(c)+" (n = "+data.length+")",data:data,pointStyle:forma(c),pointRadius:5,pointHoverRadius:7,pointBackgroundColor:bg,pointBorderColor:bd,pointBorderWidth:bw});
  }
  return {type:"scatter",data:{datasets:ds},options:{responsive:true,maintainAspectRatio:false,animation:false,
    scales:{x:{title:{display:true,text:nom(xc)}},y:{title:{display:true,text:nom(yc)}}},
    plugins:{legend:{position:"bottom",labels:{boxWidth:12}},tooltip:{callbacks:{
      title:(it)=>it[0].raw.id,
      label:(it)=>{const r=it.raw;return [etq(r.clase),sinComa(xc)+": "+dec(r.x,2),sinComa(yc)+": "+dec(r.y,2),"η: "+(esNulo(r.eta)?"—":dec(r.eta,2)+" %")];}}}}}};
}
function cfgResumen(casos){
  const ds=CLASES.map((c)=>({label:etq(c),backgroundColor:col(c),data:casos.map((id)=>sel(D.PUNTOS,(p)=>p.id_caso===id&&p.clase_trazo===c).length)}));
  return {type:"bar",data:{labels:casos,datasets:ds},options:{indexAxis:"y",responsive:true,maintainAspectRatio:false,animation:false,
    scales:{x:{stacked:true,title:{display:true,text:"Número de corridas"}},y:{stacked:true}},plugins:{legend:{position:"bottom",labels:{boxWidth:12}}}}};
}
function cfgBloqueos(ps){
  const b=bloqueos(ps);
  return {type:"bar",data:{labels:b.nombres,datasets:[{label:"Puntos que incumplen",data:b.c,backgroundColor:"#C62828"}]},
    options:{responsive:true,maintainAspectRatio:false,animation:false,scales:{y:{beginAtZero:true,title:{display:true,text:"Número de puntos"}}},plugins:{legend:{display:false}}}};
}
