from dash import Dash, callback, Output, Input, html
import plotly.express as px
import dash_bootstrap_components as dbc


app = Dash(  __name__,
    title="TP 2",
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP])

titl = dbc.Container(
    html.Div(
        html.P("Montecarlo - Caso: Ausencia de empleados automotrices"), className="title text-center"
    )
)

# Requires Dash 2.17.0 or later
app.layout = [
    titl
]

@callback(
    Output('graph-content', 'figure'),
    Input('dropdown-selection', 'value')
)
def update_graph(value):
    return px.line(x='year', y='pop')

if __name__ == '__main__':
    app.run(debug=True)
