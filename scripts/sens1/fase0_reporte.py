"""Sensibilidad 1, Fase 0 — resumen de la corrida (`fase0_filas.csv`).

Escribe `resultados/2026-10-14_sens1_fase0/fase0_resumen.md` con: (1) la tabla
de los 11 puntos, (2) el control de no-regresión `H0` vs `H0_noextra`, (3) el
escalado con `m_b` (H0, M5, M10, M15, M20) y (4) el conteo de puntos genuinos.
Cada número sale del CSV; no se inventa nada.
Se ejecuta como script, no como módulo.
"""
from __future__ import annotations

import csv
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
OUT = _RAIZ / "resultados" / "2026-10-14_sens1_fase0"
FILAS = OUT / "fase0_filas.csv"
RESUMEN = OUT / "fase0_resumen.md"
ORDEN = ["H0", "H0_noextra", "M5", "M10", "M15", "M20", "E95", "E85", "E80",
         "P600", "P800"]
ESCALADO = ["H0", "M5", "M10", "M15", "M20"]
COL_TABLA = ["id_punto", "clasificacion", "convergio", "eta [%]", "Wnet",
             "m_O2", "Qi", "Qreg", "dh_turb", "t_s"]


def _num(v):
    if v in (None, "", "None"):
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _fmt(v, n=6):
    x = _num(v)
    return "—" if x is None else f"{x:.{n}g}"


def _leer() -> dict:
    with open(FILAS, encoding="utf-8", newline="") as fh:
        return {f["id_punto"]: f for f in csv.DictReader(fh)}


def _tabla(filas: dict) -> list:
    out = ["| " + " | ".join(COL_TABLA) + " |",
           "|" + "|".join("---" for _ in COL_TABLA) + "|"]
    for pid in ORDEN:
        f = filas.get(pid)
        if f is None:
            continue
        eta = _num(f.get("eta"))
        out.append("| " + " | ".join([
            pid, f.get("clasificacion") or "—", f.get("convergio") or "—",
            "—" if eta is None else f"{100 * eta:.4f}",
            _fmt(f.get("Wnet")), _fmt(f.get("m_O2")), _fmt(f.get("Qi")),
            _fmt(f.get("Qreg")), _fmt(f.get("dh_turb")), _fmt(f.get("t_s"), 4),
        ]) + " |")
    return out


def _no_regresion(filas: dict) -> list:
    a, b = filas.get("H0"), filas.get("H0_noextra")
    if a is None or b is None:
        return ["No se pudo comparar: falta H0 o H0_noextra en el CSV."]
    ea, eb = _num(a.get("eta")), _num(b.get("eta"))
    wa, wb = _num(a.get("Wnet")), _num(b.get("Wnet"))
    ca, cb = a.get("clasificacion"), b.get("clasificacion")
    d_eta = None if ea is None or eb is None else abs(ea - eb)
    d_w = None if wa is None or wb is None else abs(wa - wb)
    ok_eta = d_eta is not None and d_eta < 1e-9
    ok = ok_eta and wa == wb and ca == cb
    return [
        f"- η: H0 = {_fmt(a.get('eta'), 12)} · H0_noextra = "
        f"{_fmt(b.get('eta'), 12)} · |Δη| = "
        f"{'—' if d_eta is None else f'{d_eta:.3e}'} → "
        f"{'OK (< 1e-9)' if ok_eta else 'NO'}",
        f"- Wnet: H0 = {_fmt(wa, 12)} · H0_noextra = {_fmt(wb, 12)} · "
        f"|ΔWnet| = {'—' if d_w is None else f'{d_w:.3e}'} → "
        f"{'iguales' if wa == wb else 'DISTINTOS'}",
        f"- clasificacion: H0 = {ca} · H0_noextra = {cb} → "
        f"{'iguales' if ca == cb else 'DISTINTAS'}",
        "",
        f"**Control de no-regresión: {'PASA' if ok else 'FALLA'}** "
        f"(H0 con extra=True y H0_noextra con extra=False deben coincidir en η, "
        f"Wnet y clase).",
    ]


