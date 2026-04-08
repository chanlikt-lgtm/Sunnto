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
    "Running":        "man-running",
    "Trail Running":  "person-hiking",
    "Walking":        "person-walking",
    "Hiking":         "person-hiking",
    "Cycling":        "person-biking",
    "MTB":            "person-biking",
    "Indoor Cycling": "person-biking",
    "Open Water Swim":"person-swimming",
    "Pool Swimming":  "person-swimming",
    "Gym":            "dumbbell",
    "Sleep":          "moon",
}

# Unit conversions
RAD_TO_DEG = 57.29577951308232    # 180/pi
HZ_TO_BPM  = 60.0                 # multiply HR samples
HZ_TO_RPM  = 60.0                 # multiply cadence samples
K_TO_C     = -273.15              # add to Kelvin

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
