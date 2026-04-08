"""Map view — wraps folium HTML in a Dash iframe."""

from dash import html
from ..controllers.map_controller import build_map
from ..models.activity import Activity


def build_map_section(activity: Activity) -> html.Div:
    if not activity.has_gps():
        return html.Div(
            html.P("No GPS data for this activity.",
                   className="text-muted text-center py-4"),
            className="border rounded p-3 mb-3",
            style={"background": "#1a1a2e"},
        )

    map_html = build_map(activity)
    if not map_html:
        return html.Div(
            html.P("GPS track too short to display.",
                   className="text-muted text-center py-4"),
        )

    return html.Div([
        html.H6("GPS Track", className="text-secondary mb-2"),
        html.Iframe(
            srcDoc=map_html,
            style={
                "width":  "100%",
                "height": "420px",
                "border": "none",
                "borderRadius": "6px",
            },
        ),
    ], className="mb-4")
