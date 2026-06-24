def detect_category(text):

    text = text.upper()

    if "NEET" in text:
        return "NEET"

    if "JEE" in text:
        return "JEE"

    if "CUET" in text:
        return "CUET"

    return "GENERAL"
def get_categories():

    return [
        "NEET",
        "JEE",
        "CUET",
        "GENERAL"
    ]