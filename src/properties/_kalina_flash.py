# Copia LITERAL de un extracto de:
#   D:\Archivo mental\Archivo mental\04_PROJECTS\active\Ciclo Kalina\codigo\src\kalina.py
#   (lineas 10-203 del original: CAPA DE PROPIEDADES; la CAPA DE RESOLUCION
#   del ciclo, especifica del vault, no se incluye — es material de una tarea
#   futura). El unico cambio respecto al original es el import de ng (abajo);
#   todo lo demas se preserva sin modificar.

import bisect
import numpy as np
from scipy.optimize import brentq, fsolve
from . import _nh3h2o_engine as ng

TOL_T = 1e-6          # tolerancia de inversion en temperatura [K]
DQ = 1e-3             # margen del criterio O5

# ---------------------------------------------------------------------------
# CAPA DE PROPIEDADES
# ---------------------------------------------------------------------------
_puros = {}
_flash = {}           # P -> lista ordenada de (T, xL, xV), usada como arranque tibio


def Tsat_puros(P):
    """(T_sat NH3, T_sat H2O) puros a P. Cotas rigurosas de la campana binaria."""
    k = round(P, 10)
    if k not in _puros:
        _puros[k] = ng.Tsat_pure(P)
    return _puros[k]


def flash_TP(T, P):
    """Equilibrio a (T,P): devuelve (x_L, x_V) MOLARES, o None si a esa (T,P) no
    existe region bifasica para ninguna composicion.

    Resuelve la igualdad de fugacidades de los dos componentes. Es el mismo
    equilibrio que bubbleP/dewP de nh3h2o, pero parametrizado por (T,P), que es
    como lo necesita el ciclo. Arranque tibio con el flash previo mas cercano en
    T a la misma presion: reduce las iteraciones de fsolve de ~9 a ~3.
    """
    Ta, Tw = Tsat_puros(P)
    # Banda de guarda de 0.3 K junto a los puros: alli la ventana bifasica en
    # composicion se cierra (x_L -> 1 o x_V -> 0) y el sistema de fugacidades se
    # vuelve singular. Fuera de la banda el estado es monofasico para cualquier
    # composicion salvo un entorno de medida despreciable, y se resuelve como tal.
    if T <= Ta + 0.3 or T >= Tw - 0.3:
        return None
    kP = round(P, 10)
    tabla = _flash.setdefault(kP, [])
    Ts = [r[0] for r in tabla]
    i = bisect.bisect_left(Ts, T)
    if i < len(Ts) and abs(Ts[i] - T) < 1e-9:
        return tabla[i][1], tabla[i][2]
    pa, pw = ng.Psat_pure(T)
    raoult = (float(np.clip((P - pw) / (pa - pw), 1e-4, 1 - 1e-4)),)
    raoult = (raoult[0], float(np.clip(raoult[0] * pa / P, 1e-4, 1 - 1e-4)))
    cand = [tabla[j] for j in (i - 1, i) if 0 <= j < len(tabla)]
    arranques = []
    if cand:
        _, xL0, xV0 = min(cand, key=lambda r: abs(r[0] - T))
        arranques.append((xL0, xV0))          # arranque tibio
    arranques.append(raoult)                  # respaldo: inicializacion de Raoult

    def F(v):
        a = min(max(v[0], 1e-9), 1 - 1e-9)
        b = min(max(v[1], 1e-9), 1 - 1e-9)
        L = ng.prop(ng.rho_TPx(T, P, a, 'l'), T, a)
        V = ng.prop(ng.rho_TPx(T, P, b, 'v'), T, b)
        return [np.log(a * L['phiA']) - np.log(b * V['phiA']),
                np.log((1 - a) * L['phiW']) - np.log((1 - b) * V['phiW'])]

    sol = None
    for v0 in arranques:
        try:
            s, _, ier, _ = fsolve(F, list(v0), full_output=True, xtol=1e-12)
        except ValueError:
            continue
        if ier == 1 and 0 < s[0] < s[1] < 1:
            sol = s
            break
    if sol is None:
        return None
    xL, xV = float(sol[0]), float(sol[1])
    bisect.insort(tabla, (T, xL, xV))
    return xL, xV


def _mono(T, P, x, fase):
    r = ng.prop(ng.rho_TPx(T, P, x, fase), T, x)
    return r['h'], r['s']


