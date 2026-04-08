"""Main dashboard layout definition."""

from dash import html, dcc
import dash_bootstrap_components as dbc

from .components.sidebar import build_sidebar
from .components.stat_cards import build_stat_cards


def build_layout(activity_options: list, sport_options: list) -> html.Div:
    return html.Div([
        # Sidebar (fixed left)
        build_sidebar(activity_options, sport_options),

        # Main panel (offset by sidebar width)
        html.Div([
            # Header bar
            dbc.Row([
                dbc.Col(html.Div(id="activity-title",
                                  className="h4 mb-0 text-white fw-bold"), width="auto"),
                dbc.Col(dbc.Button("Refresh", id="refresh-btn",
                                   color="outline-light", size="sm"), width="auto"),
            ], className="align-items-center mb-3 pt-3 px-3"),

            # Content area
            html.Div(id="main-content", className="px-3 pb-4"),

            # Store for reloads
            dcc.Store(id="reload-store"),
        ], style={"marginLeft": "240px", "minHeight": "100vh",
                  "background": "#0d0d1a"}),
    ], style={"fontFamily": "Inter, sans-serif"})


def build_main_content(activity, no_activity_msg: str = None,
                       uirevision: str = "activity"):
    """
    Build: stat cards -> summary chart -> map -> lap table.
    uirevision changes on activity switch or Refresh → resets zoom.
    """
    if activity is None:
        return html.Div(html.P(no_activity_msg or "Select an activity from the sidebar.",
                               className="text-muted py-5 text-center"))

    parts = [
        build_stat_cards(activity),
        html.H6("Performance Charts", className="text-secondary mb-2 mt-2"),
        _chart_section(activity, uirevision),
        build_map_section(activity),
        _lap_section(activity),
    ]
    return html.Div(parts)


def _chart_section(activity, uirevision="activity"):
    from .charts import build_summary_chart, build_hr_zones_bar

    fig = build_summary_chart(activity, uirevision=uirevision)
    zones_fig = build_hr_zones_bar(activity, uirevision=uirevision)

    if fig is None:
        return html.P("No chart data available.", className="text-muted")

    parts = [
        dcc.Graph(id="summary-chart",
                  figure=fig,
                  config={"displayModeBar": True,
                          "modeBarButtonsToRemove": ["select2d", "lasso2d"],
                          "displaylogo": False},
                  className="mb-2"),
    ]
    if zones_fig:
        parts.append(dcc.Graph(figure=zones_fig,
                               config={"displayModeBar": False},
                               className="mb-2"))

    return html.Div(parts, className="mb-3 rounded",
                    style={"background": "#12122a", "padding": "4px"})


def _lap_section(activity):
    from ..services.transforms import lap_table
    from dash import dash_table

    rows = lap_table(activity)
    if not rows:
        return html.Div()

    return html.Div([
        html.H6("Laps", className="text-secondary mb-2"),
        dash_table.DataTable(
            data=rows,
            columns=[{"name": k, "id": k} for k in rows[0].keys()],
            style_table={"overflowX": "auto"},
            style_header={
                "backgroundColor": "#1a1a2e",
                "color":           "#aaa",
                "fontWeight":      "bold",
                "fontSize":        "0.8rem",
            },
            style_cell={
                "backgroundColor": "#12122a",
                "color":           "#ddd",
                "border":          "1px solid #333",
                "fontSize":        "0.82rem",
                "padding":         "6px 12px",
                "textAlign":       "center",
            },
            style_data_conditional=[
                {"if": {"row_index": "odd"},
                 "backgroundColor": "#161628"},
            ],
        ),
    ], className="mb-4")
