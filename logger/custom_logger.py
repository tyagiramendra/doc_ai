import logging
import os
from datetime import datetime
import structlog


class CustomLogger:
    
    def __init__(self, log_dir="logs"):
        self.LOG_FILE = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_file_path = os.path.join(self.log_dir, self.LOG_FILE)
        self._setup_logger()
    
    def _setup_logger(self):
        logging.basicConfig(
            filename=self.log_file_path,
            format="[ %(asctime)s ] %(lineno)d %(name)s - %(levelname)s - %(message)s",
            level=logging.INFO
        )

    def get_custom_logger(self,name:__file__):
        file_handler = logging.FileHandler(self.log_file_path)
        logging.getLogger().addHandler(file_handler)

        #Stream Handler
        stream_handler = logging.StreamHandler()
        logging.getLogger().addHandler(stream_handler)

        structlog.configure(
            processors=[
                structlog.processors.add_log_level,
                structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=True),
                structlog.processors.EventRenamer(to="event"),
                structlog.processors.JSONRenderer()
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )
        logger=structlog.get_logger(name)
        return logger
    