from typing import Optional

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Animal(Base):
   
    __tablename__ = "animals"

   
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)

   
    ancestor_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("animals.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

 
    fun_fact: Mapped[Optional[str]] = mapped_column(Text, nullable=True, default=None)

    scientific_name:  Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    taxonomy_class:   Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    image_url:        Mapped[Optional[str]] = mapped_column(Text,        nullable=True)
    locations:        Mapped[Optional[str]] = mapped_column(Text,        nullable=True)
    temperament:      Mapped[Optional[str]] = mapped_column(Text,        nullable=True)
    lifespan:         Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    weight:           Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

   
    ancestor: Mapped[Optional["Animal"]] = relationship(
        "Animal",
        back_populates="descendants",
        remote_side="Animal.id",
        foreign_keys=[ancestor_id],
    )
    descendants: Mapped[list["Animal"]] = relationship(
        "Animal",
        back_populates="ancestor",
        foreign_keys=[ancestor_id],
    )

    def __repr__(self) -> str:
        return f"<Animal id={self.id} name='{self.name}' ancestor_id={self.ancestor_id}>"
