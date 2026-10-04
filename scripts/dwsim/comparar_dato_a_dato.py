"""Comparación dato a dato por ciclo KALINA: solver del proyecto (motor real) vs DWSIM-PR.

Argumentos: etiquetas. Lee motor_<et>.json y dwsim_<et>.json, escribe estados_<et>.csv y
componentes_<et>.csv, y resumen_ciclos.csv (una fila por ciclo). Entalpía: cada modelo tiene su propio cero, así que h se compara
llevada a una referencia común con la MISMA composición de cada estado:
  h_rel = h − h0L,  h0L = h(P_alta, T0, x_estado)  (líquido; referencia principal)
  h_rel0 = h − h0,  h0  = h(P0, T0, x_estado)      (estado muerto; bifásico aquí)
Las energías por equipo (Q, W) no dependen de la referencia. Solo stdlib.
"""
import csv, json, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "resultados", "2026-10-03_dato_a_dato")
NOM = {1: "salida regenerador frío / entrada HRVG", 2: "salida HRVG / entrada separador",
       3: "vapor rico -> turbina", 4: "salida turbina", 5: "líquido pobre -> regenerador",
       6: "salida regenerador caliente", 7: "salida válvula", 8: "salida absorbedor",
       9: "salida condensador / entrada bomba", 10: "salida bomba"}


