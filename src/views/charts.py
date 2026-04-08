"""Build Plotly chart figures for a single activity."""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Optional

from ..models.activity import Activity
from ..services.transforms import chart_dataframe, lap_cumulative_minutes
from ..utils.constants import CHART_COLORS, PACE_SLOW_MIN_KM, PACE_FAST_MIN_KM, HR_MAX_DEFAULT
from ..utils.datetime_utils import format_pace


_HEIGHT = 220   # px per subplot row

_ZONE_COLORS = [
    "#3fb950",   # Z1 green
    "#8bc34a",   # Z2 yellow-green
    "#f0a050",   # Z3 amber
    "#e05c5c",   # Z4 red
    "#c084fc",   # Z5 purple
]

# Human-readable names shown in the unified hover tooltip
_PANEL_META = {
    "hr":       ("Heart Rate", "bpm"),
    "pace":     ("Pace",       "min/km"),
    "altitude": ("Altitude",   "m"),
}


def build_summary_chart(activity: Activity,
                        uirevision: str = "activity",
                        allowed_panels: list = None) -> Optional[go.Figure]:
    """
    Stacked subplot: HR (with zone bands) / Pace / Altitude.
    - hovermode='x unified'  → single tooltip showing all values
    - Spike line drawn across every panel with the cursor
    - Lap boundaries as dashed vertical lines
    """
    df = chart_dataframe(activity)
    if df.empty:
        return None

    panels = []
    for col in ["hr", "pace", "altitude"]:
        if allowed_panels and col not in allowed_panels:
            continue
        if col in df.columns and df[col].notna().sum() > 5:
            title, unit = _PANEL_META[col]
            color = CHART_COLORS[col if col != "altitude" else "alt"]
            panels.append((col, title, unit, color))

    if not panels:
        return None

    rows = len(panels)
    fig = make_subplots(
        rows=rows, cols=1,
        shared_xaxes=True,
        subplot_titles=[p[1] for p in panels],
        vertical_spacing=0.08,
    )

    for r, (col, title, unit, color) in enumerate(panels, start=1):
        y = df[col]

        if col == "hr":
            _add_hr_zone_bands(fig, df, activity, r)

        fig.add_trace(go.Scatter(
            x=df["min"],
            y=y,
            mode="lines",
            line=dict(color=color, width=2),
            fill="tozeroy" if col != "hr" else None,
            fillcolor=_alpha(color, 0.10) if col != "hr" else None,
            # ── Hover label shown in unified tooltip ─────────────────────────
            name=title,
            # No <extra></extra> so trace name IS shown in unified mode
            hovertemplate=f"<b>%{{y:.1f}}</b> {unit}",
        ), row=r, col=1)

        if col == "pace":
            fig.update_yaxes(autorange="reversed", row=r, col=1)

    # ── Explicit axis ranges — adapt to each file's actual data ─────────────
    x_max = df["min"].max()
    fig.update_xaxes(range=[0, x_max * 1.02])   # 2 % right-padding

    for r, (col, _, _, _) in enumerate(panels, start=1):
        series = df[col].dropna()
        if series.empty:
            continue
        y_lo, y_hi = series.min(), series.max()
        pad = (y_hi - y_lo) * 0.10 or 1.0   # at least 1 unit of padding
        if col == "pace":
            # reversed axis: higher value (slower) at bottom
            fig.update_yaxes(range=[y_hi + pad, max(0, y_lo - pad)], row=r, col=1)
        elif col == "hr":
            fig.update_yaxes(range=[max(0, y_lo - pad), y_hi + pad], row=r, col=1)
        else:
            fig.update_yaxes(range=[y_lo - pad, y_hi + pad], row=r, col=1)

    # ── Layout ────────────────────────────────────────────────────────────────
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#12122a",
        plot_bgcolor="#12122a",
        height=rows * _HEIGHT,
        showlegend=False,
        margin=dict(l=65, r=20, t=35, b=45),
        uirevision=uirevision,
        # Unified tooltip: one box with all trace values at cursor x
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="rgba(15,15,40,0.95)",
            bordercolor="#555",
            font=dict(size=13, color="#ffffff"),
            namelength=-1,
        ),
    )

    # Grid + bottom x label
    fig.update_xaxes(showgrid=True, gridcolor="#1e1e3a",
                     showspikes=False)   # disabled — shape handles crosshair
    fig.update_yaxes(showgrid=True, gridcolor="#1e1e3a", showspikes=False)
    fig.update_xaxes(title_text="Time (min)", row=rows, col=1)

    # ── Lap boundary lines ────────────────────────────────────────────────────
    for i, t_min in enumerate(lap_cumulative_minutes(activity)):
        fig.add_vline(
            x=t_min,
            line_width=1,
            line_dash="dash",
            line_color="#446",
            annotation_text=f"L{i + 2}",
            annotation_position="top left",
            annotation_font=dict(size=10, color="#778"),
        )

    # ── Full-height crosshair shape (MUST be last shape) ─────────────────────
    # xref="x"     → x position in shared data coordinates (minutes)
    # yref="paper" → y spans 0–1 = entire figure = ALL subplot panels
    # Updated by on_chart_hover callback via Patch()["layout"]["shapes"][-1]
    fig.add_shape(
        type="line",
        xref="x", yref="paper",
        x0=0, x1=0,
        y0=0, y1=1,
        line=dict(color="rgba(200,200,255,0)", width=0),  # invisible until hover
        layer="above",
    )

    return fig


