"""Dash application — entry point."""

import threading
import webbrowser

import dash
from dash import Input, Output, State, callback_context, Patch, no_update
import dash_bootstrap_components as dbc

from .controllers.dashboard_controller import DashboardController
from .views.dashboard import build_layout, build_main_content
from .utils.constants import SPORT_ICONS, CATEGORY_COLORS

# ── Initialise ─────────────────────────────────────────────────────────────────

ctrl = DashboardController()
ctrl.ensure_loaded()

app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.DARKLY,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css",
    ],
    suppress_callback_exceptions=True,
    title=ctrl.config["app"]["title"],
)

app.layout = build_layout(
    activity_options=ctrl.get_activity_options(),
    sport_options=ctrl.get_sport_options(),
)

# ── Callbacks ──────────────────────────────────────────────────────────────────

@app.callback(
    Output("activity-title",    "children"),
    Output("main-content",      "children"),
    Output("activity-dropdown", "options"),
    Input("activity-dropdown",  "value"),
    Input("reload-btn",         "n_clicks"),
    Input("refresh-btn",        "n_clicks"),
    Input("reload-store",       "data"),
    prevent_initial_call=False,
)
def update_main(file_id, reload_clicks, refresh_clicks, _reload_store):
    triggered = [t["prop_id"] for t in callback_context.triggered]

    if any("reload" in t for t in triggered):
        ctrl.reload()

    activity = ctrl.get_activity(file_id) if file_id else ctrl.get_latest()
    options  = ctrl.get_activity_options()

    if activity is None:
        return "No activity", build_main_content(None), options

    total_clicks = (reload_clicks or 0) + (refresh_clicks or 0)
    uirevision   = f"{activity.file_id}_{total_clicks}"

    title   = f"{activity.sport}  |  {activity.date_str}  |  {activity.distance_km} km"
    content = build_main_content(activity, uirevision=uirevision)
    return title, content, options


@app.callback(
    Output("sport-badge", "children"),
    Input("activity-dropdown", "value"),
    prevent_initial_call=False,
)
def update_sport_badge(file_id):
    from dash import html
    activity = ctrl.get_activity(file_id) if file_id else ctrl.get_latest()
    if activity is None:
        return html.Span("—", className="text-muted small")

    sport     = activity.sport
    category  = activity.sport_category
    icon      = SPORT_ICONS.get(sport, "person-running")
    color     = CATEGORY_COLORS.get(category, "#aaa")

    return html.Div([
        html.Div([
            html.I(className=f"fa-solid fa-{icon} me-2", style={"color": color}),
            html.Span(sport, style={"color": "#fff", "fontWeight": "600",
                                    "fontSize": "0.9rem"}),
        ], className="mb-1"),
        html.Span(
            category.capitalize(),
            style={
                "backgroundColor": color + "33",   # 20 % alpha
                "color": color,
                "border": f"1px solid {color}55",
                "borderRadius": "4px",
                "padding": "1px 8px",
                "fontSize": "0.72rem",
                "textTransform": "uppercase",
                "letterSpacing": "0.05em",
            },
        ),
    ])


@app.callback(
    Output("reload-store", "data"),
    Input("reload-btn", "n_clicks"),
    prevent_initial_call=True,
)
def trigger_reload(n):
    return n


@app.callback(
    Output("summary-chart", "figure"),   # Patch: move crosshair shape
    Output("map-graph",     "figure"),   # Patch: move red cursor dot
    Input("summary-chart",  "hoverData"),
    State("activity-dropdown", "value"),
    prevent_initial_call=True,
)
def on_chart_hover(hover_data, file_id):
    """
    Single callback fired on every chart hover:
      1. Moves the full-height crosshair line across ALL subplot panels.
      2. Moves the red GPS cursor on the map.
    Both updates use Patch() — only the changed fields are sent to the browser.
    """
    if not hover_data or not file_id:
        return no_update, no_update

    try:
        time_min = hover_data["points"][0]["x"]
    except (KeyError, IndexError):
        return no_update, no_update

    # ── 1. Crosshair: update the last shape (always the crosshair) ────────────
    chart_patch = Patch()
    chart_patch["layout"]["shapes"][-1]["x0"] = time_min
    chart_patch["layout"]["shapes"][-1]["x1"] = time_min
    chart_patch["layout"]["shapes"][-1]["line"]["color"] = "rgba(200,200,255,0.75)"
    chart_patch["layout"]["shapes"][-1]["line"]["width"] = 1.5

    # ── 2. Map cursor: find GPS at this time ──────────────────────────────────
    activity = ctrl.get_activity(file_id)
    if not activity or not activity.has_gps():
        return chart_patch, no_update

    from .services.transforms import find_sample_at_time
    from .controllers.map_controller import CURSOR_TRACE

    sample = find_sample_at_time(activity, time_min)
    if sample is None or sample.lat is None:
        return chart_patch, no_update

    map_patch = Patch()
    map_patch["data"][CURSOR_TRACE]["lat"] = [sample.lat]
    map_patch["data"][CURSOR_TRACE]["lon"] = [sample.lon]

    return chart_patch, map_patch


# ── Run ────────────────────────────────────────────────────────────────────────

def _open_browser(url: str, delay: float = 1.5):
    """Open browser after a short delay to let the server start."""
    import time
    time.sleep(delay)
    webbrowser.open(url)


if __name__ == "__main__":
    cfg  = ctrl.config["app"]
    host = cfg.get("host", "127.0.0.1")
    port = cfg.get("port", 8050)
    url  = f"http://{host}:{port}/"

    print(f"\n  Fitness Dashboard -> {url}\n")

    # Auto-open browser (daemon thread exits when main process exits)
    threading.Thread(target=_open_browser, args=(url,), daemon=True).start()

    app.run(
        debug=cfg.get("debug", True),
        host=host,
        port=port,
    )
