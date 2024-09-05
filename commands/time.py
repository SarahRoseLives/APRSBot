from datetime import datetime

def handle_command():
    """Return a response including the current Zulu time."""
    # Get the current UTC time
    utc_now = datetime.utcnow()
    # Format the time in a readable format
    zulu_time = utc_now.strftime('%Y-%m-%dT%H:%M:%SZ')
    # Return the response with Zulu time
    return f"Current Zulu Time: {zulu_time}"
