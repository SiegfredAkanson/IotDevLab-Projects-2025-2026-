"""Utility helpers shared across modules."""


def clamp(value, minimum, maximum):
    if value < minimum:
        return minimum
    if value > maximum:
        return maximum
    return value


def lerp(prev_value, new_value, alpha):
    """Simple low-pass filter interpolation."""
    return prev_value + alpha * (new_value - prev_value)


def normalize(value, low, high):
    """Map value to 0..1 with guard for invalid ranges."""
    if high <= low:
        return 0.0
    ratio = (value - low) / float(high - low)
    return clamp(ratio, 0.0, 1.0)
