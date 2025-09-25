# =======================
#  APP
# =======================
from dash import Output, Input, State, callback, Dash, html
from dash.dash_table import DataTable
import dash_bootstrap_components as dbc

import Logica_Montecarlo as mc  

app = Dash(
    __name__,
    title="TP 2",
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP]
)

# ----- Encabezado -----
header = dbc.Container(
    [
        html.H1("Montecarlo — Ausencia de empleados",
                className="display-6 fw-bold text-center mt-4 mb-2"),
        html.P(
            "Ingresá el tamaño de la nómina y la cantidad de días para simular. "
            "Además, definí un beneficio umbral y, opcionalmente, qué tramo de iteraciones querés ver.",
            className="lead text-center text-muted mb-4"
        ),
    ],
    fluid=True
)

# ----- Tarjeta con formulario -----
form_card = dbc.Card(
    [
        dbc.CardHeader(
            [html.I(className="bi bi-sliders me-2"), html.Strong("Parámetros de Montecarlo")]
        ),
        dbc.CardBody(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label("Tamaño de nómina (empleados)"),
                                dbc.Input(id="input-nomina", type="number", step=1,
                                          value=21, placeholder="Ej: 24"),
                                dbc.FormText("Total de empleados permanentes.")
                            ],
                            md=6, className="mb-3"
                        ),
                        dbc.Col(
                            [
                                dbc.Label("Número de días (n)"),
                                dbc.Input(id="input-dias", type="number", step=5,
                                          value=None, placeholder="Ej: 5"),
                                dbc.FormText("Iteraciones de la simulación (soporta N ≥ 100000).")
                            ],
                            md=6, className="mb-3"
                        ),
                        dbc.Col(
                            [
                                dbc.Label("Dias (cantidades de 0 ausentes)"),
                                dbc.Input(id="input-dia-0", type="number", step=1,
                                          value=36, placeholder="Dias"),
                                dbc.FormText("Cantidad de dias que faltan 0 obreros.")
                            ],
                            md=6, className="mb-3"
                        ),
                        dbc.Col(
                            [
                                dbc.Label("Dias (cantidades de 1 ausentes)"),
                                dbc.Input(id="input-dia-1", type="number", step=1,
                                          value=38, placeholder="Dias"),
                                dbc.FormText("Cantidad de dias que faltan 1 obrero.")
                            ],
                            md=6, className="mb-3"
                        ),
                        dbc.Col(
                            [
                                dbc.Label("Dias (cantidades de 2 ausentes)"),
                                dbc.Input(id="input-dia-2", type="number", step=1,
                                          value=19, placeholder="Dias"),
                                dbc.FormText("Cantidad de dias que faltan 2 obreros.")
                            ],
                            md=6, className="mb-3"
                        ),  dbc.Col(
                            [
                                dbc.Label("Dias (cantidades de 3 ausentes)"),
                                dbc.Input(id="input-dia-3", type="number", step=1,
                                          value=6, placeholder="Dias"),
                                dbc.FormText("Cantidad de dias que faltan 3 obreros")
                            ],
                            md=6, className="mb-3"
                        ),
                        dbc.Col(
                            [
                                dbc.Label("Dias (cantidades de 4 ausentes)"),
                                dbc.Input(id="input-dia-4", type="number", step=1,
                                          value=1, placeholder="Dias"),
                                dbc.FormText("Cantidad de dias que faltan 4 obreros")
                            ],
                            md=6, className="mb-3"
                        ), dbc.Col(
                            [
                                dbc.Label("Dias (cantidades de 5 ausentes o más)"),
                                dbc.Input(id="input-dia-5", type="number", step=1,
                                          value=0, placeholder="Dias"),
                                dbc.FormText("Cantidad de dias que faltan 5 o más")
                            ],
                            md=6, className="mb-3"
                        ),
                        dbc.Col(
                            [
                                dbc.Label("Beneficio umbral"),
                                dbc.Input(id="input-prob", type="number", step=50,
                                          value=None, placeholder="Ej: 1000"),
                                dbc.FormText("Para P(Beneficio ≥ umbral).")
                            ],
                            md=6, className="mb-3"
                        ),
                        dbc.Col(
                            [
                                dbc.Label("Ingreso diario"),
                                dbc.Input(id="input-ingreso", type="number", step=50,
                                          value=4000, placeholder="Ej: 1000"),
                            ],
                            md=6, className="mb-3"
                        ),    dbc.Col(
                            [
                                dbc.Label("Costos por obrero"),
                                dbc.Input(id="input-obrero", type="number", step=1,
                                          value=30, placeholder="Ej: 10"),
                            ],
                            md=6, className="mb-3"
                        ), dbc.Col(
                            [
                                dbc.Label("Costos variables por fabricar"),
                                dbc.Input(id="input-costo-fabricar", type="number", step=1,
                                          value=2400, placeholder="Ej: 2400"),
                            ],
                            md=6, className="mb-3"
                        ),

                        # ---- NUEVOS PARÁMETROS DE VENTANA (i, j) ----
                        dbc.Col(
                            [
                                dbc.Label("i = cantidad de iteraciones a mostrar"),
                                dbc.Input(id="input-i", type="number", step=1,
                                          value=None),
                                dbc.FormText("Cuántas filas visualizar en la tabla.")
                            ],
                            md=6, className="mb-3"
                        ),
                        dbc.Col(
                            [
                                dbc.Label("j = a partir de qué iteración mostrar"),
                                dbc.Input(id="input-j", type="number", step=1,
                                          value=None, placeholder="Ej: 1"),
                                dbc.FormText("Primera iteración visible (1-indexado).")
                            ],
                            md=6, className="mb-3"
                        ),
                    ],
                    className="g-3"
                ),
                dbc.Button([html.I(className="bi bi-play-fill me-2"), "Continuar"],
                           id="btn-continuar", color="primary", className="mt-2",
                           disabled=True),
                html.Div(id="alerta", className="mt-3"),
            ]
        ),
    ],
    className="shadow-sm"
)

