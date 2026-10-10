/* A5 · Tablero Kalina — lógica del tablero (Chart.js 4, sin frameworks). */
"use strict";
const D=DATOS, $=(s)=>document.querySelector(s);
const CLASES=["KALINA","CORREGIBLE","INVIABLE","NO_CONVERGIO","N2","OMITIDO"];
const VARS=["T_fuente","T_sumidero","P_alta","P_baja","x_b","m_b","eta_t","eta_p","eps_hrvg","eps_reg","eps_cond","T_amb_diseno","motor"];
const PLOT=["T_fuente","T_sumidero","P_alta","P_baja","x_b","eta_t","eta_p","eps_hrvg","eps_reg","eps_cond","T_amb_diseno"];
const DERIV=["dP","rP","eta_pct"];
const NOMBRE=D.NOMBRE||{}, nom=(c)=>NOMBRE[c]||c, sinComa=(c)=>String(nom(c)).split(",")[0];
const etq=(c)=>(D.ETIQUETA_CLASE||{})[c]||c, col=(c)=>(D.COLOR_CLASE||{})[c]||"#555", forma=(c)=>(D.FORMA_CLASE||{})[c]||"circle";
const esc=(s)=>String(s==null?"":s).replace(/[&<>"]/g,(c)=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const esNulo=(v)=>v===null||v===undefined||(typeof v==="number"&&isNaN(v));
const dec=(v,d)=>esNulo(v)?"—":Number(v).toLocaleString("es-CO",{minimumFractionDigits:d,maximumFractionDigits:d});
const sig=(v)=>esNulo(v)?"—":Number(v).toLocaleString("es-CO",{maximumSignificantDigits:5});
const fmt=(v)=>typeof v==="string"?(v.trim()!==""&&!isNaN(Number(v))?sig(Number(v)):v):sig(v);
const iniS=(v)=>typeof v==="string"&&v.trim().toLowerCase().charAt(0)==="s";
const iniN=(v)=>typeof v==="string"&&v.trim().toLowerCase().charAt(0)==="n";
function sel(a,f){const o=[];for(let i=0;i<a.length;i++)if(f(a[i]))o.push(a[i]);return o;}
function uno(a,f){for(let i=0;i<a.length;i++)if(f(a[i]))return a[i];return null;}
const BLOQUES=D.BLOQUES||[], COND=D.CONDICIONES||[];
const est={bloque:"",subcaso:"",clases:new Set(CLASES),conf:false,wnet:false,x:"",y:"",pag:0,orden:{c:null,dir:1}};
const subsDe=(b)=>String(b.id_subcasos).split(";").map((s)=>s.trim()).filter(Boolean);
const ordCaso=(a,b)=>{const A=a.match(/M(\d+)(.*)$/),B=b.match(/M(\d+)(.*)$/);return parseInt(A[1],10)-parseInt(B[1],10)||A[2].localeCompare(B[2]);};
/* --- condiciones del bloque --- */
function condBloque(){
  const b=uno(BLOQUES,(x)=>x.bloque_director===est.bloque), subs=subsDe(b);
  const rows=sel(COND,(c)=>subs.indexOf(c.id_subcaso)>=0);
  const oat=rows.length>0&&sel(rows,(r)=>!iniS(r.es_oat)).length===0, fijos=[], barr=[];
  for(const v of VARS){
    const rv=sel(rows,(r)=>r.variable===v); if(!rv.length) continue;
    const es=rv.map((r)=>r.estado);
    if(sel(es,(e)=>e!=="fijo").length===0){
      const vals=[...new Set(rv.map((r)=>r.valor_fijo))];
      if(vals.length===1) fijos.push({v:v,val:vals[0],u:rv[0].unidad,ig:rv[0].igual_al_profesor});
    }
    if(es.indexOf("barrido")>=0){
      const rb=sel(rv,(r)=>r.estado==="barrido");
      const los=sel(rb.map((r)=>r.min),(x)=>!esNulo(x)), his=sel(rb.map((r)=>r.max),(x)=>!esNulo(x)), ns=sel(rb.map((r)=>r.n_valores),(x)=>!esNulo(x));
      barr.push({v:v,lo:Math.min.apply(null,los),hi:Math.max.apply(null,his),n:Math.max.apply(null,ns),u:rb[0].unidad});
    }
  }
  return {b:b,subs:subs,oat:oat,fijos:fijos,barr:barr};
}
function opcionesEje(cb){
  const out=[];
  for(const x of cb.barr) if(PLOT.indexOf(x.v)>=0) out.push({v:x.v,t:nom(x.v)});
  for(const d of DERIV) out.push({v:d,t:nom(d)});
  return out;
}
function medir(id,ops,val){const s=$(id);s.innerHTML=ops.map((o)=>'<option value="'+esc(o.v)+'">'+esc(o.t)+"</option>").join("");if(val!=null)s.value=val;}
function hayGenuinos(bl){return D.PUNTOS.some((p)=>p.bloque_director===bl&&p.genuino);}
function cargarBloque(){
  const b=uno(BLOQUES,(x)=>x.bloque_director===est.bloque), subs=subsDe(b);
  $("#sel-subcaso").innerHTML='<option value="">Todos los del bloque</option>'+subs.map((s)=>'<option value="'+esc(s)+'">'+esc(s)+"</option>").join("");
  est.subcaso="";
  const cb=condBloque(), ops=opcionesEje(cb), plot=sel(cb.barr.map((x)=>x.v),(v)=>PLOT.indexOf(v)>=0);
  est.x=plot[0]||"eta_pct";
  est.y=hayGenuinos(est.bloque)?"eta_pct":(plot[1]||"eta_pct");
  if(est.y===est.x) est.y=est.x==="eta_pct"?"dP":"eta_pct";
  medir("#sel-x",ops,est.x); medir("#sel-y",ops,est.y); renderTodo();
}
/* --- selección de puntos --- */
function puntos(){
  const cb=condBloque();
  let ps=sel(D.PUNTOS,(p)=>p.bloque_director===est.bloque);
  if(est.subcaso) ps=sel(ps,(p)=>p.id_subcaso===est.subcaso);
  ps=sel(ps,(p)=>est.clases.has(p.clase_trazo));
  if(est.conf) ps=sel(ps,(p)=>p.kalina_confiable);
  if(est.wnet) ps=sel(ps,(p)=>p.wnet_pos);
  if(cb.oat&&PLOT.indexOf(est.x)>=0) ps=sel(ps,(p)=>p.variable===est.x);
  return ps;
}
function coord(p,c){if(c==="eta_pct")return (p.genuino&&p.wnet_pos)?p.eta_pct:null;return esNulo(p[c])?null:p[c];}
function bloqueos(ps){
  const keys=["viol_O1","viol_O2","viol_O3","viol_O5"], nombres=["O1 título","O2 cavitación","O3 trabajo neto","O5 separador"];
  const g=sel(ps,(p)=>p.genuino&&p.clase_trazo!=="KALINA");
  const c=keys.map((k)=>sel(g,(p)=>!esNulo(p[k])&&p[k]>0).length);
  let im=0; for(let i=1;i<c.length;i++) if(c[i]>c[im]) im=i;
  return {claves:keys,nombres:nombres,c:c,im:im};
}
function kpisHTML(ps){
  const g=sel(ps,(p)=>p.genuino).length, k=sel(ps,(p)=>p.clase_trazo==="KALINA").length, kc=sel(ps,(p)=>p.kalina_confiable).length;
  const etas=sel(ps,(p)=>p.clase_trazo==="KALINA"&&!esNulo(p.eta_pct)).map((p)=>p.eta_pct), emax=etas.length?Math.max.apply(null,etas):null;
  const bl=bloqueos(ps), crit=bl.c[bl.im]>0?bl.nombres[bl.im]:"ninguno";
  return [["Corridas",dec(ps.length,0)],["Puntos genuinos",dec(g,0)],["KALINA",dec(k,0)],["KALINA confiables",dec(kc,0)],["η máx. KALINA",esNulo(emax)?"—":dec(emax,2)+" %"],["Criterio que más bloquea",crit]]
    .map((a)=>'<div class="kpi"><div class="v">'+a[1]+'</div><div class="t">'+a[0]+"</div></div>").join("");
}
/* --- pie y panel de condiciones --- */
function barrido(var_,lo,hi,n,u){const us=u&&u!=="–"?" "+u:"";return esNulo(lo)?var_+" ("+n+" valores)":var_+" ["+sig(lo)+"–"+sig(hi)+"]"+us+" ("+n+" valores)";}
function unidadDe(var_,u){return (var_==="motor"||u==="–"||esNulo(u))?"":u;}
function pieTexto(ps){
  const cb=condBloque(), rows=sel(COND,(c)=>cb.subs.indexOf(c.id_subcaso)>=0);
  const fijos=[], barr=cb.barr.map((x)=>barrido(x.v,x.lo,x.hi,x.n,unidadDe(x.v,x.u)));
  if(cb.oat){
    for(const v of VARS){
      const rv=sel(rows,(r)=>r.variable===v); if(!rv.length) continue;
      if(sel(rv,(r)=>r.estado!=="sin_dato").length===0) continue;
      const val=(v==="motor")?rv[0].valor_fijo:(!esNulo(rv[0].valor_base)?rv[0].valor_base:rv[0].valor_fijo);
      if(esNulo(val)||String(val).trim()==="") continue;
      fijos.push(v+" = "+(v==="motor"?val:sig(val))+(unidadDe(v,rv[0].unidad)?" "+unidadDe(v,rv[0].unidad):""));
    }
  }else{
    for(const v of VARS){
      const rv=sel(rows,(r)=>r.variable===v); if(!rv.length) continue;
      if(sel(rv,(r)=>r.estado!=="fijo").length===0){
        const vals=[...new Set(rv.map((r)=>r.valor_fijo))];
        if(vals.length===1) fijos.push(v+" = "+(v==="motor"?vals[0]:sig(vals[0]))+(unidadDe(v,rv[0].unidad)?" "+unidadDe(v,rv[0].unidad):""));
      }
    }
  }
  const filtros=["bloque "+est.bloque,est.subcaso||"todos los subcasos del bloque","clases: "+[...est.clases].join(", ")];
  if(est.conf) filtros.push("solo KALINA confiables");
  if(est.wnet) filtros.push("solo W_net > 0");
  const lineas=cb.oat
    ? ["Punto base (las demás variables quedan fijas en): "+(fijos.length?fijos.join("; "):"ninguno")+". Cada panel o tramo mueve solo su variable.",
       "Datos barridos (uno a la vez): "+(barr.length?barr.join("; "):"ninguno")+"."]
    : ["Datos fijos: "+(fijos.length?fijos.join("; "):"ninguno")+".","Datos barridos: "+(barr.length?barr.join("; "):"ninguno")+"."];
  return ["Caso(s): "+cb.subs.join(", ")+" (bloque "+est.bloque+")."].concat(lineas)
    .concat(["Filtro: "+filtros.join("; ")+".","n = "+ps.length+". Fuente: todos_los_puntos.csv."]).join("\n");
}
function renderCond(){
  const cb=condBloque();
  $("#titulo-cond").textContent=cb.oat?"Punto base: las demás variables quedan fijas en estos valores mientras se mueve una":"Condiciones de este bloque";
  $("#aviso-cond").innerHTML=(iniN(cb.b.consistente)&&!esNulo(cb.b.diferencias))?'<p class="aviso"><b>Bloque con condiciones distintas:</b> '+esc(cb.b.diferencias)+"</p>":"";
  let filas;
  if(cb.oat){
    filas=[];
    for(const v of VARS){
      const rv=sel(COND,(c)=>cb.subs.indexOf(c.id_subcaso)>=0&&c.variable===v);
      if(!rv.length||sel(rv,(r)=>r.estado!=="sin_dato").length===0) continue;
      filas.push({v:v,val:!esNulo(rv[0].valor_base)?rv[0].valor_base:rv[0].valor_fijo,u:rv[0].unidad,ig:rv[0].igual_al_profesor});
    }
  }else filas=cb.fijos;
  let h='<table><thead><tr><th>Variable</th><th>Valor</th><th>Unidad</th></tr></thead><tbody>';
  for(const f of filas){const dif=iniN(f.ig);h+="<tr"+(dif?' class="resalta"':"")+"><td>"+esc(sinComa(f.v))+"</td><td>"+(dif?"<b>"+esc(fmt(f.val))+'</b><span class="ast" aria-hidden="true">*</span>':esc(fmt(f.val)))+"</td><td>"+esc(unidadDe(f.v,f.u)||"–")+"</td></tr>";}
  h+="</tbody></table><p class=\"ayuda\">* valor distinto del punto del profesor.</p>";
  $("#tabla-cond").innerHTML=filas.length?h:'<p class="ayuda">Sin variables fijas detectadas.</p>';
  $("#pp-cond").textContent="Punto base: "+(cb.b.punto_base||"—");
  $("#lista-barridos").innerHTML=cb.barr.length?"<h3>Variables barridas</h3><ul>"+cb.barr.map((x)=>"<li>"+esc(sinComa(x.v))+": "+esc(sig(x.lo))+" – "+esc(sig(x.hi))+" "+esc(unidadDe(x.v,x.u))+" ("+x.n+" valores)</li>").join("")+"</ul>":"";
}
/* --- tabla de puntos y CSV --- */
function celda(p,k){
  if(k==="clase_trazo") return '<span class="chip" style="background:'+col(p.clase_trazo)+'">'+esc(etq(p.clase_trazo))+"</span>";
  if(k==="fuera_rango") return p.fuera_rango===true?"sí":"no";
  if(k==="eta_pct") return dec(p.eta_pct,2);
  if(k==="Wnet") return esNulo(p.Wnet)?"—":dec(p.Wnet,1);
  if(k==="dP") return dec(p.dP,0);
  if(k==="rP") return dec(p.rP,2);
  return esNulo(p[k])?"—":sig(p[k]);
}
function renderTabla(){
  const cb=condBloque(), barrVars=sel(cb.barr.map((x)=>x.v),(v)=>PLOT.indexOf(v)>=0);
  const cols=[{k:"id_punto",t:"id_punto"},{k:"clase_trazo",t:"Clase"}]
    .concat(barrVars.map((v)=>({k:v,t:sinComa(v)+" ["+(uno(cb.barr,(x)=>x.v===v).u||"")+"]"})))
    .concat([{k:"eta_pct",t:"η [%]"},{k:"Wnet",t:"W_net [kW]"},{k:"dP",t:"ΔP [kPa]"},{k:"rP",t:"r_P [–]"},{k:"fuera_rango",t:"Fuera de rango"}]);
  const arr=puntos().slice(), oc=est.orden;
  if(oc.c) arr.sort((a,b)=>{const va=oc.c==="clase_trazo"?a.clase_trazo:a[oc.c],vb=oc.c==="clase_trazo"?b.clase_trazo:b[oc.c];if(typeof va==="number"&&typeof vb==="number")return (va-vb)*oc.dir;return String(va==null?"":va).localeCompare(String(vb==null?"":vb))*oc.dir;});
  const por=50, np=Math.max(1,Math.ceil(arr.length/por)); if(est.pag>np-1) est.pag=np-1;
  const ini=est.pag*por, fin=Math.min(ini+por,arr.length);
  let h="<table><thead><tr>";
  for(const c of cols) h+='<th class="ord" data-c="'+c.k+'">'+esc(c.t)+(oc.c===c.k?(oc.dir>0?" ↑":" ↓"):"")+"</th>";
  h+="</tr></thead><tbody>";
  for(let i=ini;i<fin;i++){h+="<tr>";for(const c of cols) h+="<td>"+celda(arr[i],c.k)+"</td>";h+="</tr>";}
  h+="</tbody></table>";
  $("#tabla-puntos").innerHTML=arr.length?h:'<p class="ayuda">Sin puntos con estos filtros.</p>';
  document.querySelectorAll("#tabla-puntos th.ord").forEach((th)=>th.addEventListener("click",()=>{const k=th.dataset.c;if(est.orden.c===k)est.orden.dir*=-1;else{est.orden.c=k;est.orden.dir=1;}est.pag=0;renderTabla();}));
  $("#paginacion").innerHTML=arr.length?'<button id="pg-prev"'+(est.pag<=0?" disabled":"")+">Anterior</button>"+'<span class="info">Página '+(est.pag+1)+" de "+np+" · "+arr.length+' puntos</span><button id="pg-next"'+(est.pag>=np-1?" disabled":"")+">Siguiente</button>":"";
  if($("#pg-prev")) $("#pg-prev").addEventListener("click",()=>{est.pag=Math.max(0,est.pag-1);renderTabla();});
  if($("#pg-next")) $("#pg-next").addEventListener("click",()=>{est.pag=Math.min(np-1,est.pag+1);renderTabla();});
}
function csv(){
  const cb=condBloque(), barrVars=sel(cb.barr.map((x)=>x.v),(v)=>PLOT.indexOf(v)>=0);
  const cols=["id_punto","clase_trazo"].concat(barrVars).concat(["eta_pct","Wnet","dP","rP","fuera_rango"]);
  let s=cols.join(";")+"\n";
  for(const p of puntos()) s+=cols.map((c)=>{const v=c==="clase_trazo"?etq(p.clase_trazo):p[c];return v==null?"":String(v).replace(/;/g,",");}).join(";")+"\n";
  const a=document.createElement("a");
  a.href=URL.createObjectURL(new Blob(["\ufeff"+s],{type:"text/csv;charset=utf-8"})); a.download="puntos_filtro.csv";
  document.body.appendChild(a); a.click(); document.body.removeChild(a); URL.revokeObjectURL(a.href);
}
/* --- pestañas 1 y 3 --- */
function renderResumen(){
  const ps=D.PUNTOS, g=sel(ps,(p)=>p.genuino).length, kc=sel(ps,(p)=>p.kalina_confiable).length;
  const casos=[...new Set(ps.map((p)=>p.id_caso))].sort(ordCaso);
  $("#kpi-resumen").innerHTML=[["Corridas totales",dec(ps.length,0)],["Puntos genuinos",dec(ps.length?100*g/ps.length:0,1)+" %"],["KALINA confiables",dec(kc,0)],["Casos",dec(casos.length,0)]]
    .map((a)=>'<div class="kpi"><div class="v">'+a[1]+'</div><div class="t">'+a[0]+"</div></div>").join("");
  pinta("graf-resumen",cfgResumen(casos)); renderMatriz();
}
function renderMatriz(){
  const subs=[...new Set(COND.map((c)=>c.id_subcaso))];
  let h="<table><thead><tr><th>Subcaso</th>";
  for(const v of VARS) h+="<th>"+esc(v)+"</th>";
  h+="</tr></thead><tbody>";
  for(const s of subs){
    const oat=sel(COND,(c)=>c.id_subcaso===s&&iniS(c.es_oat)).length>0;
    h+="<tr><td>"+esc(s)+(oat?" (una variable a la vez)":"")+"</td>";
    for(const v of VARS){
      const r=uno(COND,(c)=>c.id_subcaso===s&&c.variable===v);
      if(!r||r.estado==="sin_dato"){
        if(r&&v==="T_amb_diseno"&&/^KF-M0[123]/.test(r.id_caso||"")) h+='<td><span class="sin">300,03 K (por protocolo)</span></td>';
        else h+='<td><span class="sin">—</span></td>';
      }
      else if(r.estado==="barrido") h+=oat?'<td><span class="oat">una a la vez</span></td>':'<td><span class="barrida">barrida</span></td>';
      else if(iniS(r.igual_al_profesor)) h+='<td><span class="igual">= profesor</span></td>';
      else h+='<td><span class="fijo">'+esc(fmt(r.valor_fijo))+(r.unidad&&r.unidad!=="–"?" "+esc(r.unidad):"")+"</span></td>";
    }
    h+="</tr>";
  }
  $("#matriz").innerHTML=h+"</tbody></table>";
}
function renderGlosario(){const g=D.GLOSARIO||{};$("#glosario").innerHTML=Object.keys(g).map((k)=>"<dt>"+esc(k)+"</dt><dd>"+esc(g[k])+"</dd>").join("");}
function renderCasos(){
  const cols=[["id_caso","Caso"],["n_puntos","Corridas"],["genuinos","Genuinas"],["kalina","KALINA"],["kalina_confiables","KALINA confiables"],["corregible","Corregibles"],["invariable","Inviables"],["no_convergio","No convergió"],["n2","N2"],["omitidos","Omitidos"],["fuera_rango","Fuera de rango"]];
  let h="<table><thead><tr>"+cols.map((c)=>"<th>"+esc(c[1])+"</th>").join("")+"</tr></thead><tbody>";
  for(const r of D.CASOS) h+="<tr>"+cols.map((c)=>"<td>"+(c[0]==="id_caso"?esc(r[c[0]]):dec(r[c[0]],0))+"</td>").join("")+"</tr>";
  $("#tabla-casos").innerHTML=h+"</tbody></table>";
}
/* --- arranque --- */
function renderTodo(){
  renderCond();
  const ps=puntos(), cb=condBloque();
  $("#kpi-filtro").innerHTML=kpisHTML(ps);
  $("#kpi-nota").textContent=cb.oat
    ? "Cifras de los puntos donde se mueve "+nom(est.x)+"; las demás variables están en el punto base."
    : "";
  pinta("graf-disp",cfgDisp(ps,est.x,est.y)); pinta("graf-bloq",cfgBloqueos(ps));
  $("#pie-disp").textContent=pieTexto(ps);
  est.pag=0; renderTabla();
}
function init(){
  $("#sel-bloque").innerHTML=BLOQUES.map((b)=>'<option value="'+esc(b.bloque_director)+'">'+esc(b.bloque_director+" · "+(b.id_casos||"")+" · "+(b.descripcion||b.bloque_director))+"</option>").join("");
  $("#chk-clases").innerHTML='<legend>Clase del ciclo</legend>'+CLASES.map((c)=>'<label><input type="checkbox" class="cc" value="'+c+'" checked><span class="punto" style="background:'+col(c)+'"></span>'+esc(etq(c))+"</label>").join("");
  document.querySelectorAll(".cc").forEach((ch)=>ch.addEventListener("change",()=>{est.clases=new Set(sel([...document.querySelectorAll(".cc")],(x)=>x.checked).map((x)=>x.value));est.pag=0;renderTodo();}));
  $("#sel-bloque").addEventListener("change",(e)=>{est.bloque=e.target.value;cargarBloque();});
  $("#sel-subcaso").addEventListener("change",(e)=>{est.subcaso=e.target.value;est.pag=0;renderTodo();});
  $("#sel-x").addEventListener("change",(e)=>{est.x=e.target.value;est.pag=0;renderTodo();});
  $("#sel-y").addEventListener("change",(e)=>{est.y=e.target.value;est.pag=0;renderTodo();});
  $("#chk-conf").addEventListener("change",(e)=>{est.conf=e.target.checked;est.pag=0;renderTodo();});
  $("#chk-wnet").addEventListener("change",(e)=>{est.wnet=e.target.checked;est.pag=0;renderTodo();});
  $("#btn-csv").addEventListener("click",csv);
  document.querySelectorAll(".pest-btn").forEach((b)=>b.addEventListener("click",()=>activarSec(b.dataset.sec)));
  renderResumen(); renderGlosario(); renderCasos();
  est.bloque=BLOQUES.length?BLOQUES[0].bloque_director:"";
  cargarBloque();
}
document.addEventListener("DOMContentLoaded",init);
