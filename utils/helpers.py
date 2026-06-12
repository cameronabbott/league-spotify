import random
import math

def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))

    if mag_a == 0 or mag_b == 0:
        return 0

    return dot / (mag_a * mag_b)

def jitter(x, amount=0.05):
    return x + random.uniform(-amount, amount)

def normalise(x, min_val, max_val):
    score = (x - min_val) / (max_val - min_val)
    if score < 0:
        return 0
    elif score > 1:
        return 1
    return score

def clamp(x, min_val, max_val):
    if x < min_val:
        return min_val
    elif x > max_val:
        return max_val
    return x