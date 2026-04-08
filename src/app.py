"""Dash application — entry point."""

import dash
from dash import Input, Output, State, callback_context
import dash_bootstrap_components as dbc

from .controllers.dashboard_controller import DashboardController
from .views.dashboard import build_layout, build_main_content

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
    Output("activity-title", "children"),
    Output("main-content",   "children"),
    Output("activity-dropdown", "options"),
    Input("activity-dropdown", "value"),
    Input("reload-btn",         "n_clicks"),
    Input("reload-store",       "data"),
    prevent_initial_call=False,
)
def update_main(file_id, _reload_btn, _reload_store):
    triggered = [t["prop_id"] for t in callback_context.triggered]

    if any("reload" in t for t in triggered):
        ctrl.reload()

    activity = ctrl.get_activity(file_id) if file_id else ctrl.get_latest()

    options = ctrl.get_activity_options()

    if activity is None:
        return "No activity", build_main_content(None), options

    title = f"{activity.sport}  |  {activity.date_str}  |  {activity.distance_km} km"
    content = build_main_content(activity)
    return title, content, options


@app.callback(
    Output("reload-store", "data"),
    Input("reload-btn", "n_clicks"),
    prevent_initial_call=True,
)
def trigger_reload(n):
    return n


# ── Run ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    cfg = ctrl.config["app"]
    print(f"\n  Fitness Dashboard starting on http://{cfg.get('host','127.0.0.1')}:{cfg.get('port',8050)}/\n")
    app.run(
        debug=cfg.get("debug", True),
        host=cfg.get("host", "127.0.0.1"),
        port=cfg.get("port", 8050),
    )
