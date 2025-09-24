# =======================
#  LÓGICA
# =======================
import math
import random


def tabla_de_freq(freq: float) -> int:
    # Rango [0,1) particionado como definiste
    if 0.0 <= freq < 0.36:
        return 0
    elif freq < 0.74:
        return 1
    elif freq < 0.93:
        return 2
    elif freq < 0.99:
        return 3
    else:
        return 4


def ejecutar_montecarlo(n: int, cant_obreros: int, valor_mayor_que: float):
    """
    Versión batch (opcional). Corre todo de una vez con un for.
    La dejamos por si querés ejecutar sin Interval.
    """
    costo_mano_obra_x_obrero = 30.0
    costo_produccion_x_dia_base = 2400.0
    ganancia_base = 4000.0

    beneficio_acum = 0.0
    ocurrencias = 0
    rows = []

    for i in range(n):
        rnd = random.random()
        obreros_ausentes = tabla_de_freq(rnd)
        obreros_presentes = cant_obreros - obreros_ausentes

        hay_produccion = (obreros_presentes >= 20)
        ganancia = ganancia_base if hay_produccion else 0.0
        costo_produccion_x_dia = costo_produccion_x_dia_base if hay_produccion else 0.0

        cost_mano_obra_total = cant_obreros * costo_mano_obra_x_obrero
        costo_total = costo_produccion_x_dia + cost_mano_obra_total
        beneficio = ganancia - costo_total
        beneficio_acum += beneficio

        if beneficio >= valor_mayor_que:
            ocurrencias += 1

        rows.append({
            "Iteración": i + 1,
            "rnd": round(rnd, 5),
            "Ausentes": obreros_ausentes,
            "Presentes": obreros_presentes,
            "Producción": "Sí" if hay_produccion else "No",
            "Costo total": round(costo_total, 2),
            "Beneficio": round(beneficio, 2),
            "Beneficio acum.": round(beneficio_acum, 2),
            "≥ umbral": "✔" if beneficio >= valor_mayor_que else "✖",
        })

    probabilidad = math.trunc((ocurrencias / n) * 10000) / 10000
    return probabilidad, beneficio_acum, rows  # ← corregido (sin el punto extra)


def montecarlo_step(state: dict):
    """
    Avanza UNA iteración y devuelve:
      - new_state (con i, beneficio_acum y ocurrencias actualizados)
      - row (dict con la nueva fila)
      - prob (probabilidad estimada hasta ahora)
    """
    # Parámetros del estado
    n = int(state["n"])
    cant_obreros = int(state["cant_obreros"])
    umbral = float(state["umbral"])

    # Acumuladores
    i = int(state["i"])  # cuántas iteraciones ya corridas
    beneficio_acum = float(state["beneficio_acum"])
    ocurrencias = int(state["ocurrencias"])

    # Constantes del modelo
    costo_mano_obra_x_obrero = 30.0
    costo_produccion_x_dia_base = 2400.0
    ganancia_base = 4000.0

    # Siguiente iteración (1-based en la tabla)
    iter_idx = i + 1
    rnd = random.random()
    obreros_ausentes = tabla_de_freq(rnd)
    obreros_presentes = cant_obreros - obreros_ausentes

    hay_produccion = (obreros_presentes >= 20)
    ganancia = ganancia_base if hay_produccion else 0.0
    costo_produccion_x_dia = costo_produccion_x_dia_base if hay_produccion else 0.0

    cost_mano_obra_total = cant_obreros * costo_mano_obra_x_obrero
    costo_total = costo_produccion_x_dia + cost_mano_obra_total
    beneficio = ganancia - costo_total
    beneficio_acum += beneficio

    if beneficio >= umbral:
        ocurrencias += 1

    row = {
    "Iteración": iter_idx,
    "rnd": round(rnd, 5),
    "Ausentes": obreros_ausentes,
    "Presentes": obreros_presentes,
    "Producción": "Sí" if hay_produccion else "No",
    "Costo total": round(costo_total, 2),
    "Beneficio": round(beneficio, 2),
    "Beneficio acum.": round(beneficio_acum, 2),
    "≥ umbral": str(ocurrencias),  # <- nombre consistente
}

    # Actualizar estado
    i = iter_idx
    prob = (ocurrencias / i) if i > 0 else 0.0

    new_state = {
        "n": n,
        "cant_obreros": cant_obreros,
        "umbral": umbral,
        "i": i,
        "beneficio_acum": beneficio_acum,
        "ocurrencias": ocurrencias
    }
    return new_state, row, prob

