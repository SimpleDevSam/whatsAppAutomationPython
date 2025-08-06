import re

def splitTextForWhatsApp(message: str) -> list[str]:
    parts = re.split(r'(?<=\.)\s*|(?<=!)\s*', message)
    return [part.strip() for part in parts if part.strip()]