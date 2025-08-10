import json
from datetime import datetime, timezone


class Logger:
    def info(self, message: str) -> None:
        self._log("INFO", message)
    
    def error(self, message: str) -> None:
        self._log("ERROR", message)
    
    def _log(self, level: str, message: str) -> None:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "message": message
        }
        print(json.dumps(log_entry))