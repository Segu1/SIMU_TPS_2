# =======================
#  APP
# =======================
from dash import Output, Input, State, Dash, html, dcc, exceptions
from dash.dash_table import DataTable
import dash_bootstrap_components as dbc
import math as _math

import Logica_Montercalo


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
            "Además, definí un beneficio umbral para calcular la probabilidad.",
            className="lead text-center text-muted mb-4"
        ),
    ],
    fluid=True
)

# ----- Tarjeta con formulario -----
form_card = dbc.Card(
    [
        dbc.CardHeader([html.I(className="bi bi-sliders me-2"),
                        html.Strong("Parámetros de Montecarlo")]),
        dbc.CardBody(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label("Tamaño de nómina (empleados)"),
                                dbc.Input(id="input-nomina", type="number",
                                          min=21, max=24, step=1, value=21, required=True),
                                dbc.FormText("Cantidad total de empleados a evaluar."),
                            ],
                            md=6, className="mb-3"
                        ),
                        dbc.Col(
                            [
                                dbc.Label("Número de días (n)"),
                                dbc.Input(id="input-dias", type="number",
                                          min=1, max=100000, step=1, value=10, required=True),
                                dbc.FormText("Cantidad de iteraciones a evaluar."),
                            ],
                            md=6, className="mb-3"
                        ),
                        dbc.Col(
                            [
                                dbc.Label("Beneficio umbral"),
                                dbc.Input(id="input-prob", type="number",
                                          min=1, step=1, value=100, required=True),
                                dbc.Label("Mostrar desde la fila (j)"),
                                dbc.Input(id="input-fila-desde", type="number",
                                          min=1, step=1, value=1, required=True),
                                dbc.Label("Mostrar hasta la fila (i)"),
                                dbc.Input(id="input-fila-hasta", type="number",
                                          min=1, step=1, value=10, required=True),
                                dbc.FormText("Se verá el rango [j..i]. Siempre se muestra la última fila."),
                            ],
                            md=6, className="mb-3"
                        ),
                    ],
                    className="g-3"
                ),
                dbc.Button([html.I(className="bi bi-play-fill me-2"), "Continuar"],
                           id="btn-continuar", color="primary", className="mt-2", disabled=True),
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
                dbc.Col(dbc.Alert([html.Strong("Filas: "),
                                   html.Span(id="kpi-rows")], color="light"), md=4),
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

# ----- Stores + Interval -----
runtime_helpers = dbc.Container(
    [
        dcc.Store(id="sim-state"),   # estado + rango normalizado
        dcc.Store(id="rows-store"),  # dict: {"10": row10, "11": row11, ...} SOLO [j..i]
        dcc.Interval(id="tick", interval=16, disabled=True)  # ~60fps
    ],
    style={"display": "none"}
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
        runtime_helpers,
        html.Footer(html.Div([html.Span("Grupo nro 13")],
                             className="text-center text-muted small mb-4")),
    ],
    fluid=True
)

# =======================
#  HELPERS
# =======================
def _num_or_none(x, cast=int):
    if x in (None, ""):
        return None
    try:
        return cast(x)
    except Exception:
        try:
            return cast(float(str(x).replace(",", ".")))
        except Exception:
            return None

def _jsonify_row(row: dict):
    import numbers as _numbers
    from decimal import Decimal
    import datetime as _dt
    out = {}
    for k, v in row.items():
        if v is None or isinstance(v, (str, int, float, bool)):
            out[k] = v; continue
        if isinstance(v, Decimal):
            out[k] = float(v); continue
        if isinstance(v, (_dt.datetime, _dt.date)):
            out[k] = v.isoformat(); continue
        if isinstance(v, _numbers.Number):
            out[k] = int(v) if float(v).is_integer() else float(v); continue
        try:
            out[k] = v.item()
        except Exception:
            out[k] = str(v)
    return out

# =======================
#  CALLBACKS
# =======================

# Validación
@app.callback(
    Output("btn-continuar", "disabled"),
    Output("alerta", "children"),
    Input("input-nomina", "value"),
    Input("input-dias", "value"),
    Input("input-prob", "value"),
    Input("input-fila-desde", "value"),
    Input("input-fila-hasta", "value"),
)
def validar(nomina, dias, umbral, j, i):
    nomina_i = _num_or_none(nomina, int)
    dias_i   = _num_or_none(dias, int)
    umbral_f = _num_or_none(umbral, int)
    j_i      = _num_or_none(j, int)
    i_i      = _num_or_none(i, int)

    if None in (nomina_i, dias_i, umbral_f, j_i, i_i):
        return True, dbc.Alert("Completá todos los campos.", color="warning", dismissible=True)
    if not (21 <= nomina_i <= 24):
        return True, dbc.Alert("La nómina debe estar entre 21 y 24.", color="warning", dismissible=True)
    if not (1 <= dias_i <= 100000):
        return True, dbc.Alert("El número de días debe estar entre 1 y 100000.", color="warning", dismissible=True)
    if j_i < 1 or i_i < 1:
        return True, dbc.Alert("«Desde (j)» e «Hasta (i)» deben ser ≥ 1.", color="warning", dismissible=True)
    return False, None

