import random

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