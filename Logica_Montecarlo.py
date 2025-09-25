# =======================
#  LÓGICA
# =======================
import math
import random

def tabla_de_freq(freq: float, do, d1, d2, d3, d4) -> int:
    # Distribución de ausentismo (100 días): 0:36%, 1:38%, 2:19%, 3:6%, 4:1%, 5+:0%
    if 0 <= freq < (do/100):
        return 0
    elif freq < ((d1/100) + (do/100)):
        return 1
    elif freq < (d2/100 + (d1/100) + (do/100)):
        return 2
    elif freq < ((d3/100 + (d1/100) + (do/100))):
        return 3
    elif freq < ((d4/100) + (d3/100) + (d2/100) + (d1/100) + (do/100)):
        return 4
    else:
        return 5

def ejecutar_montecarlo(n: int, cant_obreros: int, valor_mayor_que: float, d0, d1, d2, d3, d4, ingreso, costo_fabricacion, costo_obrero):
    costo_mano_obra_x_obrero = costo_obrero
    costo_produccion_x_dia_base = costo_fabricacion
    ganancia_base = ingreso

    beneficio_acum = 0.0
    ocurrencias = 0
    rows = []

    for i in range(n):
        rnd = random.random()
        obreros_ausentes = tabla_de_freq(rnd, d0, d1, d2, d3, d4)
        obreros_presentes = cant_obreros - obreros_ausentes

        hay_produccion = (obreros_presentes >= 20)
        ganancia = ganancia_base if hay_produccion else 0.0
        costo_produccion_x_dia = costo_produccion_x_dia_base if hay_produccion else 0.0

        costo_mano_obra_total = cant_obreros * costo_mano_obra_x_obrero
        costo_total = costo_produccion_x_dia + costo_mano_obra_total
        beneficio = ganancia - costo_total
        beneficio_acum += beneficio

        # contador “normal” para probabilidad
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
            # contador ACUMULADO hasta esta fila
            "Contador ≥ umbral": ocurrencias,
        })

    probabilidad = math.trunc((ocurrencias / n) * 10000) / 10000
    return probabilidad, beneficio_acum, rows
