"""Keybinding definitions and utilities."""

# Vim-style navigation keys
VIM_NAVIGATION = {
    "down": ["j", "down"],
    "up": ["k", "up"],
    "enter": ["l", "enter"],
    "back": ["h", "backspace"],
    "top": ["g"],  # gg for go to top
    "bottom": ["G"],
    "page_down": ["ctrl+d"],
    "page_up": ["ctrl+u"],
}

# File operation keys
FILE_OPERATIONS = {
    "delete": ["d"],
    "copy": ["y"],  # yank
    "paste": ["p"],
    "upload": ["u"],
    "download": ["D"],  # shift+d
    "refresh": ["r"],
    "select": ["space"],
}

# Global keys
GLOBAL_KEYS = {
    "search": ["/"],
    "cancel": ["escape"],
    "account": ["a"],
    "help": ["?"],
    "quit": ["q"],
}
