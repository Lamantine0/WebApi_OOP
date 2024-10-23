from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase




class Settings_DB:

    def __init__(self, SQLALCHEMY_DATABASE_URL):
        self.__SQLALCHEMY_DATABASE_URL__ = SQLALCHEMY_DATABASE_URL
        self.engine =  self.settings() 
        self.SessionLocal = self.locationSession()
    

    def settings(self):

      engine = self.engine = create_engine(
            self.__SQLALCHEMY_DATABASE_URL__,
            connect_args = {"check_same_thread" : False} 
        )
      
      return engine

    def locationSession(self):

       session = self.SessionLocal = sessionmaker(autoflush=False, bind=self.engine)

       return session

    

        



settings_db = Settings_DB("sqlite:///./date_news.db")






class Base(DeclarativeBase):
    pass        