# Inicializar (normaliza rango y limpia store)
@app.callback(
    Output("sim-state", "data", allow_duplicate=True),
    Output("rows-store", "data", allow_duplicate=True),
    Output("tick", "disabled", allow_duplicate=True),
    Output("tick", "n_intervals"),
    Input("btn-continuar", "n_clicks"),
    State("input-nomina", "value"),
    State("input-dias", "value"),
    State("input-prob", "value"),
    State("input-fila-desde", "value"),
    State("input-fila-hasta", "value"),
    prevent_initial_call=True
)
def iniciar_sim(n_clicks, nomina, dias, umbral, j, i):
    if not n_clicks:
        raise exceptions.PreventUpdate

    a = int(j) if j not in (None, "") else 1
    b = int(i) if i not in (None, "") else int(dias)
    lo, hi = (a, b) if a <= b else (b, a)   # NORMALIZADO

    state = {
        "n": int(dias),
        "cant_obreros": int(nomina),
        "umbral": float(umbral),
        "i": 0,
        "beneficio_acum": 0.0,
        "ocurrencias": 0,
        "lo": int(lo),   # desde (normalizado)
        "hi": int(hi)    # hasta (normalizado)
    }
    return state, {}, False, 0  # dict vacío y arranca

STEPS_PER_TICK = 10

@app.callback(
    Output("tabla", "data"),
    Output("kpi-prob", "children"),
    Output("kpi-benef", "children"),
    Output("kpi-rows", "children"),
    Output("sim-state", "data", allow_duplicate=True),
    Output("rows-store", "data", allow_duplicate=True),
    Output("tick", "disabled", allow_duplicate=True),
    Input("tick", "n_intervals"),
    State("sim-state", "data"),
    State("rows-store", "data"),
    prevent_initial_call=True
)
def avanzar_iter(_, state, pinned_map):
    import math as _math_local

    if not state:
        return [], "", "", "0", state, {}, True

    # --- RANGO NORMALIZADO ---
    n   = int(state.get("n", 1))
    lo  = max(1, int(state.get("lo", 1)))
    hi  = min(int(state.get("hi", n)), n)     # tope real
    i0  = int(state.get("i", 0))

    pinned_map = (pinned_map or {}).copy()    # {"8": row8, ...}
    new_state  = state
    last_row   = None

    # --- AVANCE EN LOTE ---
    steps = min(STEPS_PER_TICK, max(0, n - i0))
    for _ in range(steps):
        new_state, row, _ = Logica_Montercalo.montecarlo_step(new_state)
        row = _jsonify_row(row)
        last_row = row

        it = row.get("Iteración")
        try:
            it_int = int(it)
        except Exception:
            it_int = None

        if it_int is not None and lo <= it_int <= hi:
            pinned_map[str(it_int)] = row

    # --- PURGA ESTRICTA DEL STORE ---
    if pinned_map:
        keys_ok = {str(k) for k in range(lo, hi + 1)}
        pinned_map = {k: v for k, v in pinned_map.items() if k in keys_ok}

    # --- KPIs ---
    i_actual = int(new_state.get("i", 0))
    ocurr    = int(new_state.get("ocurrencias", 0))
    pval     = (ocurr / i_actual) if i_actual > 0 else 0.0
    kpi_prob  = f"{_math_local.trunc(pval * 10000)/10000:.4f}"
    kpi_benef = f"{float(new_state.get('beneficio_acum', 0.0)):.2f}"
    kpi_rows  = f"{i_actual}"

    # --- CONJUNTO DE ÍNDICES PERMITIDOS ---
    allowed = set(range(lo, hi + 1))
    if i_actual > hi:
        allowed.add(i_actual)  # una sola extra: la última

    # --- ARMADO *DURO* DE VISIBLE ---
    pool = list(pinned_map.values())
    if last_row is not None:
        pool.append(last_row)

    # filtro por índices permitidos y deduplicación por iteración
    pick = {}
    for r in pool:
        try:
            itx = int(r.get("Iteración"))
        except Exception:
            continue
        if itx in allowed:
            pick[itx] = r  # la última gana (dedupe)

    # ordenar: primero lo..hi, y al final i_actual (si está fuera del rango)
    order = [k for k in range(lo, hi + 1) if k in pick]
    if i_actual in pick and i_actual > hi:
        order.append(i_actual)

    visible = [pick[k] for k in order]

    detener = (i_actual >= n)
    return visible, kpi_prob, kpi_benef, kpi_rows, new_state, pinned_map, detener


if __name__ == "__main__":
    app.run(debug=True)
