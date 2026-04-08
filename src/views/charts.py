"""Build Plotly chart figures for a single activity."""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Optional

from ..models.activity import Activity
from ..services.transforms import chart_dataframe, lap_cumulative_minutes
from ..utils.constants import CHART_COLORS
from ..utils.datetime_utils import format_pace


_HEIGHT = 210   # px per subplot row

# Zone colours (semi-transparent fill bands)
_ZONE_COLORS = [
    "#3fb950",   # Z1 green
    "#8bc34a",   # Z2 yellow-green
    "#f0a050",   # Z3 amber
    "#e05c5c",   # Z4 red
    "#c084fc",   # Z5 purple
]


def build_summary_chart(activity: Activity) -> Optional[go.Figure]:
    """
    Stacked subplot: HR (with zone bands) / Pace / Altitude.
    All subplots share the x-axis so zoom syncs across all panels.
    """
    df = chart_dataframe(activity)
    if df.empty:
        return None

    panels = []
    for col, title, unit, color in [
        ("hr",       "Heart Rate (bpm)",  "bpm",    CHART_COLORS["hr"]),
        ("pace",     "Pace (min/km)",     "min/km", CHART_COLORS["pace"]),
        ("altitude", "Altitude (m)",      "m",      CHART_COLORS["alt"]),
    ]:
        if col in df.columns and df[col].notna().sum() > 5:
            panels.append((col, title, unit, color))

    if not panels:
        return None

    rows = len(panels)
    fig = make_subplots(
        rows=rows, cols=1,
        shared_xaxes=True,
        subplot_titles=[p[1] for p in panels],
        vertical_spacing=0.07,
    )

    for r, (col, title, unit, color) in enumerate(panels, start=1):
        y = df[col]

        # Gradient fill: add a filled area trace per zone for HR
        if col == "hr":
            _add_hr_zone_bands(fig, df, activity, r)

        fig.add_trace(go.Scatter(
            x=df["min"], y=y,
            mode="lines",
            line=dict(color=color, width=2),
            fill="tozeroy" if col != "hr" else None,
            fillcolor=_alpha(color, 0.10) if col != "hr" else None,
            name=col,
            hovertemplate=f"%{{y:.1f}} {unit}<extra></extra>",
        ), row=r, col=1)

        if col == "pace":
            fig.update_yaxes(autorange="reversed", row=r, col=1)

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#12122a",
        plot_bgcolor="#12122a",
        height=rows * _HEIGHT,
        showlegend=False,
        margin=dict(l=60, r=20, t=35, b=45),
        uirevision="activity",
        # ── Unified crosshair hover ──────────────────────────────────────────
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#1e1e3a",
            bordercolor="#333",
            font=dict(size=12, color="#eee"),
        ),
    )
    fig.update_xaxes(
        title_text="Time (min)", row=rows, col=1,
        # Spike line (vertical crosshair across all panels)
        showspikes=True,
        spikecolor="#666",
        spikethickness=1,
        spikedash="dot",
        spikemode="across+toaxis",
        spikesnap="cursor",
    )
    for r in range(1, rows + 1):
        fig.update_xaxes(showgrid=True, gridcolor="#1e1e3a",
                         showspikes=True, spikecolor="#666",
                         spikethickness=1, spikedash="dot",
                         spikemode="across", row=r, col=1)
        fig.update_yaxes(showgrid=True, gridcolor="#1e1e3a",
                         showspikes=True, spikecolor="#444",
                         spikethickness=1, spikedash="dot",
                         row=r, col=1)

    # ── Lap boundary markers ─────────────────────────────────────────────────
    lap_times = lap_cumulative_minutes(activity)
    for i, t_min in enumerate(lap_times):
        fig.add_vline(
            x=t_min,
            line_width=1,
            line_dash="dash",
            line_color="#444",
            annotation_text=f"L{i+2}",
            annotation_position="top left",
            annotation_font=dict(size=10, color="#666"),
        )

    return fig


def build_hr_zones_bar(activity: Activity) -> Optional[go.Figure]:
    """Horizontal bar chart of time in each HR zone."""
    if not activity.metrics or not activity.metrics.hr_zones:
        return None
    hz = activity.metrics.hr_zones
    zones  = ["Z1", "Z2", "Z3", "Z4", "Z5"]
    times  = [hz.z1_s/60, hz.z2_s/60, hz.z3_s/60, hz.z4_s/60, hz.z5_s/60]

    # Build threshold labels
    thresh = hz.thresholds_bpm()   # [z2, z3, z4, z5]
    labels = ["< Z2"]
    for i, t in enumerate(thresh):
        labels.append(f">= {int(t)} bpm" if t else f"Z{i+2}")

    fig = go.Figure(go.Bar(
        y=zones,
        x=times,
        orientation="h",
        marker_color=_ZONE_COLORS,
        text=[f"{t:.0f} min" for t in times],
        textposition="outside",
        customdata=labels,
        hovertemplate="%{y}: %{x:.1f} min  (%{customdata})<extra></extra>",
    ))
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#12122a",
        plot_bgcolor="#12122a",
        height=180,
        title=dict(text="Time in HR Zones", font=dict(size=13)),
        showlegend=False,
        xaxis_title="minutes",
        margin=dict(l=40, r=60, t=35, b=30),
        uirevision="activity",
    )
    return fig


# ── Private helpers ────────────────────────────────────────────────────────────

def _add_hr_zone_bands(fig, df: pd.DataFrame, activity: Activity, row: int):
    """
    Add horizontal coloured bands behind the HR trace, one per zone.
    Uses actual bpm thresholds from the Suunto file when available.
    """
    hz = activity.metrics and activity.metrics.hr_zones
    if not hz:
        return

    hr_max = df["hr"].max() if df["hr"].notna().any() else 220
    hr_max = max(hr_max * 1.05, hr_max + 5)

    thresholds = hz.thresholds_bpm()   # [z2, z3, z4, z5]
    # Fall back to 60/70/80/90 % of max HR if no thresholds stored
    if not any(thresholds):
        thresholds = [hr_max * p for p in (0.60, 0.70, 0.80, 0.90)]

    boundaries = [0] + [t for t in thresholds if t] + [hr_max]

    # yref for this row: 'y' for row 1, 'y2' for row 2, etc.
    yref = "y" if row == 1 else f"y{row}"

    for i in range(len(boundaries) - 1):
        lo = boundaries[i]
        hi = boundaries[i + 1]
        color = _ZONE_COLORS[min(i, len(_ZONE_COLORS) - 1)]
        fig.add_shape(
            type="rect",
            xref="paper", yref=yref,
            x0=0, x1=1,
            y0=lo, y1=hi,
            fillcolor=_alpha(color, 0.14),
            line_width=0,
            layer="below",
        )


def _alpha(hex_color: str, a: float) -> str:
    """Convert #rrggbb to rgba(r,g,b,a)."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{a})"
