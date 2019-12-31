import sys
#for creating the mapper code
from sqlalchemy import Column, ForeignKey, Integer, String, PickleType

#for configuration and class code
from sqlalchemy.ext.declarative import declarative_base

#for creating foreign key relationship between the tables
from sqlalchemy.orm import relationship

#for configuration
from sqlalchemy import create_engine

#create declarative_base instance
Base = declarative_base()

#we'll add classes here

#creates a create_engine instance at the bottom of the file
engine = create_engine('sqlite:///game-records.db')

Base.metadata.create_all(engine)

#we create the class Book and extend it from the Base Class.
class Game(Base):
   __tablename__ = 'game'

   id = Column(Integer, primary_key=True)
   board = Column(String(400), nullable=False)
   answers = Column(String(1000), default="", nullable=False)
   solved = Column(String(100), default="[0,9]")
   active = Column(String(100), default="[1,8]")
   letters_active = Column(Integer(), default=0)
   letters_other = Column(Integer(), default=0)
   choice = Column(Integer(), default=0)
   turn = Column(Integer(), default=1)
   finished = Column(Integer(), default=0)