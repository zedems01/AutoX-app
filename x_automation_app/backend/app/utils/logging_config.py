import logging
import sys
from copy import copy
import re
import os
from pathlib import Path
from datetime import datetime

import colorlog
import click

class NoHttpRequestFilter(logging.Filter):
    """
    A logging filter to exclude logs containing 'http' or 'AFC' (case-insensitive).
    """
    def filter(self, record: logging.LogRecord) -> bool:
        # Exclude logs containing 'http' or 'AFC' (case-insensitive)
        patterns = [ r'http', r'afc']
        message = record.getMessage().lower()
        return not any(re.search(pattern, message) for pattern in patterns)

def setup_logging(log_level='INFO', use_colors=None):
    """
    Set up colored console logging.
    - Uses colorlog for level-based colors.
    - Custom message styling via `extra`:
        extra={'color': 'red'}                              # applies a color to the message
        extra={'color': {'fg': 'yellow', 'bold': True}}     # detailed style specification
        extra={'color_message': click.style("...")}         # pre-styled message (takes priority)
    """
    if use_colors is None:
        use_colors = sys.stdout.isatty()

    # Root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    logger.handlers.clear()

    # Custom formatter to handle styled messages
    class ClickMessageFormatter(colorlog.ColoredFormatter):
        def format(self, record: logging.LogRecord) -> str:
            r = copy(record)
            # Check for pre-styled message in `color_message`
            cm = getattr(r, "color_message", None)
            if isinstance(cm, str) and cm:
                r.msg = cm
            else:
                # Apply dynamic styling via `extra['color']`
                color_spec = getattr(r, "color", None)
                if color_spec and use_colors:
                    text = r.getMessage()
                    if isinstance(color_spec, str):
                        # Simple color specification
                        r.msg = click.style(text, fg=color_spec)
                    elif isinstance(color_spec, dict):
                        # Detailed style specification
                        r.msg = click.style(
                            text,
                            fg=color_spec.get("fg"),
                            bg=color_spec.get("bg"),
                            bold=bool(color_spec.get("bold", False)),
                            dim=bool(color_spec.get("dim", False)),
                            underline=bool(color_spec.get("underline", False)),
                            italic=bool(color_spec.get("italic", False)),
                            blink=bool(color_spec.get("blink", False)),
                            reverse=bool(color_spec.get("reverse", False)),
                        )
            return super().format(r)

    fmt = '\n%(log_color)s%(asctime)s [%(levelname)s] %(message)s%(reset)s'
    datefmt = '%Y-%m-%d %H:%M:%S'

    console_handler = colorlog.StreamHandler()
    console_handler.setFormatter(
        ClickMessageFormatter(
            fmt=fmt,
            datefmt=datefmt,
            log_colors={
                'DEBUG':    'cyan',
                'INFO':     'blue',
                'WARNING':  'yellow',
                'ERROR':    'red',
                'CRITICAL': 'bold_red',
            },
            reset=True,
        )
    )

    # Add the HTTP filter to the console handler
    console_handler.addFilter(NoHttpRequestFilter())

    if not use_colors:
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s', datefmt=datefmt
        ))

    logger.addHandler(console_handler)
    return logger

def add_file_handler(thread_id: str):
    """Adds a file handler to the root logger for a specific workflow run."""
    logger = logging.getLogger()

    logs_dir = Path(__file__).parent.parent / 'logs'
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file_path = logs_dir / f"{timestamp}_{thread_id}.log"

    file_handler = logging.FileHandler(log_file_path, mode='a', encoding='utf-8')
    file_handler.setLevel(logger.level)
    file_handler.name = f"file_handler_{thread_id}"

    class PlainFormatter(logging.Formatter):
        def format(self, record: logging.LogRecord) -> str:
            formatted_message = super().format(record)
            return click.unstyle(formatted_message)

    fmt = '%(asctime)s [%(levelname)s] %(message)s'
    datefmt = '%Y-%m-%d %H:%M:%S'
    
    formatter = PlainFormatter(fmt, datefmt=datefmt)
    file_handler.setFormatter(formatter)
    
    file_handler.addFilter(NoHttpRequestFilter())

    logger.addHandler(file_handler)

def remove_file_handler(thread_id: str):
    """Removes the file handler associated with a specific workflow run."""
    logger = logging.getLogger()
    handler_name = f"file_handler_{thread_id}"
    
    handler_to_remove = None
    for handler in logger.handlers:
        if handler.name == handler_name:
            handler_to_remove = handler
            break
            
    if handler_to_remove:
        handler_to_remove.close()
        logger.removeHandler(handler_to_remove)

def ctext(text: str, color: str = None, bg: str = None, **styles) -> str:
    """
    Shortcut for click.style:
    - text : the string to style
    - color : foreground color (alias of fg)
    - bg : background color
    - styles : bold=True, underline=True, italic=True, dim=True, blink=True, reverse=True
    """
    return click.style(
        text,
        fg=color,
        bg=bg,
        bold=styles.get("bold", False),
        dim=styles.get("dim", False),
        underline=styles.get("underline", False),
        italic=styles.get("italic", False),
        blink=styles.get("blink", False),
        reverse=styles.get("reverse", False),
    )

if __name__ == "__main__":
    logger = setup_logging()

    # Test logs
    logger.info("Default INFO message")
    logger.warning("Default WARNING message")
    logger.info("HTTP Request: POST https://api.anthropic.com/v1/messages \"HTTP/1.1 200 OK\"")  # Should be filtered
    logger.info("HTTP Request: POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite-preview-06-17:generateContent \"HTTP/1.1 200 OK\"")  # Should be filtered
    logger.info(ctext("This is bold red", color="red", bold=True))
    logger.info(f"Process {ctext('OK', color='green', bold=True)} completed")