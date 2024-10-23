from sqlalchemy import Column, Integer, LargeBinary, String
from settings.settings_db import Base, settings_db
from sqlalchemy.orm import Mapped, mapped_column
from settings.settings_db import settings_db


class Table_news(Base):

    __tablename__ = "table_news"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, index=True)

    news = Column(String)

    image = Column(LargeBinary)



Base.metadata.create_all(bind=settings_db.engine)