import logging
import sys


logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [ReflexSystem] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)