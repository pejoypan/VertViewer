import re

log_pattern = re.compile(r"\[(.*?)\] \[(.*?)\] \[(.*?)\] (.*)")

LEVEL_COLOR = {
    "trace": "#aaaaaa",
    "debug": "#9999cc",
    "info": "#008800",
    "warning": "#ffaa00",
    "error": "#ff4444",
    "critical": "#cc0000",
}

LEVEL_ICON = {
    "trace": "👀",
    "debug": "🐞",
    "info": "ℹ️",
    "warning": "⚠️",
    "error": "🚫",
    "critical": "🔥",
}

def parse_log_line(line: str):
    match = log_pattern.match(line)
    if not match:
        return None
    return match.groups()  # time, level, source, detail

def get_color(level: str):
    return LEVEL_COLOR.get(level.lower(), "#ffffff")

def get_emoji(level: str):
    return LEVEL_ICON.get(level.lower(), "⁉️")