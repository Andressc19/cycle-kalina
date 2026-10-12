# -*- coding: utf-8 -*-
"""A4 · Checks de validación cruzada V13-V23 (TASK_CONTEXT af-A4).

Segunda parte de los checks; usa los helpers de a4_checks.py (V01-V12).
No corrige nada: solo mide y reporta.
"""
import pandas as pd

from a4_checks import (ESCALERA, T_ETA, T_P, T_RP, Kalina, cerca, fila, num,
                       p5p95)


def v13(df):
    k = Kalina(df[df["id_caso"].isin(["KF-M04", "KF-M04b"])])
    esp = {"P_alta": (2155.69, 4841.78, T_P), "P_baja": (683.165, 1460.71, T_P),
           "dP": (968.027, 3717.63, T_P), "rP": (1.68614, 5.33942, T_RP)}
    filas = []
    for col, (a, b, tol) in esp.items():
        q = p5p95(k, col)
        filas.append(fila("V13", "KF-M04 + KF-M04b", "KALINA", f"p5–p95 {col}",
                          f"[{a}; {b}]", f"[{q[0]:.6g}; {q[1]:.6g}]",
                          cerca(q[0], a, tol) and cerca(q[1], b, tol)))
    return filas


def v14(df):
    c = df[df["id_caso"] == "KF-M04c"]
    n, o = len(c), int(c["omitido"].sum())
    return [fila("V14", "KF-M04c", "todas las filas", "filas; omitidas; evaluadas",
                 "150; 15; 135", f"{n}; {o}; {n - o}", (n, o) == (150, 15))]


def v15(df):
    m = df[df["id_caso"] == "KF-M05"]
    n, o = len(m), int(m["omitido"].sum())
    f = int(m[~m["omitido"]]["fuera_rango"].sum())
    ev = len(m[~m["omitido"]])
    kal = [int(((m["escenario"].astype(str) == str(i)) & (m["clasificacion"] == "KALINA")).sum())
           for i in range(1, 6)]
    return [fila("V15", "KF-M05", "subcasos KF-M05-1…5 = S1…S5",
                 "filas; omitidas; KALINA por esc. (S1→S5); fuera de rango (de evaluadas)",
                 "600; 2; [4,0,0,6,10]; 322 de 598",
                 f"{n}; {o}; {kal}; {f} de {ev}",
                 n == 600 and o == 2 and kal == [4, 0, 0, 6, 10] and f == 322 and ev == 598)]


def v16(df):
    x = df[df["id_caso"] == "KF-M05c"]
    n, k = len(x), int((x["clasificacion"] == "KALINA").sum())
    return [fila("V16", "KF-M05c", "todas las filas", "filas; KALINA", "165; 104",
                 f"{n}; {k}", (n, k) == (165, 104))]


def v17(df):
    p = Kalina(df[df["id_caso"] == "KF-M07"])
    esp = {"A1": 0.1498, "A2": 0.1548, "A3": 0.1274, "A4": 0.1560, "A5": 0.1109}
    filas = []
    for a, e in esp.items():
        v = float(p[p["arranque"] == a]["eta"].max())
        filas.append(fila("V17", f"KF-M07-{a}", "KALINA", "η máx", f"{e:.4f}",
                          f"{v:.4f}", cerca(v, e, T_ETA)))
    return filas


def v18(df):
    m = df[df["id_caso"] == "KF-M09"]
    subs = set(m["id_subcaso"])
    filas = []
    for _, r in pd.read_csv(ESCALERA).iterrows():
        sub = "KF-M09-R{}-{}".format(int(r["ronda"]), str(r["conservados"]).replace("+", "_"))
        esp = [int(r[c]) for c in ("n_eval", "n_genuinos", "n_kalina", "n_kalina_confiable")]
        if sub not in subs:
            filas.append(fila("V18", sub, "m9_escalera.csv", "n; genuinas; KALINA; confiables",
                              "; ".join(map(str, esp)), "(subcaso ausente)", None,
                              nota="subcaso no encontrado en la tabla canónica"))
            continue
        g = m[m["id_subcaso"] == sub]
        rec = [len(g), int(g["genuino"].sum()), int((g["clasificacion"] == "KALINA").sum()),
               int(g["kalina_confiable"].sum())]
        filas.append(fila("V18", sub,
                          "ronda {}, conservados {}".format(int(r["ronda"]), r["conservados"]),
                          "n; genuinas; KALINA; confiables",
                          "; ".join(map(str, esp)), "; ".join(map(str, rec)), rec == esp))
    return filas


