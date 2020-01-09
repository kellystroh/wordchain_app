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

#we create the table classes and extend them from the 
#declarative base Class.
class Game(Base):
   __tablename__ = 'game'

   id = Column(Integer, primary_key=True)
   board = Column(String(400), nullable=False)
   answers = Column(String(1000), default="", nullable=False)
   solved = Column(String(100), default="[0,9]")
   active = Column(String(100), default="[1,8]")
   preview_top = Column(Integer(), default=0)
   preview_bottom = Column(Integer(), default=0)
   choice = Column(Integer(), default=0)
   turn = Column(Integer(), default=1)
   finished = Column(Integer(), default=0)
   score1 = Column(Integer(), default=0)
   score2 = Column(Integer(), default=0)

class Turn(Base):
   __tablename__ = 'turn'

   id = Column(Integer, primary_key=True)
   game_id = Column(Integer, ForeignKey('game.id'))
   player = Column(Integer(), default=0)   
   start_score = Column(Integer(), default=0) 
   active = Column(String(20), default="[1,8]")
   choice = Column(Integer(), default=0)
   word = Column(String(30), default=" ")
   preview = Column(Integer(), default=1)
   num_guess = Column(Integer(), default = 0)
   clue_above = Column(String(30), default=" ")
   clue_below = Column(String(30), default=" ")
   turn_count = Column(Integer(), default=1)
   correct = Column(Integer(), default=0)
   points = Column(Integer(), default=0)

Base.metadata.create_all(engine)