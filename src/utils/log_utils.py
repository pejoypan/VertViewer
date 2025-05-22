import re

from qfluentwidgets import InfoBar, InfoBarPosition

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

def show_info_bar(level, content, title=None, duration=5000, parent=None):
    '''
    level: success, info, warning, error
    duration: -1 for permanent
    '''
    if level in ['success', 'info']:
        dura = duration
    elif level in ['warning', 'error']:
        dura = -1
    else:
        level = 'info'
        dura = duration

    getattr(InfoBar, level)(
        title=title if title else level,
        content=content,
        duration=dura,
        position=InfoBarPosition.TOP,
        parent=parent
    )