def estado(T, P, w):
    """Estado completo a (T,P) con composicion global MASICA w."""
    x = ng.w2m(w)
    d = dict(T=T, P=P, w=w)
    eq = flash_TP(T, P)
    if eq is None:
        Ta, Tw = Tsat_puros(P)
        if Ta + 0.3 < T < Tw - 0.3:
            # El flash a (T,P) no converge: ocurre solo en la vecindad de los
            # componentes puros, donde la ventana bifasica en composicion se
            # cierra. Se decide la fase con las funciones propias del motor,
            # que si son estables ahi porque estan parametrizadas por x.
            Pb = ng.bubbleP(T, x)[0]
            Pd = ng.dewP(T, x)[0]
            if P >= Pb:
                fase = 'liquido'
            elif P <= Pd:
                fase = 'vapor'
            else:
                raise RuntimeError(f"equilibrio no resoluble en T={T:.4f} K, "
                                   f"P={P:.5g} MPa, w={w:.4f}")
        else:
            fase = 'liquido' if T <= Ta else 'vapor'
            if Ta < T <= Ta + 0.3:
                # Sobre Ta la regla de componente puro llama vapor a mezclas liquidas.
                try:
                    if P >= ng.bubbleP(T, x)[0]:
                        fase = 'liquido'
                except Exception:
                    pass
        h, s = _mono(T, P, x, 'l' if fase == 'liquido' else 'v')
        d.update(h=h, s=s, q=0.0 if fase == 'liquido' else 1.0, fase=fase)
        return d
    xL, xV = eq
    if x <= xL:
        h, s = _mono(T, P, x, 'l')
        d.update(h=h, s=s, q=0.0, fase='liquido')
    elif x >= xV:
        h, s = _mono(T, P, x, 'v')
        d.update(h=h, s=s, q=1.0, fase='vapor')
    else:
        wL, wV = ng.m2w(xL), ng.m2w(xV)
        q = (w - wL) / (wV - wL)                 # titulo MASICO (regla de la palanca)
        hL, sL = _mono(T, P, xL, 'l')
        hV, sV = _mono(T, P, xV, 'v')
        d.update(h=q * hV + (1 - q) * hL, s=q * sV + (1 - q) * sL, q=q,
                 fase='bifasico', wL=wL, wV=wV, hL=hL, hV=hV, sL=sL, sV=sV)
    return d


_env = {}


def T_sat(P, w, kind):
    """T de liquido saturado ('L') o de vapor saturado ('V') a (P, w masica).
    Solo se usa para informar y para el criterio F1; se cachea."""
    k = (round(P, 10), round(w, 8), kind)
    if k not in _env:
        x = ng.w2m(w)
        _env[k] = (ng.bubbleT(P, x)[0] if kind == 'L' else ng.dewT(P, x)[0])
    return _env[k]


_ultimaT = {}     # (P, w, propiedad) -> ultima T resuelta, para acotar el brentq


def estado_de(P, w, h=None, s=None):
    """Inversion: estado a (P, w) con h o s prescrita. h y s crecen con T.

    El intervalo de arranque se toma alrededor de la ultima T resuelta para esa
    misma (P, w, propiedad) y se ensancha hasta encontrar cambio de signo. En un
    lazo iterativo las llamadas sucesivas caen casi encima, de modo que brentq
    trabaja sobre un intervalo de pocos K en lugar de sobre toda la campana.
    """
    nombre = 'h' if h is not None else 's'
    val = h if h is not None else s
    k = (round(P, 10), round(w, 8), nombre)
    Ta, Tw = Tsat_puros(P)
    T0 = _ultimaT.get(k)
    f = lambda T: estado(T, P, w)[nombre] - val
    if T0 is not None:
        lo, hi = T0 - 8.0, T0 + 8.0
    else:
        lo, hi = max(235.0, Ta - 60.0), Tw + 40.0
    flo, fhi = f(lo), f(hi)
    paso, n = 16.0, 0
    while flo > 0 and n < 30:
        hi, fhi = lo, flo
        lo = max(233.0, lo - paso)
        flo = f(lo)
        paso *= 1.6
        n += 1
        if lo <= 233.0 and flo > 0:
            break
    paso = 16.0
    while fhi < 0 and n < 60:
        lo, flo = hi, fhi
        hi += paso
        fhi = f(hi)
        paso *= 1.6
        n += 1
        if hi > 900.0:
            break
    if flo > 0 or fhi < 0:
        raise RuntimeError(f"{nombre}={val:.6g} fuera de dominio a "
                           f"P={P:.5g} MPa, w={w:.4f}")
    T = brentq(f, lo, hi, xtol=TOL_T)
    _ultimaT[k] = T
    return estado(T, P, w)
