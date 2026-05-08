def analyze_face(width, height):
    if width > 150:
        return "Confident Personality"
    elif width > 100:
        return "Balanced Personality"
    else:
        return "Calm Personality"