def v19(df):
    k = Kalina(df[df["id_subcaso"] == "KF-M09-R3-x_b+P_alta+eficiencias+P_baja"])
    n, c = len(k), int(k["kalina_confiable"].sum())
    tf, ts = num(k["T_fuente"]).round().astype(int), num(k["T_sumidero"]).round().astype(int)
    ok = n == 5 and c == 5 and tf.between(391, 409).all() and ts.between(280, 293).all()
    return [fila("V19", "KF-M09-R3-x_b+P_alta+eficiencias+P_baja", "KALINA", "n; confiables; T redondeadas",
                 "5; 5; T_fuente [391,409] K; T_sumidero [280,293] K",
                 f"{n}; {c}; T_fuente [{tf.min()},{tf.max()}]; T_sumidero [{ts.min()},{ts.max()}]", ok)]


def v20(df):
    con_tf = df[(df["id_caso"] == "KF-M09") & df["conservados"].astype(str).str.contains("TF")]
    c = int(con_tf["kalina_confiable"].sum())
    return [fila("V20", "KF-M09", "conservados que incluyen TF", "KALINA confiables",
                 "0 en todas las rondas", f"{c}", c == 0,
                 nota="Subcasos: " + ", ".join(sorted(con_tf["id_subcaso"].unique())))]


def v21(df):
    g = df[df["id_subcaso"] == "KF-M10-F3"]
    n, k = len(g), int((g["clasificacion"] == "KALINA").sum())
    return [fila("V21", "KF-M10-F3", "todas las filas", "filas; KALINA", "97; 97",
                 f"{n}; {k}", (n, k) == (97, 97))]


def v22(df):
    m = df[df["id_subcaso"].isin(["KF-M10-MALLA", "KF-M10b-MALLA"])]
    k = Kalina(m)
    tab = {round(float(x), 4): float(g["P_baja"].min()) for x, g in k.groupby("x_b")}
    m10 = {0.70: 500, 0.73: 600, 0.76: 600, 0.79: 700, 0.82: 700, 0.85: 800, 0.88: 800, 0.91: 800}
    m10b = {0.30: None, 0.35: None, 0.40: None, 0.45: None, 0.50: 200,
            0.55: 300, 0.60: 400, 0.65: 500, 0.70: 500}

    def coincide(exp):
        for x, e in exp.items():
            r = tab.get(round(x, 4))
            if (e is None and r is not None) or (e is not None and (r is None or not cerca(r, e, T_P))):
                return False, x
        return True, None

    okb, xb = coincide(m10b)
    okm, xm = coincide(m10)
    low = m[num(m["x_b"]) <= 0.475 + 1e-9]
    nlow = int((low["genuino"] & low["wnet_pos"]).sum())
    xs = sorted(tab)
    prim = xs[0] if xs else None
    ok_d = prim is not None and cerca(prim, 0.55, 1e-9) and cerca(tab[prim], 300, T_P)
    return [
        fila("V22", "KF-M10-MALLA + KF-M10b-MALLA", "KALINA (malla)",
             "P_baja mín KALINA por x_b vs REPORTE_M10b",
             "≤0.45 sin KALINA; 0.50→200; 0.55→300; 0.60→400; 0.65→500; 0.70→500",
             "coincide" if okb else f"difiere en x_b={xb}", okb),
        fila("V22", "KF-M10-MALLA + KF-M10b-MALLA", "KALINA (malla)",
             "P_baja mín KALINA por x_b vs REPORTE_M10",
             "0.70→500; 0.73→600; 0.76→600; 0.79→700; 0.82→700; 0.85→800; 0.88→800; 0.91→800",
             "coincide" if okm else f"difiere en x_b={xm}", okm),
        fila("V22", "KF-M10-MALLA + KF-M10b-MALLA", "x_b ≤ 0.475", "genuinos con W_net > 0",
             "0", f"{nlow}", nlow == 0),
        fila("V22", "KF-M10-MALLA + KF-M10b-MALLA", "KALINA (malla)",
             "primer x_b con KALINA y su P_baja mín", "0.55 con 300 kPa",
             f"{prim} con {tab.get(prim)} kPa", ok_d,
             nota="REPORTE_M10b §4 dice 0.50 con 200 kPa (KALINA formal, η≈0.1–1.2 %); "
                  "0.55 es el primero 'útil' según la nota del director, no el primero KALINA."),
    ]


def v23(df):
    return [fila("V23", c, "todas las filas", "N2", "(información)",
                 f"{int(g['es_N2'].sum())}", True, nota="solo información")
            for c, g in df.groupby("id_caso")]


CHECKS = [v13, v14, v15, v16, v17, v18, v19, v20, v21, v22, v23]