# ----- KPIs + Tabla -----
kpis = dbc.Card(
    dbc.CardBody(
        dbc.Row(
            [
                dbc.Col(dbc.Alert([html.Strong("Probabilidad (≥ umbral): "),
                                   html.Span(id="kpi-prob")], color="light"), md=4),
                dbc.Col(dbc.Alert([html.Strong("Beneficio acumulado: "),
                                   html.Span(id="kpi-benef")], color="light"), md=4),
                dbc.Col(dbc.Alert([html.Strong("Filas mostradas: "),
                                   html.Span(id="kpi-rows")], color="light"), md=4),
            ],
            className="g-2"
        )
    ),
    className="shadow-sm"
)

tabla_card = dbc.Card(
    [
        dbc.CardHeader([html.I(className="bi bi-table me-2"),
                        "Resultados Montecarlo"]),
        dbc.CardBody(
            DataTable(
                id="tabla",
                columns=[{"name": c, "id": c} for c in
                         ["Iteración", "rnd", "Ausentes", "Presentes", "Producción",
                          "Costo total", "Beneficio", "Beneficio acum.", "Contador ≥ umbral"]],
                data=[],
                page_action="none",
                virtualization=True,
                fixed_rows={"headers": True},
                style_table={"height": "60vh", "overflowY": "auto", "overflowX": "auto"},
                style_cell={"fontFamily": "Inter, system-ui", "fontSize": 13, "minWidth": "110px"},
            )
        ),
    ],
    className="shadow-sm"
)

