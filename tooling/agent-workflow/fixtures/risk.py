import math


def probability_power(q, k):
    if isinstance(q, bool) or not isinstance(q, (int, float)) or not math.isfinite(q) or not 0 <= q <= 1:
        raise ValueError("q must be finite and between zero and one")
    if isinstance(k, bool) or not isinstance(k, int) or k < 1:
        raise ValueError("k must be a positive integer")
    return q ** k


def loss_streak_probability(q, k):
    raise NotImplementedError("Reuse the existing helper")
