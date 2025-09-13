from dash import Dash, html
import dash_bootstrap_components as dbc

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
            "Ingresá el tamaño de la nómina y la probabilidad de ausencia para tu modelo.",
            className="lead text-center text-muted mb-4"
        ),
    ],
    fluid=True
)

# ----- Tarjeta con formulario (solo UI) -----
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
                                    min=21,
                                    max=24,
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
                                dbc.Label("Beneficio a evaluar"),
                                dbc.Input(
                                    id="input-prob",
                                    type="number",
                                    step=100,
                                    value=None,
                                    placeholder="Ej: 1000",
                                ),
                                dbc.FormText("Por ejemplo: 600"),
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
                    disabled=True  # por ahora deshabilitado: solo interfaz
                ),
                html.Div(
                    "Esta es una interfaz de ejemplo. Conectá tu callback/simulación aquí.",
                    className="text-muted small mt-3"
                ),
            ]
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

if __name__ == "__main__":
    app.run(debug=True)
