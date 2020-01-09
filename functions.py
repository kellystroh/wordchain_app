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
from forms import SelectForm, SubmitForm, AnswerForm, ConcedeForm, RestartForm


with open("word_dict.pickle", 'rb') as inputfile:
    word_dict = pickle.load(inputfile)


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
        restart = RestartForm(prefix="restart")
        concede = ConcedeForm(prefix="concede")
        game = session.query(Game).filter(Game.id == a).all()
        board_list = literal_eval(game[0].board)
        board = enumerate(board_list)
        solved = literal_eval(game[0].solved)
        active = literal_eval(game[0].active)
        score1, score2 = game[0].score1, game[0].score2
        turn = game[0].turn
        preview_top = game[0].preview_top
        preview_bottom = game[0].preview_bottom
        choice = game[0].choice
        params = {'form1':form1, 'form2':form2,
                'concede':concede, 'restart':restart, 
                'board':board, 'solved':solved, 
                'active':active, 'turn':turn,
                'preview_top':preview_top,
                'preview_bottom':preview_bottom,
                'score1':score1, 'score2':score2, 
                'choice': choice, 'board_list':board_list,
                'a':a, 'b':b}
        return params

class Enact_Choice(object):
    def go(self, session, params, a, x):
        game = session.query(Game).filter(Game.id == a).all()
        choice = params['active'][x]
        ### check whether more preview letters are available
        if x == 0: 
            preview_bottom = game[0].preview_bottom
            if len(params['board_list'][choice]) > params['preview_top'] + 1:
                preview_top = game[0].preview_top + 1
            else:
                preview_top = game[0].preview_top
            ### update database 
            session.query(Game).filter(Game.id == a).update({"choice": choice, 
                                                            "preview_top":preview_top, 
                                                            "preview_bottom":preview_bottom})
        else: 
            preview_top = game[0].preview_top
            if len(params['board_list'][choice]) > params['preview_bottom'] + 1:
                preview_bottom = game[0].preview_bottom + 1
            else:
                preview_bottom = game[0].preview_bottom
            ### update database 
            session.query(Game).filter(Game.id == a).update({"choice": choice, 
                                                            "preview_top":preview_top, 
                                                            "preview_bottom":preview_bottom})
        ### update params
        params['choice'] = choice
        params['preview_top'] = preview_top
        params['preview_bottom'] = preview_bottom
        return params

class Concede(object):
    def go(self, session, params, a, b):
        full = list(range(0,10))
        params['solved'] = full
        session.query(Game).filter(Game.id == a).update({"solved": str(full)})

        session.commit()
        return params

class Display_Guess_Mode(object):
    def go(self, session, a, b):
        form = AnswerForm()
        game = session.query(Game).filter(Game.id == a).all()
        board_list = literal_eval(game[0].board)
        board = enumerate(board_list)
        solved = literal_eval(game[0].solved)
        turn = game[0].turn
        score1, score2 = game[0].score1, game[0].score2
        choice = game[0].choice
        active = literal_eval(game[0].active)
        preview_top = game[0].preview_top
        preview_bottom = game[0].preview_bottom
        params = {'form':form, 'choice':choice,
              'board':board, 'solved':solved, 
              'turn':turn, 'active':active,
              'preview_top':preview_top,
              'score1':score1, 'score2':score2,
              'preview_bottom':preview_bottom, 
              'a':a, 'b':b, 'board_list':board_list}
        return params

class Enact_Guess(object):
    def go(self, session, params, a, b):
        ans = request.form['answer']
        ans = ans.lower()
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
                pro_rate = params['preview_top'] / (len(params['board_list'][params['choice']]))
                params['preview_top'] = 0
            else: 
                pro_rate = params['preview_bottom'] / (len(params['board_list'][params['choice']]))
                params['preview_bottom'] = 0
            score = (int(np.floor(10*(1-pro_rate))))
            if params['turn'] % 2 != 0:
                params['score1'] += score
            else:
                params['score2'] += score
            params['active'] = find_active(params['solved'])
            session.query(Game).filter(Game.id == a).update({'turn': params['turn'],
                                                            'active': str(params['active']),
                                                            'solved': str(params['solved']),
                                                            'preview_top': params['preview_top'],
                                                            'preview_bottom': params['preview_bottom'],
                                                            'score1': params['score1'],
                                                            'score2': params['score2']})
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
