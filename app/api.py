import base64
import psutil

from app.config import CONFIG
from app.database import SessionLocal, get_db_path, logger
from app.models import CharacterTemplate, Character, Tag

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
            'users': [
                {'id': 1, 'name': 'John Doe', 'email': 'john@example.com'},
                {'id': 2, 'name': 'Jane Smith', 'email': 'jane@example.com'}
            ]
        }

    def get_system_info(self):
        """Get basic system information"""
        import platform
        return {
            'platform': platform.system(),
            'version': platform.version(),
            'machine': platform.machine(),
            'python_version': platform.python_version()
        }

    def get_database_path(self):
        """Get current database path"""
        return {'path': get_db_path()}

    def test_database_connection(self):
        """Test database connection"""
        from sqlalchemy import text

        try:
            with SessionLocal() as db:
                db.execute(text("SELECT 1"))
            return {'status': 'success', 'message': 'Database connection OK'}
        except Exception as e:
            logger.error(f"Database test failed: {e}")
            return {'status': 'error', 'message': str(e)}

    # New method for system monitoring using psutil:
    def get_system_stats(self):
        """Get detailed system statistics using psutil"""
        try:
            return {
                'cpu_percent': psutil.cpu_percent(interval=0.1),
                'memory': {
                    'total': psutil.virtual_memory().total,
                    'available': psutil.virtual_memory().available,
                    'percent_used': psutil.virtual_memory().percent
                },
                'disk': {
                    'total': psutil.disk_usage('/').total,
                    'used': psutil.disk_usage('/').used,
                    'percent_used': psutil.disk_usage('/').percent
                }
            }
        except Exception as e:
            logger.error(f"Failed to get system stats: {e}")
            return {'status': 'error', 'message': str(e)}

    def create_character_template(self, name, image_data=None, image_mime=None, tag_names=None):
        """Create a new character template with optional image and tags"""
        try:
            with SessionLocal() as db:
                # Handle image data (base64 encoded)
                image_bytes = None
                if image_data and image_data.startswith("data:"):
                    # Extract base64 part from data URL
                    image_bytes = base64.b64decode(image_data.split(",")[1])

                # Create template
                template = CharacterTemplate(
                    name=name,
                    image_data=image_bytes,
                    image_mime=image_mime
                )
                db.add(template)
                db.flush()  # Get ID for relationships

                # Create and associate tags
                if tag_names:
                    for tag_name in tag_names:
                        tag = db.query(Tag).filter(Tag.name == tag_name.strip()).first()
                        if not tag:
                            tag = Tag(name=tag_name.strip())
                            db.add(tag)
                            db.flush()
                        template.tags.append(tag)

                db.commit()
                return {
                    "status": "success",
                    "template": {
                        "id": template.id,
                        "name": template.name,
                        "tag_count": len(template.tags)
                    }
                }
        except Exception as e:
            logger.error(f"Failed to create character template: {e}")
            return {"status": "error", "message": str(e)}

    def create_character(self, name, template_id, health=100.0, level=1):
        """Create a new character from a template"""
        try:
            with SessionLocal() as db:
                template = db.query(CharacterTemplate).get(template_id)
                if not template:
                    return {"status": "error", "message": "Template not found"}

                character = Character(
                    name=name,
                    health=health,
                    level=level,
                    template_id=template_id
                )
                db.add(character)
                db.commit()

                return {
                    "status": "success",
                    "character": {
                        "id": character.id,
                        "name": character.name,
                        "health": character.health,
                        "template_name": template.name
                    }
                }
        except Exception as e:
            logger.error(f"Failed to create character: {e}")
            return {"status": "error", "message": str(e)}

    def get_template_with_image(self, template_id):
        """Get template with image data as base64 URL"""
        try:
            with SessionLocal() as db:
                template = db.query(CharacterTemplate).get(template_id)
                if not template:
                    return {"status": "error", "message": "Template not found"}

                image_url = None
                if template.image_data and template.image_mime:
                    image_data = base64.b64encode(template.image_data).decode("utf-8")
                    image_url = f"data:{template.image_mime};base64,{image_data}"

                return {
                    "status": "success",
                    "template": {
                        "id": template.id,
                        "name": template.name,
                        "image_url": image_url,
                        "tags": [tag.name for tag in template.tags]
                    }
                }
        except Exception as e:
            logger.error(f"Failed to get template: {e}")
            return {"status": "error", "message": str(e)}