def comparar(et):
    mo = json.load(open(os.path.join(OUT, "motor_%s.json" % et)))
    dw = json.load(open(os.path.join(OUT, "dwsim_%s.json" % et)))
    if not dw.get("convergio"):
        print(et, "DWSIM no convergio:", dw.get("error")); return None
    print("\n=====", et, mo["punto"])
    filas = []
    print("%3s %-38s %8s %8s %7s | %7s %7s | %8s %8s %8s | %8s %8s %8s" % (
        "e", "estado", "T_mot", "T_dw", "dT", "x_mot", "x_dw", "m_mot", "m_dw", "dm",
        "hrel_mot", "hrel_dw", "dh"))
    for k in range(1, 11):
        a, b = mo["estados"][str(k)], dw["estados"][str(k)]
        hm, hd = a["h"] - a["h0L"], b["h"] - b["h0L"]
        hm0, hd0 = a["h"] - a["h0"], b["h"] - b["h0"]
        f = dict(estado=k, descripcion=NOM[k], P_kPa=a["P"], T_motor=a["T"], T_dwsim=b["T"], dT=b["T"] - a["T"],
                 x_motor=a["x"], x_dwsim=b["x"], dx=b["x"] - a["x"], m_motor=a["m"], m_dwsim=b["m"], dm=b["m"] - a["m"],
                 hrel_motor=hm, hrel_dwsim=hd, dh_rel=hd - hm,
                 hrel0_motor=hm0, hrel0_dwsim=hd0, dh_rel0=hd0 - hm0,
                 h_abs_motor=a["h"], h_abs_dwsim=b["h"], fase_motor=a.get("fase"), q_motor=a.get("q"),
                 vf_molar_dwsim=b.get("vf_molar"))
        filas.append(f)
        print("%3d %-38s %8.2f %8.2f %+7.2f | %7.4f %7.4f | %8.4f %8.4f %+8.4f | %8.2f %8.2f %+8.2f" % (
            k, NOM[k][:38], a["T"], b["T"], f["dT"], a["x"], b["x"], a["m"], b["m"], f["dm"], hm, hd, f["dh_rel"]))
    e = {k: mo["estados"][str(k)] for k in range(1, 11)}
    g = {k: dw["estados"][str(k)] for k in range(1, 11)}

    def comp(nombre, fn):
        vm, vd = fn(e), fn(g)
        return dict(componente=nombre, motor=vm, dwsim=vd, diferencia=vd - vm,
                    rel_pct=100 * (vd - vm) / vm if vm else float("nan"))
    comps = [
        comp("HRVG  Qi = m1(h2-h1)", lambda s: s[1]["m"] * (s[2]["h"] - s[1]["h"])),
        comp("Turbina  Wt = m3(h3-h4)", lambda s: s[3]["m"] * (s[3]["h"] - s[4]["h"])),
        comp("Bomba  Wp = m9(h10-h9)", lambda s: s[9]["m"] * (s[10]["h"] - s[9]["h"])),
        comp("Regenerador caliente  m5(h5-h6)", lambda s: s[5]["m"] * (s[5]["h"] - s[6]["h"])),
        comp("Regenerador frío  m10(h1-h10)", lambda s: s[10]["m"] * (s[1]["h"] - s[10]["h"])),
        comp("Válvula  h6-h7 [kJ/kg]", lambda s: s[6]["h"] - s[7]["h"]),
        comp("Condensador  Qout = m8(h8-h9)", lambda s: s[8]["m"] * (s[8]["h"] - s[9]["h"])),
        comp("Separador  m2h2-m3h3-m5h5 (debe ser 0)", lambda s: s[2]["m"] * s[2]["h"] - s[3]["m"] * s[3]["h"] - s[5]["m"] * s[5]["h"]),
        comp("Absorbedor  m4h4+m7h7-m8h8 (debe ser 0)", lambda s: s[4]["m"] * s[4]["h"] + s[7]["m"] * s[7]["h"] - s[8]["m"] * s[8]["h"]),
        comp("Wnet = Wt - Wp", lambda s: s[3]["m"] * (s[3]["h"] - s[4]["h"]) - s[9]["m"] * (s[10]["h"] - s[9]["h"])),
    ]
    comps.append(dict(componente="eta [%]", motor=100 * mo["eta"], dwsim=100 * dw["eta"],
                      diferencia=100 * (dw["eta"] - mo["eta"]), rel_pct=100 * (dw["eta"] - mo["eta"]) / mo["eta"]))
    print()
    for c in comps:
        print("%-42s motor=%10.4f  dwsim=%10.4f  dif=%+9.4f  (%+6.2f %%)" % (
            c["componente"], c["motor"], c["dwsim"], c["diferencia"], c["rel_pct"]))
    for nombre, datos in (("estados_%s.csv" % et, filas), ("componentes_%s.csv" % et, comps)):
        with open(os.path.join(OUT, nombre), "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(datos[0])); w.writeheader(); w.writerows(datos)
    liq = [abs(f["dh_rel"]) for f in filas if f["estado"] in (1, 5, 6, 7, 9, 10)]
    vap = [abs(f["dh_rel"]) for f in filas if f["estado"] in (2, 3, 4, 8)]
    c = {x["componente"].split()[0]: x for x in comps}
    return dict(ciclo=et, x_b=mo["punto"]["x_b"], T_fuente=mo["punto"]["T_fuente"],
                P_baja=mo["punto"]["P_baja"], eta_motor=100 * mo["eta"], eta_dwsim=100 * dw["eta"],
                d_eta_pp=100 * (dw["eta"] - mo["eta"]), max_abs_dT=max(abs(f["dT"]) for f in filas),
                max_dh_liquidos=max(liq), max_dh_con_vapor=max(vap),
                dm3_pct=100 * filas[2]["dm"] / filas[2]["m_motor"], dWt_pct=c["Turbina"]["rel_pct"],
                dWp_pct=c["Bomba"]["rel_pct"], dQi_pct=c["HRVG"]["rel_pct"], dQout_pct=c["Condensador"]["rel_pct"],
                cierre_dwsim_kW=dw["cierre"])


if __name__ == "__main__":
    import sys
    res = [r for r in (comparar(et) for et in sys.argv[1:]) if r]
    if res:
        with open(os.path.join(OUT, "resumen_ciclos.csv"), "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(res[0])); w.writeheader(); w.writerows(res)
        print("\n%-10s %5s %4s %8s %8s %7s %6s %7s %7s %7s %7s %7s" % (
            "ciclo", "x_b", "Tf", "eta_mot", "eta_dw", "d_eta", "maxdT", "dh_liq", "dh_vap", "dm3%", "dWt%", "dWp%"))
        for r in res:
            print("%-10s %5.2f %4.0f %7.3f%% %7.3f%% %+6.3f %6.2f %7.2f %7.2f %+7.2f %+7.2f %+7.2f" % (
                r["ciclo"], r["x_b"], r["T_fuente"], r["eta_motor"], r["eta_dwsim"], r["d_eta_pp"],
                r["max_abs_dT"], r["max_dh_liquidos"], r["max_dh_con_vapor"], r["dm3_pct"], r["dWt_pct"], r["dWp_pct"]))
