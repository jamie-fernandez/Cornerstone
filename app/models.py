from sqlalchemy import Column, Integer, String, Float, ForeignKey, Table, LargeBinary
from sqlalchemy.orm import relationship
from app.base import Base

# Association table for many-to-many relationship
template_tags = Table(
    "template_tags",
    Base.metadata,
    Column("template_id", Integer, ForeignKey("character_templates.id")),
    Column("tag_id", Integer, ForeignKey("tags.id"))
)

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    def __repr__(self):
        return f"<Tag {self.name}>"

class CharacterTemplate(Base):
    __tablename__ = "character_templates"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    image_data = Column(LargeBinary)  # For storing images as blobs
    image_mime = Column(String(50))   # MIME type (e.g., "image/png")

    # Relationships
    tags = relationship("Tag", secondary=template_tags, back_populates="templates")
    characters = relationship("Character", back_populates="template")

    def __repr__(self):
        return f"<CharacterTemplate {self.name}>"

class Character(Base):
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    health = Column(Float, default=100.0)
    level = Column(Integer, default=1)

    template_id = Column(Integer, ForeignKey("character_templates.id"), nullable=False)
    template = relationship("CharacterTemplate", back_populates="characters")

    def __repr__(self):
        return f"<Character {self.name}>"

# Back-populate relationships
Tag.templates = relationship("CharacterTemplate", secondary=template_tags, back_populates="tags")
