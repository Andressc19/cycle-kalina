"""M4b — tablas y prosa de las presiones para `REPORTE_M4b.md`.

Los formatos son fijos a propósito: `m4b_verificar.py` recalcula cada cifra
desde los CSV con estos mismos decimales y exige que el reporte coincida. Los
números usan `nf`/`gf`/`pf` de `m4_tablas.py` (decimal fijo, 6 cifras
generales y valor p con 4 cifras).
"""
from __future__ import annotations

from m4_tablas import gf, nf, pf

CAB_B = ("| variable | grupo | n | mín | p5 | mediana | p95 | máximo | KS | "
         "valor p |")
CAB_F = ("| franja | lo | hi | n | n KALINA | % KALINA | P_baja (mín–máx) | "
         "dP (mín–máx) | rP (mín–máx) |")
CAB_G = "| zona | codigos_falla | n |"
CAB_C = ("| variable | KS (500) | rango favorable (500) | KS (300) | "
         "rango favorable (300) |")


def _sep(n: int) -> str:
    return "|" + "---|" * n


def tabla_b(rangos: list) -> str:
    """Tabla (b): los cuatro estadísticos de los dos grupos, más el KS."""
    out = [CAB_B, _sep(10)]
    for r in rangos:
        out.append(f'| {r["variable"]} | {r["grupo"]} | {r["n"]} | '
                   f'{gf(r["min"])} | {gf(r["p05"])} | {gf(r["mediana"])} | '
                   f'{gf(r["p95"])} | {gf(r["max"])} | {nf(r["KS"])} | '
                   f'{pf(r["p_valor"])} |')
    return "\n".join(out)


def tabla_fr(rows: list) -> str:
    """Tabla (c)/(d)/(e): una fila por franja con los rangos de KALINA."""
    out = [CAB_F, _sep(9)]
    for r in rows:
        out.append(f'| {r["franja"]} | {gf(r["lo"])} | {gf(r["hi"])} | '
                   f'{r["n"]} | {r["n_kalina"]} | {nf(r["pct_kalina"], 1)} | '
                   f'{gf(r["P_baja_min"])} – {gf(r["P_baja_max"])} | '
                   f'{gf(r["dP_min"])} – {gf(r["dP_max"])} | '
                   f'{gf(r["rP_min"])} – {gf(r["rP_max"])} |')
    return "\n".join(out)


def tabla_g(rows: list) -> str:
    """Tabla (g): `codigos_falla` de los genuinos no KALINA por zona de rP."""
    out = [CAB_G, _sep(3)]
    out += [f'| {r["zona"]} | {r["codigos_falla"]} | {r["n"]} |' for r in rows]
    if not rows:
        out.append("| (sin filas) | — | 0 |")
    return "\n".join(out)


def tabla_cmp(rsa500: list, rsa300: dict) -> str:
    """RSA con 500 (KS y rango favorable) junto al mismo con los 300."""
    o = sorted([r for r in rsa500 if r["KS"] is not None],
               key=lambda r: -r["KS"])
    o += [r for r in rsa500 if r["KS"] is None]
    out = [CAB_C, _sep(5)]
    for r in o:
        a = rsa300.get(r["variable"], {})
        out.append(f'| {r["variable"]} | {nf(r["KS"])} | '
                   f'[{gf(r["fav_p05"])}, {gf(r["fav_p95"])}] | '
                   f'{nf(a.get("KS"))} | '
                   f'[{gf(a.get("fav_p05"))}, {gf(a.get("fav_p95"))}] |')
    return "\n".join(out)


def prosa_franjas(rows: list, nombre: str) -> list:
    """Una frase por franja: cuántos puntos, cuántos KALINA y sus rangos."""
    frases = []
    for r in rows:
        base = (f'{nombre} entre {gf(r["lo"])} y {gf(r["hi"])}: {r["n"]} '
                f'puntos, {r["n_kalina"]} KALINA')
        if not r["n_kalina"]:
            frases.append(base + ", así que ahí no hay KALINA")
            continue
        frases.append(
            base + f' ({nf(r["pct_kalina"], 1)} %), con P_baja de '
            f'{gf(r["P_baja_min"])} a {gf(r["P_baja_max"])} kPa, dP de '
            f'{gf(r["dP_min"])} a {gf(r["dP_max"])} kPa y rP de '
            f'{gf(r["rP_min"])} a {gf(r["rP_max"])}')
    return frases


def suma_zonas(rows: list) -> dict:
    """`(zona → total de puntos)` de la tabla (g), para la prosa."""
    tot = {}
    for r in rows:
        tot[r["zona"]] = tot.get(r["zona"], 0) + r["n"]
    return tot
