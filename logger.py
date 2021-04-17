import logging
from datetime import date
import sys

# Logging
logging.captureWarnings(True)
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(f"logs/{date.today()}.log")
console_handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("%(asctime)s : %(levelname)s : %(name)s : %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)
log.addHandler(file_handler)
log.addHandler(console_handler)