def _escalado(filas: dict) -> list:
    h0 = filas.get("H0")
    if h0 is None or _num(h0.get("m_b")) in (None, 0):
        return ["No se pudo comprobar el escalado: falta H0 o su m_b."]
    mb0, eta0 = _num(h0["m_b"]), _num(h0["eta"])
    ref = {k: _num(h0.get(k)) / mb0 for k in ("Wnet", "Qi", "Qreg")}
    out = ["| id_punto | m_b | eta | \\|Δη\\| vs H0 | misma clase | "
           "Wnet/m_b ÷ H0 | Qi/m_b ÷ H0 | Qreg/m_b ÷ H0 |",
           "|---|---|---|---|---|---|---|---|"]
    max_deta, max_dev = 0.0, {k: 0.0 for k in ref}
    mismas_clases = True
    for pid in ESCALADO:
        f = filas.get(pid)
        if f is None:
            continue
        mb, eta = _num(f.get("m_b")), _num(f.get("eta"))
        deta = None if None in (eta, eta0) else abs(eta - eta0)
        same = f.get("clasificacion") == h0.get("clasificacion")
        mismas_clases &= same
        ratios = {}
        for k in ref:
            v = _num(f.get(k))
            ratios[k] = (None if None in (v, mb, ref[k]) or ref[k] == 0 or mb == 0
                         else (v / mb) / ref[k])
            if ratios[k] is not None:
                max_dev[k] = max(max_dev[k], abs(ratios[k] - 1.0))
        if deta is not None:
            max_deta = max(max_deta, deta)
        out.append("| " + " | ".join([
            pid, _fmt(mb, 6), _fmt(eta, 10),
            "—" if deta is None else f"{deta:.3e}",
            "sí" if same else "NO",
            _fmt(ratios["Wnet"], 10), _fmt(ratios["Qi"], 10),
            _fmt(ratios["Qreg"], 10),
        ]) + " |")
    tol_r, tol_eta = 1e-4, 1e-6
    escala = (mismas_clases and max_deta <= tol_eta
              and all(d <= tol_r for d in max_dev.values()))
    out += ["",
            f"Desviación máxima de η respecto a H0: **{max_deta:.3e}** "
            f"(tol {tol_eta:g}).",
            f"Desviación máxima de las razones (|razón − 1|): "
            f"Wnet/m_b = **{max_dev['Wnet']:.3e}**, "
            f"Qi/m_b = **{max_dev['Qi']:.3e}**, "
            f"Qreg/m_b = **{max_dev['Qreg']:.3e}** (tol {tol_r:g}).",
            f"¿Misma clasificación en los cinco?: "
            f"**{'sí' if mismas_clases else 'no'}**."]
    if escala:
        out.append("\n**ESCALA**: η y la clase se mantienen y las potencias "
                   "escalan con m_b dentro de tolerancia.")
    else:
        fallos = [k for k, d in max_dev.items() if d > tol_r]
        if not mismas_clases:
            fallos.append("clasificación")
        if max_deta > tol_eta:
            fallos.append("η")
        out.append(f"\n**NO ESCALA**: falla en {', '.join(fallos)}.")
    return out


def _genuinos(filas: dict) -> list:
    g = [pid for pid in ORDEN if pid in filas
         and filas[pid].get("convergio") == "True"
         and filas[pid].get("clasificacion") != "NO_CONVERGIO"]
    return [f"Puntos genuinos (convergio=True y clasificacion != "
            f"NO_CONVERGIO): **{len(g)} de {len(ORDEN)}** ({', '.join(g)}).",
            "Los N2 espurios no cuentan como genuinos."]


def main() -> None:
    filas = _leer()
    doc = ["# Sensibilidad 1 — Fase 0: H*, no-regresión y escalado con m_b", "",
           "**Fecha:** 2026-10-14 · **Motor:** teqp · **t_amb_diseno:** 283.15 K "
           "· **H\\*** = Húsavík (T_fuente 394.15, T_sumidero 278.15, P_alta "
           "3300, P_baja 690, x_b 0.82, m_b 1.0, eta_t 0.85, eta_p 0.80, "
           "eps_hrvg 0.85, eps_reg 0.75, eps_cond 0.90).", "",
           "## 1. Los 11 puntos", "", *_tabla(filas), "",
           "## 2. Control de no-regresión (H0 vs H0_noextra)", "",
           *_no_regresion(filas), "",
           "## 3. Escalado con m_b (H0, M5, M10, M15, M20)", "",
           *_escalado(filas), "",
           "## 4. Puntos genuinos", "", *_genuinos(filas)]
    RESUMEN.write_text("\n".join(doc) + "\n", encoding="utf-8")
    print(f"escrito: {RESUMEN} ({len(doc)} líneas)", flush=True)


if __name__ == "__main__":
    main()
