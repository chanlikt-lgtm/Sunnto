"""Classify an Activity into a GUI rendering category based on ActivityType + data signals."""

# Suunto ActivityType ID → GUI category
_TYPE_TO_CATEGORY = {
    0:  "endurance",   # Running
    1:  "endurance",   # Cycling
    2:  "endurance",   # Skiing
    3:  "endurance",   # Walking
    4:  "endurance",   # Hiking
    5:  "endurance",   # MTB
    6:  "endurance",   # Indoor Cycling
    7:  "endurance",   # Rowing
    8:  "endurance",   # Paddling
    9:  "endurance",   # Nordic Ski
    10: "endurance",   # Ski Touring
    11: "swimming",    # Open Water Swim
    12: "gym",         # Indoor Training (promoted to endurance if GPS + real distance)
    13: "endurance",   # Trail Running
    14: "endurance",   # Triathlon
    15: "swimming",    # Pool Swimming
    16: "endurance",   # Treadmill
    17: "gym",         # Gym / Weight Training
    18: "sleep",       # Sleep
    19: "gym",         # Yoga
    20: "gym",         # Fitness Class
    21: "gym",         # Bouldering
    22: "gym",         # Crossfit
    23: "sleep",       # Sleep
    24: "sleep",       # Meditation
}


def classify_sport(activity) -> str:
    """
    Return one of: 'endurance', 'swimming', 'gym', 'sleep'.

    Rules:
    - Use ActivityType as primary signal.
    - Indoor Training / Gym recorded with GPS and > 500 m → treat as endurance
      (user selected wrong mode on watch).
    """
    base = _TYPE_TO_CATEGORY.get(activity.activity_type_id, "endurance")

    # Promote gym→endurance when meaningful GPS distance was recorded
    if base == "gym" and activity.distance_m > 500 and activity.has_gps():
        return "endurance"

    return base
