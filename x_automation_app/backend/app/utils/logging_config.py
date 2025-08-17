import logging
import sys
from copy import copy

import colorlog
import click

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
                            dim=bool(color_spec.get("dim", False)),         # Reduces the intensity of the text.
                            underline=bool(color_spec.get("underline", False)),
                            italic=bool(color_spec.get("italic", False)),    
                            blink=bool(color_spec.get("blink", False)),      # Makes the text blink.
                            reverse=bool(color_spec.get("reverse", False)),  # Inverts the foreground and background colors of the text.
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

    if not use_colors:
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s', datefmt=datefmt
        ))

    logger.addHandler(console_handler)
    return logger

def ctext(text: str, color: str = None, bg: str = None, **styles) -> str:
    """
    Shortcut for click.style:
    - text : the string to style
    - color : foreground color (alias of fg)
    - bg : background color
    - styles : bold=True, underline=True, italic=True, dim=True, blink=True, reverse=True

    Example:
        ctext("Hello", color="red", bold=True)
        ctext("Warning!", color="yellow", underline=True)
        ctext("OK", color="green", bg="black")
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

    logger.info("Default INFO message")
    logger.warning("Default WARNING message")

    # Styled text
    logger.info(ctext("This is bold red", color="red", bold=True))
    logger.info(ctext("This is underlined cyan", color="cyan", underline=True))

    # Mixing styled parts inside a sentence
    logger.info(f"Process {ctext('OK', color='green', bold=True)} completed")

