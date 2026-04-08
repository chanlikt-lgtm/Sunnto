"""Application-wide constants."""

# Suunto activity type ID -> display name
ACTIVITY_TYPES = {
    0:  "Running",
    1:  "Cycling",
    2:  "Skiing",
    3:  "Walking",
    4:  "Hiking",
    5:  "MTB",
    6:  "Indoor Cycling",
    7:  "Rowing",
    8:  "Paddling",
    9:  "Nordic Ski",
    10: "Ski Touring",
    11: "Open Water Swim",
    12: "Indoor Training",
    13: "Trail Running",
    14: "Triathlon",
    15: "Pool Swimming",
    16: "Treadmill",
    17: "Gym",
    18: "Sleep",
    19: "Yoga",
    20: "Fitness Class",
    21: "Bouldering",
    22: "Crossfit",
    23: "Sleep",
    24: "Meditation",
}

SPORT_ICONS = {
    "Running":          "man-running",
    "Jogging":          "person-running",
    "Trail Running":    "person-hiking",
    "Walking":          "person-walking",
    "Hiking":           "person-hiking",
    "Cycling":          "person-biking",
    "MTB":              "person-biking",
    "Indoor Cycling":   "person-biking",
    "Rowing":           "water",
    "Paddling":         "water",
    "Nordic Ski":       "person-skiing-nordic",
    "Ski Touring":      "person-skiing",
    "Open Water Swim":  "person-swimming",
    "Pool Swimming":    "person-swimming",
    "Indoor Training":  "dumbbell",
    "Treadmill":        "man-running",
    "Triathlon":        "person-biking",
    "Gym":              "dumbbell",
    "Yoga":             "spa",
    "Fitness Class":    "heart-pulse",
    "Bouldering":       "mountain",
    "Crossfit":         "dumbbell",
    "Sleep":            "moon",
    "Meditation":       "brain",
}

# Colour per GUI category
CATEGORY_COLORS = {
    "endurance": "#3fb950",   # green
    "gym":       "#f0a050",   # amber
    "swimming":  "#58a6ff",   # blue
    "sleep":     "#c084fc",   # purple
}

# Domain thresholds (used for chart colour scales and HR zone rendering)
PACE_SLOW_MIN_KM    = 8.0    # min/km — red end of pace colour scale
PACE_FAST_MIN_KM    = 4.5    # min/km — green end of pace colour scale
HR_MAX_DEFAULT      = 220    # bpm  — fallback when no HR data to set zone ceiling
MIN_MOVING_SPEED_MPS = 0.05  # m/s  — below this the activity is considered paused

# Date range presets
DATE_RANGES = [
    ("7d",  "Last 7 days"),
    ("14d", "Last 14 days"),
    ("30d", "Last 30 days"),
    ("90d", "Last 90 days"),
    ("all", "All time"),
]

# Chart colours
CHART_COLORS = {
    "hr":   "#e05c5c",
    "pace": "#3fb950",
    "alt":  "#58a6ff",
    "cad":  "#c084fc",
    "temp": "#f0a050",
    "spd":  "#50d0c0",
}
