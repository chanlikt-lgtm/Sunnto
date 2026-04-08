"""Generate Plotly Scattermapbox map for interactive cursor tracking."""

import colorsys
import plotly.graph_objects as go
import folium
from ..models.activity import Activity
from ..services.transforms import gps_track

# Pace colour scale bounds (min/km)
_PACE_SLOW = 8.0
_PACE_FAST = 4.5

# Trace indices in the Plotly map figure (must match build_plotly_map order)
TRACK_TRACE  = 0
START_TRACE  = 1
CURSOR_TRACE = 2


def build_plotly_map(activity: Activity):
    """
    Interactive Plotly Scattermapbox map.
    Trace layout:
      0 — GPS track (lines, pace-colored via multiple segments)
      1 — Start marker (green)
      2 — Cursor marker (red, moved by hover callback)
    Returns go.Figure or None if no GPS.
    """
    samples = [s for s in activity.samples if s.lat is not None]
    if len(samples) < 2:
        return None

    # Downsample for performance
    step = max(1, len(samples) // 600)
    pts  = samples[::step]

    lats = [s.lat for s in pts]
    lons = [s.lon for s in pts]
    centre = (sum(lats) / len(lats), sum(lons) / len(lons))

    fig = go.Figure()

    # ── Track — one segment per color bucket ──────────────────────────────────
    # Group consecutive points by pace bucket (10 buckets) for coloring.
    # We use None separators within a single trace for gaps between buckets,
    # but a simpler approach: draw one line with a colorscale on markers.
    fig.add_trace(go.Scattermapbox(
        lat=lats,
        lon=lons,
        mode="lines+markers",
        line=dict(width=3, color="#3fb950"),
        marker=dict(
            size=5,
            color=[_pace_norm(s.pace) for s in pts],
            colorscale=[[0, "#27c93f"], [0.5, "#f0a050"], [1, "#e05c5c"]],
            cmin=0, cmax=1,
            showscale=False,
            opacity=0.0,   # hide dots, show only the colorscale on the line
        ),
        hoverinfo="skip",
        name="Track",
    ))

    # ── Start marker ──────────────────────────────────────────────────────────
    fig.add_trace(go.Scattermapbox(
        lat=[lats[0]], lon=[lons[0]],
        mode="markers",
        marker=dict(size=14, color="#27c93f", symbol="circle"),
        hovertemplate="Start<extra></extra>",
        name="Start",
    ))

    # ── Cursor marker (moved by hover callback) ───────────────────────────────
    fig.add_trace(go.Scattermapbox(
        lat=[lats[0]], lon=[lons[0]],
        mode="markers",
        marker=dict(
            size=18,
            color="#ff3333",        # bright red
            opacity=1.0,
        ),
        hovertemplate="<b>Current Position</b><extra></extra>",
        name="Cursor",
    ))

    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=centre[0], lon=centre[1]),
            zoom=13,
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=400,
        showlegend=False,
        paper_bgcolor="#12122a",
        uirevision="map-static",   # keep user zoom/pan between cursor updates
    )
    return fig


def build_map(activity: Activity) -> str:
    """
    Legacy folium map (kept for reference).
    Returns HTML string.
    """
    coords = gps_track(activity)
    if len(coords) < 2:
        return ""

    lats = [c[0] for c in coords]
    lons = [c[1] for c in coords]
    centre = (sum(lats) / len(lats), sum(lons) / len(lons))

    m = folium.Map(location=centre, zoom_start=14,
                   tiles="CartoDB dark_matter", prefer_canvas=True)

    step = max(1, len(coords) // 800)
    pts  = list(zip(
        [s.lat  for s in activity.samples if s.lat  is not None][::step],
        [s.lon  for s in activity.samples if s.lon  is not None][::step],
        [s.pace for s in activity.samples if s.lat  is not None][::step],
    ))

    for i in range(len(pts) - 1):
        p1, p2 = pts[i], pts[i + 1]
        folium.PolyLine(
            [(p1[0], p1[1]), (p2[0], p2[1])],
            color=_pace_to_hex(p1[2]),
            weight=4, opacity=0.85,
            tooltip=f"{p1[2]:.1f} min/km" if p1[2] else "",
        ).add_to(m)

    folium.Marker(coords[0], tooltip="Start",
                  icon=folium.Icon(color="green", icon="play", prefix="fa")).add_to(m)
    folium.Marker(coords[-1], tooltip="Finish",
                  icon=folium.Icon(color="red", icon="flag", prefix="fa")).add_to(m)
    m.fit_bounds([[min(lats), min(lons)], [max(lats), max(lons)]])
    return m._repr_html_()


# ── Helpers ────────────────────────────────────────────────────────────────────

def _pace_norm(pace) -> float:
    """Normalise pace to 0..1 for colorscale (0=fast/green, 1=slow/red)."""
    if pace is None or pace <= 0 or pace > 30:
        return 0.5
    t = (pace - _PACE_FAST) / (_PACE_SLOW - _PACE_FAST)
    return max(0.0, min(1.0, t))


def _pace_to_hex(pace) -> str:
    if pace is None or pace <= 0 or pace > 30:
        return "#888888"
    t = (pace - _PACE_FAST) / (_PACE_SLOW - _PACE_FAST)
    t = max(0.0, min(1.0, t))
    hue = 0.33 * (1.0 - t)
    r, g, b = colorsys.hsv_to_rgb(hue, 0.85, 0.95)
    return "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))
