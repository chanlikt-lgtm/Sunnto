"""Sidebar: activity selector, date filter, sport filter."""

import dash_bootstrap_components as dbc
from dash import html, dcc


def build_sidebar(activity_options: list, sport_options: list = None) -> html.Div:
    return html.Div([
        html.H5("Fitness Dashboard", className="fw-bold mb-4 text-primary"),

        html.Label("Activity", className="fw-semibold small"),
        dcc.Dropdown(
            id="activity-dropdown",
            options=activity_options,
            value=activity_options[0]["value"] if activity_options else None,
            clearable=False,
            className="mb-3",
        ),

        html.Hr(),

        html.Label("Date Range", className="fw-semibold small"),
        dbc.RadioItems(
            id="date-range-radio",
            options=[
                {"label": "Last 7 days",  "value": "7d"},
                {"label": "Last 14 days", "value": "14d"},
                {"label": "Last 30 days", "value": "30d"},
                {"label": "Last 90 days", "value": "90d"},
                {"label": "All time",     "value": "all"},
            ],
            value="all",
            className="mb-3 small",
        ),

        html.Hr(),

        html.Label("Sport Type", className="fw-semibold small"),
        html.Div(id="sport-badge", className="mb-3"),

        html.Hr(),

        dbc.Button("Reload Data", id="reload-btn",
                   color="outline-secondary", size="sm",
                   className="w-100"),
    ], style={
        "width":     "240px",
        "minWidth":  "240px",
        "padding":   "20px 16px",
        "background": "#1a1a2e",
        "height":    "100vh",
        "overflowY": "auto",
        "position":  "fixed",
        "top":       0,
        "left":      0,
        "zIndex":    100,
    })
