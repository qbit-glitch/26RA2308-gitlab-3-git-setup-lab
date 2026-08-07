# detector.py - threshold obstacle detector
THRESHOLD = 0.40


def is_obstacle(score):
    return score >= THRESHOLD
