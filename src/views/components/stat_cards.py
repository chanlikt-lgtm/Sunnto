"""Stat card components for the header row."""

import dash_bootstrap_components as dbc
from dash import html
from ...models.activity import Activity
from ...utils.datetime_utils import format_duration, format_pace


def build_stat_cards(activity: Activity):
    """Return a dbc.Row of metric cards for the selected activity."""
    m = activity.metrics

    cards_data = [
        ("Distance",   f"{activity.distance_km} km",        "primary"),
        ("Time",       format_duration(activity.duration_s), "info"),
        ("Avg HR",     _fmt(m.avg_hr, "bpm"),               "danger"),
        ("Avg Pace",   format_pace(m.avg_pace) + " /km",    "success"),
        ("Ascent",     f"{activity.ascent_m:.0f} m",         "warning"),
        ("Calories",   _fmt(m.calories, "kcal"),             "secondary"),
        ("VO2max",     _fmt(m.vo2max),                       "light"),
        ("Recovery",   _fmt(m.recovery_h, "h"),              "light"),
    ]

    return _cards_row(cards_data)


def build_gym_stat_cards(activity: Activity):
    """Stat cards for gym / indoor training / yoga / crossfit sessions."""
    m = activity.metrics
    cards_data = [
        ("Duration",  format_duration(activity.duration_s), "info"),
        ("Avg HR",    _fmt(m.avg_hr, "bpm"),                "danger"),
        ("Calories",  _fmt(m.calories, "kcal"),             "secondary"),
        ("EPOC",      _fmt(m.epoc),                         "warning"),
        ("Recovery",  _fmt(m.recovery_h, "h"),              "light"),
        ("Peak TE",   _fmt(m.peak_training_effect),         "primary"),
    ]
    return _cards_row(cards_data)


def build_sleep_stat_cards(activity: Activity):
    """Stat cards for sleep / meditation / rest sessions."""
    m = activity.metrics
    cards_data = [
        ("Duration", format_duration(activity.duration_s), "info"),
        ("Avg HR",   _fmt(m.avg_hr, "bpm"),                "danger"),
        ("Recovery", _fmt(m.recovery_h, "h"),              "light"),
        ("EPOC",     _fmt(m.epoc),                         "secondary"),
    ]
    return _cards_row(cards_data)


def build_swim_stat_cards(activity: Activity):
    """Stat cards for pool / open-water swimming sessions."""
    m = activity.metrics
    cards_data = [
        ("Distance",  f"{activity.distance_km} km",         "primary"),
        ("Time",      format_duration(activity.duration_s), "info"),
        ("Avg HR",    _fmt(m.avg_hr, "bpm"),                "danger"),
        ("Avg Pace",  format_pace(m.avg_pace) + " /km",     "success"),
        ("Calories",  _fmt(m.calories, "kcal"),             "secondary"),
        ("Recovery",  _fmt(m.recovery_h, "h"),              "light"),
    ]
    return _cards_row(cards_data)


def _cards_row(cards_data):
    cols = []
    for label, value, color in cards_data:
        cols.append(dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.P(label, className="text-muted mb-1",
                           style={"fontSize": "0.72rem", "textTransform": "uppercase"}),
                    html.H5(value, className="mb-0 fw-bold"),
                ])
            ], color=color, outline=True, className="h-100"),
            xs=6, sm=4, md=3, lg=2
        ))
    return dbc.Row(cols, className="g-2 mb-3")


def _fmt(val, unit=""):
    if val is None:
        return "--"
    if isinstance(val, float):
        val = round(val, 1)
    return f"{val} {unit}".strip()