def build_hr_zones_bar(activity: Activity,
                       uirevision: str = "activity") -> Optional[go.Figure]:
    """Horizontal bar chart of time in each HR zone."""
    if not activity.metrics or not activity.metrics.hr_zones:
        return None
    hz    = activity.metrics.hr_zones
    zones = ["Z1", "Z2", "Z3", "Z4", "Z5"]
    times = [hz.z1_s / 60, hz.z2_s / 60, hz.z3_s / 60,
             hz.z4_s / 60, hz.z5_s / 60]

    thresh = hz.thresholds_bpm()
    labels = ["< Z2 threshold"]
    for i, t in enumerate(thresh):
        labels.append(f">= {int(t)} bpm" if t else f"Z{i + 2}")

    fig = go.Figure(go.Bar(
        y=zones, x=times,
        orientation="h",
        marker_color=_ZONE_COLORS,
        text=[f"{t:.0f} min" for t in times],
        textposition="outside",
        customdata=labels,
        hovertemplate="%{y}: <b>%{x:.1f} min</b>  (%{customdata})<extra></extra>",
    ))
    x_max = max(t for t in times if t > 0) if any(t > 0 for t in times) else 1
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#12122a",
        plot_bgcolor="#12122a",
        height=180,
        title=dict(text="Time in HR Zones", font=dict(size=13)),
        showlegend=False,
        xaxis=dict(title="minutes", range=[0, x_max * 1.15]),
        margin=dict(l=40, r=70, t=35, b=30),
        uirevision=uirevision,
    )
    return fig


# ── Private helpers ────────────────────────────────────────────────────────────

def _add_hr_zone_bands(fig, df: pd.DataFrame, activity: Activity, row: int):
    hz = activity.metrics and activity.metrics.hr_zones
    if not hz:
        return

    hr_max = (df["hr"].max() if df["hr"].notna().any() else HR_MAX_DEFAULT) * 1.06
    thresholds = hz.thresholds_bpm()
    if not any(thresholds):
        thresholds = [hr_max * p for p in (0.60, 0.70, 0.80, 0.90)]

    boundaries = [0] + [t for t in thresholds if t] + [hr_max]
    yref = "y" if row == 1 else f"y{row}"

    for i in range(len(boundaries) - 1):
        color = _ZONE_COLORS[min(i, len(_ZONE_COLORS) - 1)]
        fig.add_shape(
            type="rect",
            xref="paper", yref=yref,
            x0=0, x1=1,
            y0=boundaries[i], y1=boundaries[i + 1],
            fillcolor=_alpha(color, 0.14),
            line_width=0,
            layer="below",
        )


def _alpha(hex_color: str, a: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{a})"
