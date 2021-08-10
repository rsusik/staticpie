from rich.console import Console
console = Console()

from rich.traceback import install
install(show_locals=True)

import logging
from rich.logging import RichHandler

logging.basicConfig(
    #level="NOTSET",
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)

log = logging.getLogger("rich")