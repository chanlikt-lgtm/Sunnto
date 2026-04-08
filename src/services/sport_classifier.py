"""Classify an Activity into a GUI rendering category based on ActivityType + data signals."""

from ..models.activity import SportCategory

# Suunto ActivityType ID → SportCategory
_TYPE_TO_CATEGORY = {
    0:  SportCategory.ENDURANCE,   # Running
    1:  SportCategory.ENDURANCE,   # Cycling
    2:  SportCategory.ENDURANCE,   # Skiing
    3:  SportCategory.ENDURANCE,   # Walking
    4:  SportCategory.ENDURANCE,   # Hiking
    5:  SportCategory.ENDURANCE,   # MTB
    6:  SportCategory.ENDURANCE,   # Indoor Cycling
    7:  SportCategory.ENDURANCE,   # Rowing
    8:  SportCategory.ENDURANCE,   # Paddling
    9:  SportCategory.ENDURANCE,   # Nordic Ski
    10: SportCategory.ENDURANCE,   # Ski Touring
    11: SportCategory.SWIMMING,    # Open Water Swim
    12: SportCategory.GYM,         # Indoor Training (promoted if GPS + real distance)
    13: SportCategory.ENDURANCE,   # Trail Running
    14: SportCategory.ENDURANCE,   # Triathlon
    15: SportCategory.SWIMMING,    # Pool Swimming
    16: SportCategory.ENDURANCE,   # Treadmill
    17: SportCategory.GYM,         # Gym / Weight Training
    18: SportCategory.SLEEP,       # Sleep
    19: SportCategory.GYM,         # Yoga
    20: SportCategory.GYM,         # Fitness Class
    21: SportCategory.GYM,         # Bouldering
    22: SportCategory.GYM,         # Crossfit
    23: SportCategory.SLEEP,       # Sleep
    24: SportCategory.SLEEP,       # Meditation
}


def classify_sport(activity) -> SportCategory:
    """
    Return a SportCategory for the activity.

    Rules:
    - Use ActivityType as primary signal.
    - Indoor Training / Gym recorded with GPS and > 500 m → treat as endurance
      (user selected wrong mode on watch).
    """
    base = _TYPE_TO_CATEGORY.get(activity.activity_type_id, SportCategory.ENDURANCE)

    # Promote gym→endurance when meaningful GPS distance was recorded
    if base == SportCategory.GYM and activity.distance_m > 500 and activity.has_gps():
        return SportCategory.ENDURANCE

    return base
