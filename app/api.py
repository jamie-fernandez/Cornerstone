import logging
import platform

import psutil
from sqlalchemy import text

from app.config import CONFIG
from app.database import get_db_path, get_session
from app.decorators import bridge_method

logger = logging.getLogger(__name__)


class API:
    """Python API class that can be called from JavaScript"""

    def __init__(self):
        self._window = None

    def set_window(self, window):
        self._window = window

    def quit(self):
        # Use hide() if you plan to reuse the window; use destroy() when you’re done with it entirely.
        # TODO: add a check to save data before calling destroy()
        self._window.hide()

    @bridge_method
    def get_app_configuration(self):
        return CONFIG

    @bridge_method
    def get_user_data(self):
        """Example API method - returns user data"""
        return {
            "users": [
                {"id": 1, "name": "John Doe", "email": "john@example.com"},
                {"id": 2, "name": "Jane Smith", "email": "jane@example.com"},
            ]
        }

    @bridge_method
    def get_system_info(self):
        """Get basic system information"""
        return {
            "platform": platform.system(),
            "version": platform.version(),
            "machine": platform.machine(),
            "python_version": platform.python_version(),
        }

    @bridge_method
    def get_database_path(self):
        """Get current database path"""
        return {"path": get_db_path()}

    @bridge_method
    def test_database_connection(self):
        """Test database connection"""
        with get_session() as db:
            db.execute(text("SELECT 1"))
        return {"message": "Database connection OK"}

    @bridge_method
    def get_system_stats(self):
        """Get detailed system statistics using psutil"""
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        return {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "percent_used": memory.percent,
            },
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "percent_used": disk.percent,
            },
        }
