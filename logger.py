from datetime import datetime
from pytz import timezone
import logging

def timetz(*args):
    return datetime.now(timezone('Asia/Tokyo')).timetuple()

logging.Formatter.converter = timetz

logging.basicConfig(
    format='[%(asctime)s][%(name)s][%(levelname)s]: %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger()