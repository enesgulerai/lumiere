import logging
import sys
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """
    Custom formatter to output logs in JSON format for external monitoring tools.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "func_name": record.funcName,
            "line_no": record.lineno,
        }
        
        # Include exception traceback if an error occurs
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_record)

def get_logger(name: str) -> logging.Logger:
    """
    Retrieves a configured logger instance.
    """
    logger = logging.getLogger(name)
    
    # Prevent adding multiple handlers if the logger is requested multiple times
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(JSONFormatter())
        
        logger.addHandler(console_handler)
        # Prevent logs from propagating to the root logger to avoid duplicates
        logger.propagate = False
        
    return logger