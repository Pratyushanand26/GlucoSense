def format_health_data(raw_data):
    """
    Clean and standardize smartwatch data before inserting.
    Example transformation: flatten nested dicts, add timestamp, etc.
    """
    if not raw_data:
        return None

    # Example: ensure consistent schema
    formatted_data = {
        "heart_rate": raw_data.get("heart_rate"),
        "hrv": raw_data.get("hrv"),
        "sleep": raw_data.get("sleep"),
        "activity": raw_data.get("activity"),
        "spo2": raw_data.get("spo2"),
        "stress": raw_data.get("stress"),
        "skin_temp": raw_data.get("skin_temp"),
        "body_weight": raw_data.get("body_weight"),
        "timestamp": raw_data.get("timestamp"),
    }

    return formatted_data
