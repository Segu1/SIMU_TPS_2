# =======================
#  APP
# =======================
from dash import Output, Input, State, callback, Dash, html
from dash.dash_table import DataTable
import dash_bootstrap_components as dbc

import Logica_Montercalo

app = Dash(
    __name__,
    title="TP 2",
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP]
)

# ----- Encabezado -----
header = dbc.Container(
    [
        html.H1(
            "Montecarlo — Ausencia de empleados",
            className="display-6 fw-bold text-center mt-4 mb-2"
        ),
        html.P(
            "Ingresá el tamaño de la nómina y la cantidad de días para simular. "
            "Además, definí un beneficio umbral para calcular la probabilidad.",
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
                                dbc.Input(
                                    id="input-nomina",
                                    type="number",
                                    step=1,
                                    value=None,
                                    placeholder="Ej: 24",
                                ),
                                dbc.FormText("Cantidad total de empleados a evaluar."),
                            ],
                            md=6,
                            className="mb-3"
                        ),
                        dbc.Col(
                            [
                                dbc.Label("Número de días (n)"),
                                dbc.Input(
                                    id="input-dias",
                                    type="number",
                                    step=10,
                                    value=None,
                                    placeholder="Ej: 560",
                                ),
                                dbc.FormText("Cantidad de iteraciones a evaluar."),
                            ],
                            md=6,
                            className="mb-3"
                        ),
                        dbc.Col(
                            [
                                dbc.Label("Beneficio umbral"),
                                dbc.Input(
                                    id="input-prob",  # dejo tu id original
                                    type="number",
                                    step=100,
                                    value=None,
                                    placeholder="Ej: 1000",
                                ),
                                dbc.FormText("Calcula la probabilidad de obtener un beneficio ≥ a este valor.")
                            ],
                            md=6,
                            className="mb-3"
                        ),
                    ],
                    className="g-3"
                ),
                dbc.Button(
                    [html.I(className="bi bi-play-fill me-2"), "Continuar"],
                    id="btn-continuar",
                    color="primary",
                    className="mt-2",
                    disabled=True  # se habilita con la validación
                ),
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
                dbc.Col(dbc.Alert([html.Strong("Probabilidad (≥ umbral): "), html.Span(id="kpi-prob")], color="light"), md=4),
                dbc.Col(dbc.Alert([html.Strong("Beneficio acumulado: "), html.Span(id="kpi-benef")], color="light"), md=4),
                dbc.Col(dbc.Alert([html.Strong("Filas: "), html.Span(id="kpi-rows")], color="light"), md=4),
            ],
            className="g-2"
        )
    ),
    className="shadow-sm"
)

tabla_card = dbc.Card(
    [
        dbc.CardHeader([html.I(className="bi bi-table me-2"), "Resultados Montecarlo"]),
        dbc.CardBody(
            DataTable(
                id="tabla",
                columns=[{"name": c, "id": c} for c in
                         ["Iteración", "rnd", "Ausentes", "Presentes", "Producción",
                          "Costo total", "Beneficio", "Beneficio acum.", "≥ umbral"]],
                data=[],
                page_action="none",          # ← sin paginación
                virtualization=True,         # ← renderiza solo lo visible
                fixed_rows={"headers": True},# ← header fijo al hacer scroll
                style_table={
                    "height": "60vh",        # altura del viewport (ajustá a gusto)
                    "overflowY": "auto",
                    "overflowX": "auto"
                },
                style_cell={
                    "fontFamily": "Inter, system-ui",
                    "fontSize": 13,
                    "minWidth": "110px"      # evita saltos si hay números largos
                },
            )
        ),
    ],
    className="shadow-sm"
)

# ----- Layout -----
app.layout = dbc.Container(
    [
        header,
        dbc.Row(
            dbc.Col(form_card, md=10, lg=8, xl=6, className="mx-auto"),
            className="justify-content-center mb-3"
        ),
        dbc.Row(
            dbc.Col(kpis, md=10, lg=10, xl=10, className="mx-auto"),
            className="justify-content-center mb-3"
        ),
        dbc.Row(
            dbc.Col(tabla_card, md=10, lg=10, xl=10, className="mx-auto"),
            className="justify-content-center mb-5"
        ),
        html.Footer(
            html.Div(
                [html.Span("Grupo nro 13")],
                className="text-center text-muted small mb-4"
            )
        ),
    ],
    fluid=True
)

# =======================
#  CALLBACKS
# =======================

# 1) Validación: habilitar/deshabilitar botón
@callback(
    Output("btn-continuar", "disabled"),
    Output("alerta", "children"),
    Input("input-nomina", "value"),
    Input("input-dias", "value"),
    Input("input-prob", "value"),
)
def validar(nomina, dias, umbral):
    msg = None
    disabled = True

    if nomina is None or dias is None or umbral is None:
        return True, msg

    # Validaciones según tus límites del formulario
    if not (21 <= int(nomina) <= 24):
        msg = dbc.Alert("La nómina debe estar entre 21 y 24.", color="warning", dismissable=True)
        return True, msg

    if int(dias) < 1 or int(dias) > 100000:
        msg = dbc.Alert("El número de días debe estar entre 1 y 100000.", color="warning", dismissable=True)
        return True, msg

    disabled = False
    return disabled, msg

# 2) Ejecutar Montecarlo y llenar tabla + KPIs
@callback(
    Output("tabla", "data"),
    Output("kpi-prob", "children"),
    Output("kpi-benef", "children"),
    Output("kpi-rows", "children"),
    Input("btn-continuar", "n_clicks"),
    State("input-nomina", "value"),
    State("input-dias", "value"),
    State("input-prob", "value"),
    prevent_initial_call=True
)
def ejecutar(_, nomina, dias, umbral):
    n = int(dias)
    cant_obreros = int(nomina)
    valor_mayor_que = float(umbral)

    prob, benef_acum, rows = Logica_Montercalo.ejecutar_montecarlo(n, cant_obreros, valor_mayor_que)

    return rows, f"{prob:.4f}", f"{benef_acum:.2f}", f"{len(rows)}"

if __name__ == "__main__":
    app.run(debug=True)