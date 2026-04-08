"""Generate folium map HTML — GPS track colored by pace."""

import colorsys
import folium
from ..models.activity import Activity


# Pace range used for the colour scale (min/km)
_PACE_SLOW = 8.0    # red   — walking pace
_PACE_FAST = 4.5    # green — brisk run


def build_map(activity: Activity) -> str:
    """
    Build a folium map.  The GPS route is drawn as short coloured
    segments where colour encodes pace (green=fast, red=slow).
    Returns HTML string for embedding in an iframe.
    """
    # Collect GPS samples that also have a pace value
    pts = [
        (s.lat, s.lon, s.pace, s.speed)
        for s in activity.samples
        if s.lat is not None and s.lon is not None
    ]
    if len(pts) < 2:
        return ""

    # Downsample for performance — keep every Nth point
    step = max(1, len(pts) // 800)
    pts  = pts[::step]

    lats = [p[0] for p in pts]
    lons = [p[1] for p in pts]
    centre = (sum(lats) / len(lats), sum(lons) / len(lons))

    m = folium.Map(location=centre, zoom_start=14,
                   tiles="CartoDB dark_matter", prefer_canvas=True)

    # ── Colored route segments ───────────────────────────────────────────────
    for i in range(len(pts) - 1):
        p1, p2 = pts[i], pts[i + 1]
        pace = p1[2]   # min/km (may be None)
        color = _pace_to_hex(pace)
        folium.PolyLine(
            [(p1[0], p1[1]), (p2[0], p2[1])],
            color=color,
            weight=4,
            opacity=0.85,
            tooltip=f"{pace:.1f} min/km" if pace else "",
        ).add_to(m)

    # ── Start / Finish markers ───────────────────────────────────────────────
    folium.Marker(
        (pts[0][0],  pts[0][1]),
        tooltip="Start",
        icon=folium.Icon(color="green", icon="play", prefix="fa"),
    ).add_to(m)
    folium.Marker(
        (pts[-1][0], pts[-1][1]),
        tooltip="Finish",
        icon=folium.Icon(color="red", icon="flag", prefix="fa"),
    ).add_to(m)

    # ── Legend ───────────────────────────────────────────────────────────────
    _add_legend(m)

    m.fit_bounds([[min(lats), min(lons)], [max(lats), max(lons)]])
    return m._repr_html_()


# ── Helpers ────────────────────────────────────────────────────────────────────

def _pace_to_hex(pace_min_km) -> str:
    """Map pace (min/km) to a hex colour: green (fast) -> red (slow)."""
    if pace_min_km is None or pace_min_km <= 0 or pace_min_km > 30:
        return "#888888"
    t = (pace_min_km - _PACE_FAST) / (_PACE_SLOW - _PACE_FAST)
    t = max(0.0, min(1.0, t))
    # hue: 0.33 (green) -> 0.0 (red)
    hue = 0.33 * (1.0 - t)
    r, g, b = colorsys.hsv_to_rgb(hue, 0.85, 0.95)
    return "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))


def _add_legend(m: folium.Map):
    """Inject an HTML legend into the folium map."""
    legend_html = """
    <div style="
        position: fixed; bottom: 20px; right: 20px; z-index: 1000;
        background: rgba(20,20,40,0.88); padding: 10px 14px;
        border-radius: 8px; color: #eee; font-size: 12px;
        font-family: sans-serif; border: 1px solid #333;
    ">
      <b style="font-size:13px">Pace</b><br>
      <span style="color:#27c93f">&#9632;</span> Fast (&lt; {fast} min/km)<br>
      <span style="color:#f0a050">&#9632;</span> Medium<br>
      <span style="color:#e05c5c">&#9632;</span> Slow (&gt; {slow} min/km)
    </div>
    """.format(fast=_PACE_FAST, slow=_PACE_SLOW)

    m.get_root().html.add_child(folium.Element(legend_html))
