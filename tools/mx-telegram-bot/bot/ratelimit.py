"""Limitador de tasa en memoria (ventana deslizante) para peticiones con IA.

Se usa para evitar que `/ask` consuma todos los tokens de la API. Lleva un
conteo por usuario y, opcionalmente, un tope global. Pensado para un solo
proceso del bot (estado en memoria, se reinicia con el bot).
"""

from __future__ import annotations

import time
from collections import deque


class RateLimiter:
    """Ventana deslizante de N peticiones por `window_seconds` por clave.

    - `max_requests`: máximo por clave (usuario). 0 = sin límite por usuario.
    - `window_seconds`: tamaño de la ventana.
    - `global_max_requests`: máximo global. 0 = sin límite global.
    """

    def __init__(self, max_requests: int, window_seconds: float, global_max_requests: int = 0):
        self.max_requests = max(0, int(max_requests))
        self.window_seconds = max(1.0, float(window_seconds))
        self.global_max_requests = max(0, int(global_max_requests))
        self._hits: dict[object, deque[float]] = {}
        self._global: deque[float] = deque()

    def _prune(self, hits: deque, now: float) -> None:
        cutoff = now - self.window_seconds
        while hits and hits[0] <= cutoff:
            hits.popleft()

    def check(self, key) -> tuple[bool, float]:
        """Registra un intento. Devuelve (permitido, segundos_para_reintentar)."""
        if self.max_requests <= 0 and self.global_max_requests <= 0:
            return True, 0.0

        now = time.monotonic()

        if self.max_requests > 0:
            hits = self._hits.setdefault(key, deque())
            self._prune(hits, now)
            if len(hits) >= self.max_requests:
                return False, max(0.0, hits[0] + self.window_seconds - now)

        if self.global_max_requests > 0:
            self._prune(self._global, now)
            if len(self._global) >= self.global_max_requests:
                return False, max(0.0, self._global[0] + self.window_seconds - now)

        if self.max_requests > 0:
            self._hits.setdefault(key, deque()).append(now)
        if self.global_max_requests > 0:
            self._global.append(now)
        return True, 0.0

    def reset(self, key=None) -> None:
        """Reinicia el estado (para pruebas o administración)."""
        if key is None:
            self._hits.clear()
            self._global.clear()
        else:
            self._hits.pop(key, None)
