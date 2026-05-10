# Unified stylesheet constants for the application

# Color palette
PRIMARY = "#1e40af"
PRIMARY_LIGHT = "#3b82f6"
PRIMARY_HOVER = "#60a5fa"
SUCCESS = "#10b981"
SUCCESS_HOVER = "#34d399"
SUCCESS_DARK = "#059669"
WARNING = "#f59e0b"
WARNING_HOVER = "#fbbf24"
DANGER = "#ef4444"
DANGER_HOVER = "#f87171"
DANGER_DARK = "#dc2626"
PURPLE = "#8b5cf6"

TEXT_PRIMARY = "#1e293b"
TEXT_SECONDARY = "#64748b"
TEXT_MUTED = "#94a3b8"

BG_MAIN = "#f8fafc"
BG_CARD = "#ffffff"
BG_SIDEBAR = "#f1f5f9"
BG_INPUT = "#f8fafc"
BORDER = "#e2e8f0"
BORDER_DASHED = "#cbd5e1"

FONT_FAMILY = "'Microsoft YaHei', 'Segoe UI', sans-serif"

# Shared drop shadow effect (applied in code via QGraphicsDropShadowEffect)
# CSS box-shadow is NOT supported by Qt stylesheets; use the helper below.


def apply_shadow(widget, blur=20, x_offset=0, y_offset=2, color_rgb=(0, 0, 0, 40)):
    """Apply a real drop shadow to a widget using QGraphicsDropShadowEffect."""
    from PyQt5.QtWidgets import QGraphicsDropShadowEffect
    from PyQt5.QtGui import QColor
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(blur)
    shadow.setXOffset(x_offset)
    shadow.setYOffset(y_offset)
    shadow.setColor(QColor(*color_rgb))
    widget.setGraphicsEffect(shadow)


# Button styles
BTN_PRIMARY = f"""
    QPushButton {{
        background-color: {PRIMARY_LIGHT};
        color: white;
        font-weight: bold;
        border-radius: 6px;
        border: none;
        font-size: 12px;
        font-family: {FONT_FAMILY};
        padding: 6px 14px;
    }}
    QPushButton:hover {{
        background-color: {PRIMARY_HOVER};
    }}
    QPushButton:disabled {{
        background-color: {TEXT_MUTED};
    }}
"""

BTN_SUCCESS = f"""
    QPushButton {{
        background-color: {SUCCESS};
        color: white;
        font-weight: bold;
        border-radius: 6px;
        border: none;
        font-size: 12px;
        font-family: {FONT_FAMILY};
        padding: 6px 14px;
    }}
    QPushButton:hover {{
        background-color: {SUCCESS_HOVER};
    }}
    QPushButton:disabled {{
        background-color: {TEXT_MUTED};
    }}
"""

BTN_DANGER = f"""
    QPushButton {{
        background-color: {DANGER};
        color: white;
        font-weight: bold;
        border-radius: 6px;
        border: none;
        font-size: 12px;
        font-family: {FONT_FAMILY};
        padding: 6px 14px;
    }}
    QPushButton:hover {{
        background-color: {DANGER_HOVER};
    }}
    QPushButton:disabled {{
        background-color: {TEXT_MUTED};
    }}
"""

BTN_SECONDARY = f"""
    QPushButton {{
        background-color: {BG_SIDEBAR};
        color: {TEXT_SECONDARY};
        font-weight: bold;
        border-radius: 6px;
        border: 1px solid {BORDER};
        font-size: 12px;
        font-family: {FONT_FAMILY};
        padding: 6px 14px;
    }}
    QPushButton:hover {{
        background-color: {BORDER};
        color: {TEXT_PRIMARY};
    }}
    QPushButton:disabled {{
        background-color: {BG_MAIN};
        color: {BORDER_DASHED};
    }}
"""

# Frame / card styles (no box-shadow or padding; apply shadow via code)
CARD_FRAME = f"""
    QFrame {{
        background-color: {BG_CARD};
        border-radius: 10px;
        border: 1px solid {BORDER};
    }}
"""

SIDEBAR_FRAME = f"""
    QFrame {{
        background-color: {BG_SIDEBAR};
        border-radius: 10px;
        border: 1px solid {BORDER};
    }}
"""

TITLE_BAR = f"""
    QFrame {{
        background-color: {PRIMARY};
        border-radius: 0px;
    }}
"""

# Text edit / input styles
TEXT_EDIT = f"""
    QTextEdit {{
        background-color: {BG_CARD};
        border-radius: 6px;
        border: 1px solid {BORDER};
        padding: 8px;
        font-family: {FONT_FAMILY};
        font-size: 12px;
        color: {TEXT_PRIMARY};
    }}
"""

# List widget styles
LIST_WIDGET = f"""
    QListWidget {{
        background-color: {BG_CARD};
        border-radius: 6px;
        border: 1px solid {BORDER};
        padding: 4px;
        font-family: {FONT_FAMILY};
        font-size: 12px;
        color: {TEXT_PRIMARY};
        outline: none;
    }}
    QListWidget::item {{
        padding: 6px 8px;
        border-radius: 4px;
    }}
    QListWidget::item:selected {{
        background-color: {PRIMARY_LIGHT};
        color: white;
    }}
    QListWidget::item:hover {{
        background-color: {BG_INPUT};
    }}
"""

# Scroll area styles
SCROLL_AREA = f"""
    QScrollArea {{
        background-color: {BG_CARD};
        border-radius: 6px;
        border: 1px solid {BORDER};
    }}
"""

# Label styles
LABEL_TITLE = f"""
    QLabel {{
        color: {TEXT_PRIMARY};
        font-family: {FONT_FAMILY};
        font-size: 13px;
        font-weight: bold;
    }}
"""

LABEL_MUTED = f"""
    QLabel {{
        color: {TEXT_MUTED};
        font-family: {FONT_FAMILY};
        font-size: 12px;
    }}
"""

# Slider style
SLIDER = f"""
    QSlider::groove:horizontal {{
        height: 6px;
        background: {BORDER};
        border-radius: 3px;
    }}
    QSlider::sub-page:horizontal {{
        background: {PRIMARY_LIGHT};
        border-radius: 3px;
    }}
    QSlider::handle:horizontal {{
        width: 14px;
        background: {PRIMARY_LIGHT};
        border-radius: 7px;
        margin: -4px 0;
    }}
    QSlider::handle:horizontal:hover {{
        background: {PRIMARY_HOVER};
    }}
"""
