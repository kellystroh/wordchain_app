import random
import numpy as np

from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)

from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker, scoped_session
from database_setup import Base, Game
import numpy as np
import random
import pickle
from ast import literal_eval
from flask_wtf import FlaskForm
from wtforms import StringField, TextField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length

with open("word_dict.pickle", 'rb') as inputfile:
    word_dict = pickle.load(inputfile)


class SubmitForm(FlaskForm):
    """Submit form."""
    submit = SubmitField('Generate New Game')

class SelectForm(FlaskForm):
    """Submit form."""
    select = SubmitField('Guess This Word')

class AnswerForm(FlaskForm):
    """Answer form."""
    answer = TextField(label='Your Guess')
    submit = SubmitField('Submit')

def find_active(solved):
    if len(solved) < 10:
        not_solved = []
        for x in range(0,9):
            if x not in solved:
                not_solved.append(x)
        return [min(not_solved), max(not_solved)]
    else:
        return []

# def add_boards(word_dict, number):
#     board_collection = []
#     for x in range(number):
#             brd = pick_set(word_dict)
#             board_collection.append(brd)
#             session = DBSession()
#             new = Game(board = str(brd))
#             session.add(new)
#             session.commit()
#             session.close()
#             print(x)
    

class Generate_Board(object):
    def go(self, session):
        brd = pick_set(word_dict)
        new = Game(board = str(brd))
        session.add(new)
        session.flush()
        session.refresh(new)
        self.a = new.id
        return self.a

class Display_Choose_Mode(object):
    def go(self, session, a, b):
        form1 = SelectForm(prefix="form1")
        form2 = SelectForm(prefix="form2")
        game = session.query(Game).filter(Game.id == a).all()
        board_list = literal_eval(game[0].board)
        board = enumerate(board_list)
        solved = literal_eval(game[0].solved)
        active = literal_eval(game[0].active)
        turn = game[0].turn
        letters_active = game[0].letters_active
        letters_other = game[0].letters_other
        choice = game[0].choice
        params = {'form1':form1, 'form2':form2, 
                'board':board, 'solved':solved, 
                'active':active, 'turn':turn,
                'letters_active':letters_active,
                'letters_other':letters_other,
                'choice': choice, 'board_list':board_list,
                'a':a, 'b':b}
        return params

class Enact_Choice(object):
    def go(self, session, params, a, x):
        game = session.query(Game).filter(Game.id == a).all()
        choice = params['active'][x]
        ### check whether more preview letters are available
        if x == 0: 
            letters_other = game[0].letters_other
            if len(params['board_list'][choice]) > params['letters_active'] + 1:
                letters_active = game[0].letters_active + 1
            else:
                letters_active = game[0].letters_active
            ### update database 
            session.query(Game).filter(Game.id == a).update({"choice": choice, 
                                                            "letters_active":letters_active, 
                                                            "letters_other":letters_other})
        else: 
            letters_active = game[0].letters_active
            if len(params['board_list'][choice]) > params['letters_other'] + 1:
                letters_other = game[0].letters_other + 1
            else:
                letters_other = game[0].letters_other
            ### update database 
            session.query(Game).filter(Game.id == a).update({"choice": choice, 
                                                            "letters_active":letters_active, 
                                                            "letters_other":letters_other})
        ### update params
        params['choice'] = choice
        params['letters_active'] = letters_active
        params['letters_other'] = letters_other
        return params

class Display_Guess_Mode(object):
    def go(self, session, a, b):
        form = AnswerForm()
        game = session.query(Game).filter(Game.id == a).all()

        board_list = literal_eval(game[0].board)
        board = enumerate(board_list)
        solved = literal_eval(game[0].solved)
        turn = game[0].turn
        choice = game[0].choice
        active = literal_eval(game[0].active)
        letters_active = game[0].letters_active
        letters_other = game[0].letters_other
        params = {'form':form, 'choice':choice,
              'board':board, 'solved':solved, 
              'turn':turn, 'active':active,
              'letters_active':letters_active,
              'letters_other':letters_other, 
              'a':a, 'b':b, 'board_list':board_list}
        return params

class Enact_Guess(object):
    def go(self, session, params, a, b):
        ans = request.form['answer']
        if ans == params['board_list'][params['choice']]:
            '''
            What happens when answer is right 
            '''
            params['turn'] += 2
            b = int(b) + 1
            params['b'] = b
            params['solved'].append(params['choice'])
            params['solved'] = sorted(params['solved'])
            if params['choice'] == params['active'][0]:
                params['letters_active'] = 0
            else: 
                params['letters_other'] = 0
            params['active'] = find_active(params['solved'])
            session.query(Game).filter(Game.id == a).update({'turn': params['turn'],
                                                            'active': str(params['active']),
                                                            'solved': str(params['solved']),
                                                            'letters_active': params['letters_active'],
                                                            'letters_other': params['letters_other']})
        else:
            '''
            What happens when answer is wrong 
            '''
            params['turn'] += 1
            b = int(b) + 1
            params['b'] = b
            session.query(Game).filter(Game.id == a).update({'turn': b})
            session.commit()
        return params

def pick_new(word_dict, l_word, word_list):
    rng = list(range(len(word_dict[l_word])))
    random.shuffle(rng)
    random.shuffle(rng)
    choices = list(np.array(word_dict[l_word])[rng])
    for i in range(len(choices)):
        l = len(choices)
        if l > 0:
            if choices[i] in word_dict.keys():
                if choices[i] not in word_list:
                    new_word = choices[i]
                    word_list.append(new_word)
                    break
                else:
                    choices.remove(choices[i])
        else:
            raise ValueError('No choices left')
    return new_word, word_list

def pick_set(word_dict):
    word_list = []
    word1 = random.choice(list(word_dict.keys()))
    word_list.append(word1)
    
    word2, word_list = pick_new(word_dict, word1, word_list)
    word3, word_list = pick_new(word_dict, word2, word_list)
    word4, word_list = pick_new(word_dict, word3, word_list)
    word5, word_list = pick_new(word_dict, word4, word_list)
    word6, word_list = pick_new(word_dict, word5, word_list)
    word7, word_list = pick_new(word_dict, word6, word_list)
    word8, word_list = pick_new(word_dict, word7, word_list)
    word9, word_list = pick_new(word_dict, word8, word_list)
    _, word_list = pick_new(word_dict, word9, word_list)
    return word_list




'''
from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker, scoped_session
from database_setup import Base, Game
import numpy as np
import random
from sqlalchemy.sql.expression import func
import pickle
from functions import pick_new, pick_set, Generate_Board0, Generate_Board1
engine = create_engine('sqlite:///game-records.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()
x = Generate_Board0()
x.brd
'''