# ----- Layout -----
app.layout = dbc.Container(
    [
        header,
        dbc.Row(dbc.Col(form_card, md=10, lg=8, xl=6, className="mx-auto"),
                className="justify-content-center mb-3"),
        dbc.Row(dbc.Col(kpis, md=10, lg=10, xl=10, className="mx-auto"),
                className="justify-content-center mb-3"),
        dbc.Row(dbc.Col(tabla_card, md=10, lg=10, xl=10, className="mx-auto"),
                className="justify-content-center mb-5"),
        html.Footer(html.Div([html.Span("Grupo nro 13")],
                             className="text-center text-muted small mb-4"))
    ],
    fluid=True
)

# =======================
#  CALLBACKS
# =======================

# 1) Validación
@callback(
    Output("btn-continuar", "disabled"),
    Output("alerta", "children"),
    Input("input-nomina", "value"),
    Input("input-dias", "value"),
    Input("input-prob", "value"),
    Input("input-i", "value"),
    Input("input-j", "value"),
    Input("input-dia-0", "value"),
    Input("input-dia-1", "value"),
    Input("input-dia-2", "value"),
    Input("input-dia-3", "value"),
    Input("input-dia-4", "value"),
    Input("input-dia-5", "value"),

)
def validar(nomina, dias, umbral, i, j, d1, d2, d3, d4, d5, d6):
    msg = None

    if None in (nomina, dias, umbral, i, j):
        return True, msg

    if sum([d1, d2, d3,d4,d5,d6]) != 100:
        return True, "La suma de los dias no es igual a 100"

    if not (21 <= int(nomina) <= 24):
        msg = dbc.Alert("La nómina debe estar entre 21 y 24.", color="warning", dismissable=True)
        return True, msg

    if int(dias) < 1 or int(dias) > 100000:
        msg = dbc.Alert("El número de días debe estar entre 1 y 100000.", color="warning", dismissable=True)
        return True, msg

    if int(i) < 1:
        msg = dbc.Alert("i debe ser ≥ 1.", color="warning", dismissable=True)
        return True, msg

    if int(j) < 1 or int(j) > int(dias):
        msg = dbc.Alert("j debe estar entre 1 y n.", color="warning", dismissable=True)
        return True, msg

    return False, msg

# 2) Ejecutar Montecarlo y mostrar ventana (j, i)
@callback(
    Output("tabla", "data"),
    Output("kpi-prob", "children"),
    Output("kpi-benef", "children"),
    Output("kpi-rows", "children"),
    Input("btn-continuar", "n_clicks"),
    State("input-nomina", "value"),
    State("input-dias", "value"),
    State("input-prob", "value"),
    State("input-i", "value"),
    State("input-j", "value"),
    Input("input-dia-0", "value"),
    Input("input-dia-1", "value"),
    Input("input-dia-2", "value"),
    Input("input-dia-3", "value"),
    Input("input-dia-4", "value"),
    Input("input-dia-5", "value"),
    Input("input-obrero", "value"),
    Input("input-ingreso", "value"),
    Input("input-costo-fabricar", "value"),
    prevent_initial_call=True
)
def ejecutar(_, nomina, dias, umbral, i, j, d0, d1, d2, d3, d4, d5, costo_obrero, ingreso, costo_fabricar):
    n = int(dias)
    cant_obreros = int(nomina)
    valor_mayor_que = float(umbral)
    i = int(i)
    j = int(j)

    prob, benef_acum, rows = mc.ejecutar_montecarlo(n, cant_obreros, valor_mayor_que, d0, d1, d2, d3, d4, ingreso,
                                                    costo_fabricar, costo_obrero)

    # ventana: mostrar solo desde j (1-index) i iteraciones
    start = max(0, j - 1)
    end = min(start + i, n)
    rows_window = rows[start:end] 
    
    # agregar siempre la última fila (N) si no está ya incluida
    if rows[-1] not in rows_window:
        rows_window.append(rows[-1])

    return rows_window, f"{prob:.4f}", f"{benef_acum:.2f}", f"{len(rows_window)}"

if __name__ == "__main__":
    app.run(debug=True)
