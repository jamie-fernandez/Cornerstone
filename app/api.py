import psutil

from app.config import CONFIG
from app.database import SessionLocal, get_db_path, logger
# from app.models import *


class Api:
    """Python API class that can be called from JavaScript"""

    def __init__(self):
        self._window = None

    def set_window(self, window):
        self._window = window

    def quit(self):
        # Use hide() if you plan to reuse the window; use destroy() when you’re done with it entirely.
        # TODO: add a check to save data before calling destroy()
        self._window.hide()

    def get_app_configuration(self):
        return CONFIG

    def get_user_data(self):
        """Example API method - returns user data"""
        return {
            "users": [
                {"id": 1, "name": "John Doe", "email": "john@example.com"},
                {"id": 2, "name": "Jane Smith", "email": "jane@example.com"},
            ]
        }

    def get_system_info(self):
        """Get basic system information"""
        import platform

        return {
            "platform": platform.system(),
            "version": platform.version(),
            "machine": platform.machine(),
            "python_version": platform.python_version(),
        }

    def get_database_path(self):
        """Get current database path"""
        return {"path": get_db_path()}

    def test_database_connection(self):
        """Test database connection"""
        from sqlalchemy import text

        try:
            with SessionLocal() as db:
                db.execute(text("SELECT 1"))
            return {"status": "success", "message": "Database connection OK"}
        except Exception as e:
            logger.error(f"Database test failed: {e}")
            return {"status": "error", "message": str(e)}

    # New method for system monitoring using psutil:
    def get_system_stats(self):
        """Get detailed system statistics using psutil"""
        try:
            return {
                "cpu_percent": psutil.cpu_percent(interval=0.1),
                "memory": {
                    "total": psutil.virtual_memory().total,
                    "available": psutil.virtual_memory().available,
                    "percent_used": psutil.virtual_memory().percent,
                },
                "disk": {
                    "total": psutil.disk_usage("/").total,
                    "used": psutil.disk_usage("/").used,
                    "percent_used": psutil.disk_usage("/").percent,
                },
            }
        except Exception as e:
            logger.error(f"Failed to get system stats: {e}")
            return {"status": "error", "message": str(e)}
