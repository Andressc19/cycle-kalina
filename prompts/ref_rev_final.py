import sys
sys.path.insert(0,'scripts/sens1'); sys.path.insert(0,'scripts/sens2')
import pandas as pd, numpy as np
R='resultados/2026-10-17_sens2_P%d/'
d=pd.read_csv(R%2+'p2_dataset_dedup.csv'); k=d[d.kalina&d.eta_pct.notna()]
F=[]
def chk(c,m):
    print(("OK    " if c else "FALLA ")+m)
    if not c: F.append(m)
env=pd.read_csv(R%4+'p4_envolventes.csv'); e=env[env.centro=='todos']
def g(q,col,conj='KALINA (total)'): return float(e[(e.cantidad==q)&(e.conjunto==conj)].iloc[0][col])
chk(abs(g('Qi_mb','p5')-228.8)<0.5 and abs(g('Qi_mb','p95')-1695.3)<0.5,'E6 Qi 229-1695')
chk(abs(g('Wp_Wt','p5')-0.0238)<5e-4 and abs(g('Wp_Wt','p95')-0.3014)<5e-4 and abs(g('Wp_Wt','p50')-0.060)<1e-3,'E7 Wp/Wt 2.4-30, med 6.0')
chk(abs(g('Wp_Wt','p5','10 % de KALINA (total) con mayor eta')-0.0272)<5e-4 and abs(g('Wp_Wt','p95','10 % de KALINA (total) con mayor eta')-0.0781)<5e-4,'E7 top10 2.7-7.8')
chk(abs(g('Qout_mb','p50')-721.2)<0.5,'E5 Qout med 721')
chk(abs(g('aprox_cond_sal','p5')-2.6)<0.1 and abs(g('aprox_cond_sal','p95')-23.4)<0.1,'E5 aprox 2.6-23.4')
chk(abs(g('q4','p50','10 % de KALINA (total) con mayor eta')-0.9355)<1e-3,'E3 q4 top10 0.9355')
# M-conclusions
def pt(i): return d[d.id_punto==i].iloc[0]
a=pt('C1-B3-0127'); chk(abs(a.eta_pct-14.01)<0.01 and a.P_alta==5000 and a.P_baja==600,'M2 C1-B3-0127')
a=pt('C1-B5-0228'); chk(abs(a.eta_pct-13.95)<0.01 and a.eta_t==0.95 and a.eps_reg==0.95 and a.P_alta==3300,'M3')
a=pt('N7B-C4-B1-045'); chk(abs(a.eta_pct-13.23)<0.01 and a.T_fuente==423.15 and a.P_baja==800,'M4 C4')
a=pt('C2-LHS-0005'); chk(abs(a.eta_pct-12.37)<0.01 and not a.fuera_rango,'M4 C2')
chk(abs(k[~k.fuera_rango].eta_pct.max()-14.53)<0.01 and abs(k[k.fuera_rango].eta_pct.max()-14.82)<0.01,'M1 maximos')
chk(abs(k.eta_pct.median()-7.73)<0.01 and abs(k.eta_pct.quantile(.9)-11.53)<0.01,'M1 mediana y P90')
chk(abs(k.fuera_rango.mean()-0.15)<0.005,'L4 15 % fuera')
# L1 / zonas grises / L3
zg=pd.read_csv(R%1+'p1_zonas_grises.csv'); chk(len(zg)==255 and (zg.dominante=='viol_O2').sum()==249,'L1 255 zonas, 249 O2')
dist=pd.read_csv(R%2+'p2_distancia.csv'); chk(len(dist)==968,'L2 968 CORREGIBLE con vecino')
chk(abs((dist.nvars_diff==1).mean()-0.4928)<0.002,'L2 49 % a una variable')
# D4 eps_cond minimos
for c,v in (('C1 Husavik',0.80),('C2 ancla A*',0.65),('C3 caliente 150 C',0.85),('C4 frio 110 C',0.85)):
    chk(abs(k[k.centro==c].eps_cond.min()-v)<1e-9,'D4 eps_cond min '+c)
# F6
cor=d[d.clasificacion=='CORREGIBLE']; chk(abs(cor.eta_pct.median()-10.20)<0.01 and abs(k.eta_pct.median()-7.73)<0.01,'F6 medianas')
# conclusiones: 32, categorias, sin terminos prohibidos
c=pd.read_csv(R%5+'p5_conclusiones.csv'); chk(len(c)==41 and c.id.is_unique,'41 conclusiones, ids unicos')
txt=' '.join(c.astype(str).values.ravel()).lower()
chk(not any(w in txt for w in ['confiable','no citable','fuera de rango del motor','sin respaldo','indicio','extrapol']),'terminologia en conclusiones')
print('\nFALLAS:',len(F))
