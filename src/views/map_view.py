"""Map view — interactive Plotly Scattermapbox with cursor tracking."""

from dash import html, dcc
from ..controllers.map_controller import build_plotly_map
from ..models.activity import Activity


def build_map_section(activity: Activity) -> html.Div:
    if not activity.has_gps():
        return html.Div(
            html.P("No GPS data for this activity.",
                   className="text-muted text-center py-4"),
            className="border rounded p-3 mb-3",
            style={"background": "#1a1a2e"},
        )

    fig = build_plotly_map(activity)
    if fig is None:
        return html.Div(
            html.P("GPS track too short to display.",
                   className="text-muted text-center py-4"),
        )

    return html.Div([
        html.H6("GPS Track", className="text-secondary mb-2"),
        dcc.Graph(
            id="map-graph",
            figure=fig,
            config={
                "displayModeBar": True,
                "modeBarButtonsToRemove": ["select2d", "lasso2d", "toImage"],
                "displaylogo": False,
                "scrollZoom": True,
            },
            style={"borderRadius": "10px", "overflow": "hidden"},
        ),
        html.P(
            "Hover on charts above to move the cursor on the map.",
            className="text-muted mt-1",
            style={"fontSize": "0.75rem"},
        ),
    ], className="mb-4")
