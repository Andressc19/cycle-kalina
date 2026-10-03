"""Bracket tolerante del lazo exterior de T1 ("siempre tolerante", MA).

Complemento de `src/cycle_solver.py` (tarea `2026-10-02-implementar-ma`): con
``bracket_tolerante=True`` el resolutor nunca se rinde ante un estado que el
motor de propiedades no puede evaluar.

- **Extremos**: si F(lo) o F(hi) no son evaluables, el extremo se repliega
  hacia dentro ``paso_repliegue`` K por intento mientras ``lo + paso < hi``
  (resp. ``hi − paso > lo``); ``max_repliegues=None`` = sin tope.
- **Punto interior**: un estado no evaluable durante ``brentq`` NO tiene
  recuperación (el buscador necesita un valor) y aborta con la T en el mensaje.
- **Presupuesto**: con ``presupuesto_s`` el reloj de pared se comprueba ENTRE
  evaluaciones de F, nunca a mitad de una.
- Solo se tolera ``PropertyRangeError``; cualquier otra excepción sube intacta.

Patrón adapter: recibe ``evaluar`` y el backend por inyección y solo importa
``PropertyRangeError`` (de `src.properties.adapter`) y ``CicloNoConvergeError``
(de `src._cycle_loops`): nunca importa un backend concreto. El estado (T10
tibio, nº de evaluaciones, reloj) vive en la instancia, así que dos llamadas
sucesivas de `resolver_ciclo` no comparten nada.
"""

from __future__ import annotations

import time

from ._cycle_loops import CicloNoConvergeError
from .properties.adapter import PropertyRangeError

__all__ = ["BracketTolerante"]

APARTE_T10 = 5.0    # K: arranque tibio del lazo interior en la 1a evaluación de F


class BracketTolerante:
    """Lazo exterior de T1 con bracket replegado, arranque tibio y presupuesto.

    ``evaluar(T1, backend, **kwargs, T10_inicial=...)`` se recibe por inyección
    (el global ``evaluar`` de ``src.cycle_solver``, que así sigue siendo
    espiable por los tests) junto con los ``kwargs`` de ``evaluar``.
    ``nF`` cuenta evaluaciones de F: la evaluación final con T1 ya resuelto
    (la hace `cerrar`) no cuenta.
    """

    def __init__(self, evaluar, backend, kwargs, *, T_sumidero, T_fuente,
                 paso_repliegue=5.0, max_repliegues=None, presupuesto_s=None):
        self._evaluar, self._backend, self._kwargs = evaluar, backend, kwargs
        self.T_sumidero, self.T_fuente = T_sumidero, T_fuente
        self.paso, self.max_repliegues = paso_repliegue, max_repliegues
        self.presupuesto_s = presupuesto_s
        self.ultimo_T10 = None       # arranque tibio entre evaluaciones de F
        self.repliegues_lo = 0
        self.repliegues_hi = 0
        self.nF = 0
        self.t0 = time.perf_counter()

    # -------------------------------------------------------------- reloj --
    def _reloj(self):
        """Rinde si se pasó ``presupuesto_s``; se llama entre evaluaciones de F."""
        if self.presupuesto_s is None:
            return
        if time.perf_counter() - self.t0 > self.presupuesto_s:
            raise CicloNoConvergeError(
                f"presupuesto de tiempo agotado: {self.nF} evaluaciones de F "
                f"en {time.perf_counter() - self.t0:.1f} s "
                f"(presupuesto {self.presupuesto_s:g} s)")

    # -------------------------------------------------------- evaluaciones --
    def F(self, T1):
        """F(T1) = T1_nuevo − T1. La 1ª evaluación arranca el lazo interior en
        ``T_sumidero + APARTE_T10`` K (arranque tibio); después, con el T10
        convergido de la evaluación anterior."""
        self._reloj()
        T10_ini = (self.T_sumidero + APARTE_T10 if self.ultimo_T10 is None
                   else self.ultimo_T10)
        T1_nuevo, estados, _ = self._evaluar(T1, self._backend, **self._kwargs,
                                             T10_inicial=T10_ini)
        self.ultimo_T10 = estados["e10"].T
        self.nF += 1
        return T1_nuevo - T1

    def F_seguro(self, T1):
        """F tolerando solo ``PropertyRangeError``: extremo no evaluable -> None."""
        try:
            return self.F(T1)
        except PropertyRangeError:
            return None

    def F_brentq(self, T1):
        """F para ``brentq``: un punto INTERIOR no evaluable no se puede replegar."""
        v = self.F_seguro(T1)
        if v is None:
            raise CicloNoConvergeError(
                "punto interior no evaluable durante brentq "
                f"(T={T1:.6f} K)")
        return v

    # ------------------------------------------------------------- bracket --
    def bracketear(self):
        """``(lo, hi)`` evaluables con cambio de signo de F, replegando cada
        extremo que el motor no pueda evaluar. Lanza ``CicloNoConvergeError`` si
        no quedan dos extremos evaluables o si no hay cambio de signo."""
        lo, hi = self.T_sumidero + 1.0, self.T_fuente - 1.0
        if not lo < hi:
            raise CicloNoConvergeError(
                "rango físico de T1 degenerado: T_fuente <= T_sumidero + 2 K; "
                "no hay bracket posible")
        r_lo, r_hi = 0, 0
        f_lo = self.F_seguro(lo)
        while f_lo is None and lo + self.paso < hi and self._queda(r_lo):
            r_lo += 1
            lo, f_lo = lo + self.paso, self.F_seguro(lo + self.paso)
        f_hi = self.F_seguro(hi)
        while f_hi is None and hi - self.paso > lo and self._queda(r_hi):
            r_hi += 1
            hi, f_hi = hi - self.paso, self.F_seguro(hi - self.paso)
        self.repliegues_lo, self.repliegues_hi = r_lo, r_hi
        if f_lo is None or f_hi is None:
            raise CicloNoConvergeError(
                "sin dos extremos evaluables en el rango físico de T1 "
                f"(repliegues_lo={r_lo}, repliegues_hi={r_hi}, "
                f"paso={self.paso} K)")
        if f_lo * f_hi > 0.0:
            raise CicloNoConvergeError(
                f"extremos [{lo:.4f}, {hi:.4f}] K sin cambio de signo de F "
                f"(F(lo)={f_lo:.5g}, F(hi)={f_hi:.5g})")
        return lo, hi

    def _queda(self, n_repliegues):
        """``max_repliegues=None`` = sin tope; si es entero, tope por extremo
        (el primer intento no cuenta: tope 2 ⇒ hasta 3 evaluaciones)."""
        return self.max_repliegues is None or n_repliegues < self.max_repliegues

    # ------------------------------------------------------------- cierre --
    def cerrar(self, T1_sol):
        """Evaluación final (T1 ya resuelto; no cuenta como F) + energías."""
        _, estados, energias = self._evaluar(T1_sol, self._backend, **self._kwargs,
                                             T10_inicial=self.ultimo_T10)
        Wnet = energias["Wt"] - energias["Wp"]
        return dict(estados=estados, **energias, Wnet=Wnet,
                    eta=Wnet / energias["Qi"])

    def info_bracket(self, lo, hi):
        """Valor de la clave extra ``bracket`` del dict de salida."""
        return dict(lo=lo, hi=hi, repliegues_lo=self.repliegues_lo,
                    repliegues_hi=self.repliegues_hi, nF=self.nF)