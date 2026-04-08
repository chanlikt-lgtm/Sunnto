"""Dash application — entry point."""

import threading
import webbrowser

import dash
from dash import Input, Output, State, callback_context
import dash_bootstrap_components as dbc

from .controllers.dashboard_controller import DashboardController
from .controllers.map_controller import CURSOR_TRACE
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
    Output("reload-store", "data"),
    Input("reload-btn", "n_clicks"),
    prevent_initial_call=True,
)
def trigger_reload(n):
    return n


@app.callback(
    Output("selected-activity-store", "data"),
    Output("activity-dropdown",       "options"),
    Input("activity-dropdown",        "value"),
    Input("reload-store",             "data"),
    Input("refresh-btn",              "n_clicks"),
    prevent_initial_call=False,
)
def select_activity(file_id, _reload_store, _refresh_clicks):
    triggered = [t["prop_id"] for t in callback_context.triggered]

    if any("reload" in t for t in triggered):
        ctrl.reload()

    options  = ctrl.get_activity_options()
    activity = ctrl.get_activity(file_id) if file_id else ctrl.get_latest()
    resolved_id = activity.file_id if activity else None

    return {"file_id": resolved_id}, options


@app.callback(
    Output("activity-title", "children"),
    Output("main-content",   "children"),
    Input("selected-activity-store", "data"),
    State("reload-store",            "data"),
    State("refresh-btn",             "n_clicks"),
    prevent_initial_call=False,
)
def render_activity(store_data, reload_data, refresh_clicks):
    file_id = (store_data or {}).get("file_id")
    activity = ctrl.get_activity(file_id) if file_id else None

    if activity is None:
        return "No activity", build_main_content(None)

    total_clicks = (reload_data or 0) + (refresh_clicks or 0)
    uirevision   = f"{activity.file_id}_{total_clicks}"

    title   = f"{activity.sport}  |  {activity.date_str}  |  {activity.distance_km} km"
    content = build_main_content(activity, uirevision=uirevision)
    return title, content


@app.callback(
    Output("sport-badge", "children"),
    Input("selected-activity-store", "data"),
    prevent_initial_call=False,
)
def update_sport_badge(store_data):
    from dash import html
    file_id  = (store_data or {}).get("file_id")
    activity = ctrl.get_activity(file_id) if file_id else None
    if activity is None:
        return html.Span("—", className="text-muted small")

    sport     = activity.sport
    category  = activity.sport_category
    icon      = SPORT_ICONS.get(sport, "person-running")
    color     = CATEGORY_COLORS.get(category.value if category else "", "#aaa")

    return html.Div([
        html.Div([
            html.I(className=f"fa-solid fa-{icon} me-2", style={"color": color}),
            html.Span(sport, style={"color": "#fff", "fontWeight": "600",
                                    "fontSize": "0.9rem"}),
        ], className="mb-1"),
        html.Span(
            category.value.capitalize(),
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
    Output("hover-data-store", "data"),
    Input("selected-activity-store", "data"),
    prevent_initial_call=False,
)
def precompute_hover_data(store_data):
    """
    Runs once per activity selection (not per hover).
    Stores a lean per-sample array for the clientside hover callback.
    """
    file_id  = (store_data or {}).get("file_id")
    activity = ctrl.get_activity(file_id) if file_id else None
    if not activity:
        return None
    return {
        "samples": [
            {
                "lat":     s.lat,
                "lon":     s.lon,
                "dist_km": round(s.distance / 1000.0, 3) if s.distance is not None else 0.0,
            }
            for s in activity.samples
        ],
        "cursor_trace_idx": CURSOR_TRACE,
    }


# ── Clientside hover callback — runs entirely in the browser (<20 ms) ──────────
app.clientside_callback(
    """
    function(hoverData, chartFig, mapFig, hoverStore) {
        var no_update = window.dash_clientside.no_update;

        if (!hoverData || !hoverStore || !chartFig) {
            return [no_update, no_update, no_update];
        }
        var pt = hoverData.points && hoverData.points[0];
        if (!pt) return [no_update, no_update, no_update];

        var timeMin = pt.x;
        var ptIdx   = pt.pointIndex;

        // ── 1. Crosshair — shallow-copy shapes array so Plotly diffs it ──────
        var shapes = chartFig.layout.shapes.slice();
        var last   = shapes.length - 1;
        shapes[last] = Object.assign({}, shapes[last], {
            x0: timeMin, x1: timeMin,
            line: {color: 'rgba(200,200,255,0.75)', width: 1.5}
        });
        var chartOut = Object.assign({}, chartFig, {
            layout: Object.assign({}, chartFig.layout, {shapes: shapes})
        });

        // ── 2 & 3. GPS cursor + distance ──────────────────────────────────────
        var mapOut   = no_update;
        var distText = '0.00 km';

        if (ptIdx !== undefined && ptIdx !== null) {
            var s = hoverStore.samples[ptIdx];
            if (s) {
                if (s.lat !== null && s.lat !== undefined && mapFig) {
                    var data = mapFig.data.slice();
                    var ci   = hoverStore.cursor_trace_idx;
                    data[ci] = Object.assign({}, data[ci], {lat: [s.lat], lon: [s.lon]});
                    mapOut = Object.assign({}, mapFig, {data: data});
                }
                if (s.dist_km > 0) {
                    distText = s.dist_km.toFixed(2) + ' km';
                }
            }
        }

        return [chartOut, mapOut, distText];
    }
    """,
    Output("summary-chart",   "figure"),
    Output("map-graph",       "figure"),
    Output("cursor-distance", "children"),
    Input("summary-chart",    "hoverData"),
    State("summary-chart",    "figure"),
    State("map-graph",        "figure"),
    State("hover-data-store", "data"),
    prevent_initial_call=True,
)


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
