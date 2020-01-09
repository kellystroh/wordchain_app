import random
import numpy as np

from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)

from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker, scoped_session
from database_setup import Base, Game, Turn
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

def whose_turn(turn):
    if turn % 2 != 0:
        player = 1
    else: 
        player = 2
    return player
def get_score(player, score1, score2):
    if player == 1:
        score = score1
    else: 
        score = score2
    return score

def get_clues(choice, solved, board_list):
    if choice - 1 in solved:
        clue_above = board_list[choice - 1]
    else:
        clue_above = np.nan
    if choice + 1 in solved:
        clue_below = board_list[choice + 1]
    else:
        clue_below = np.nan
    return clue_above, clue_below


class Generate_Board(object):
    def go(self, session):
        brd = pick_set(word_dict)
        new_game = Game(board = str(brd))
        session.add(new_game)
        session.flush()
        session.refresh(new_game)
        self.a = new_game.id
        return self.a

class Display_Choose_Mode(object):
    def go(self, session, a, b):
        # Define forms for word selection & restart/concede
        form1 = SelectForm(prefix="form1")
        form2 = SelectForm(prefix="form2")
        restart = RestartForm(prefix="restart")
        concede = ConcedeForm(prefix="concede")

        # Query DB to get details on specific game & turn
        game = session.query(Game).filter(Game.id == a).all()[0]
        
        # Define query results as local variables -- game
        board_list = literal_eval(game.board)
        board = enumerate(board_list)
        ### solved: List of board_list indices for words that have been solved already
        ### active: List of board_list indices for words available to choose/guess (max 2 items)
        solved, active = literal_eval(game.solved), literal_eval(game.active)
        score1, score2 = game.score1, game.score2
        turn, choice = game.turn, game.choice
        preview_top, preview_bottom = game.preview_top, game.preview_bottom

        #calc turn details we want to track
        turn_records = session.query(Turn).filter(Turn.game_id == a).all()
        turn_count = len(turn_records) + 1
        player = whose_turn(turn)
        start_score = get_score(player, score1, score2)

        # New turn
        new_turn = Turn(game_id=a, active=str(active), 
                        player=player, start_score=start_score,
                        turn_count=turn_count)
        session.add(new_turn)

        params = {'form1':form1, 
                  'form2':form2,
                  'concede':concede, 
                  'restart':restart, 
                  'board':board, 
                  'solved':solved, 
                  'active':active, 
                  'turn':turn,
                  'preview_top':preview_top,
                  'preview_bottom':preview_bottom,
                  'score1':score1, 
                  'score2':score2, 
                  'choice': choice, 
                  'board_list':board_list,
                  'turn_count':turn_count,
                  'a':a, 
                  'b':b}
        return params

class Enact_Choice(object):
    def go(self, session, params, a, x):
        game = session.query(Game).filter(Game.id == a).all()[0]
        # turn_record = session.query(Turn).filter(Turn.game_id == a, Turn.turn_count == turn_count).all()
        
        choice = params['active'][x]
        word = params['board_list'][choice]
        clue_above, clue_below = get_clues(choice, params['solved'], params['board_list'])
        ### check whether more preview letters are available
        num_guess = len(session.query(Turn).filter(Turn.game_id == a, Turn.choice == choice).all())

        if x == 0: 
            preview_bottom = game.preview_bottom
            if len(params['board_list'][choice]) > params['preview_top'] + 1:
                preview_top = game.preview_top + 1
            else:
                preview_top = game.preview_top
            preview = preview_top
            ### update database 
            session.query(Game).filter(Game.id == a).update({"choice": choice, 
                                                            "preview_top":preview_top, 
                                                            "preview_bottom":preview_bottom})
            session.query(Turn).filter(Turn.game_id == a, 
                                       Turn.turn_count == params['turn_count']).update({'choice':choice,
                                                                              'preview':preview,
                                                                              'num_guess':num_guess,
                                                                              'word':word,
                                                                              'clue_above':clue_above,
                                                                              'clue_below':clue_below})
        else: 
            preview_top = game.preview_top
            if len(params['board_list'][choice]) > params['preview_bottom'] + 1:
                preview_bottom = game.preview_bottom + 1
            else:
                preview_bottom = game.preview_bottom
            preview = preview_bottom
            ### update database 
            session.query(Game).filter(Game.id == a).update({"choice": choice, 
                                                            "preview_top":preview_top, 
                                                            "preview_bottom":preview_bottom})
            session.query(Turn).filter(Turn.game_id == a, 
                                       Turn.turn_count == params['turn_count']).update({'choice':choice,
                                                                              'preview':preview,
                                                                              'num_guess':num_guess,
                                                                              'word':word,
                                                                              'clue_above':clue_above,
                                                                              'clue_below':clue_below})
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
        game = session.query(Game).filter(Game.id == a).all()[0]
        turn_records = session.query(Turn).filter(Turn.game_id == a).all()
        turn_count = len(turn_records)
        board_list = literal_eval(game.board)
        board = enumerate(board_list)
        solved = literal_eval(game.solved)
        turn = game.turn
        score1, score2 = game.score1, game.score2
        choice = game.choice
        active = literal_eval(game.active)
        preview_top = game.preview_top
        preview_bottom = game.preview_bottom
        params = {'form':form, 'choice':choice,
              'board':board, 'solved':solved, 
              'turn':turn, 'active':active,
              'preview_top':preview_top,
              'score1':score1, 'score2':score2,
              'preview_bottom':preview_bottom,
              'turn_count':turn_count, 
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
            correct = 1
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
            session.query(Turn).filter(Turn.game_id == a, 
                                       Turn.turn_count == params['turn_count']).update({'answer':ans,
                                                                              'points':score,
                                                                              'correct':correct})
        else:
            '''
            What happens when answer is wrong 
            '''
            points, correct = 0, 0
            params['turn'] += 1
            b = int(b) + 1
            params['b'] = b
            session.query(Game).filter(Game.id == a).update({'turn': b})
            session.query(Turn).filter(Turn.game_id == a, 
                                       Turn.turn_count == params['turn_count']).update({'answer':ans,
                                                                              'points':points,
                                                                              'correct':correct})
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
