HIGH_RISK_KEYWORDS = [
    "fraud",
    "stolen",
    "identity theft",
    "hack",
    "hacked",
    "exploit",
    "vulnerability",
    "delete all files",
    "lawsuit",
    "urgent cash",
    "bypass",
    "internal rules",
    "reveal logic"
]

def assess_risk(text):
    text = text.lower()

    for keyword in HIGH_RISK_KEYWORDS:
        if keyword in text:
            return "high"

    return "low"