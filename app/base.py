from sqlalchemy.orm import declarative_base


class DictMixin:
    """Serialize model instances to plain dicts for the JS bridge.

    Only JSON-serializable values may cross the pywebview bridge, so API
    methods must convert ORM objects with ``to_dict()`` before returning
    them — never return ORM instances directly.
    """

    def to_dict(self):
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }


Base = declarative_base(cls=DictMixin)
