from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)

from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Game
import numpy as np
import random
from functions import pick_new, pick_set
import pickle
from ast import literal_eval
from flask_wtf import FlaskForm
from wtforms import StringField, TextField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length

app.config['SECRET_KEY'] = 'fijiferry'

#Connect to Database and create database session
engine = create_engine('sqlite:///game-records.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

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

with open("word_dict.pickle", 'rb') as inputfile:
    word_dict = pickle.load(inputfile)

#landing page to start a new game
@app.route('/',methods=['GET','POST'])
def index():
    form = SubmitForm()
    if form.validate_on_submit():
        brd = pick_set(word_dict)
        new = Game(board = str(brd))
        session.add(new)
        session.commit()
        a = new.id
        b = new.turn
        status = {"a":a, "b":b}
        return redirect(url_for('choose_mode', **status))
    return render_template("books.html", form=form)

#This will let us Create a new book and save it in our database
@app.route('/game/<a>/<b>/choose',methods=['GET','POST'])
def choose_mode(a, b):

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
              'choice': choice,
              'a':a, 'b':b}
             
    if form1.validate_on_submit():
        game = session.query(Game).filter(Game.id == a).all()
        ### check if player chose same word as last turn
        # if choice == active[1]:
        #     letters_active, letters_other = letters_other, letters_active
        ### update value of choice to reflect player's choice
        choice = active[0]
        ### check whether more preview letters are available
        if len(board_list[choice]) > letters_active + 1:
            letters_active = game[0].letters_active + 1
        ### update database 
        session.query(Game).filter(Game.id == a).update({"choice": choice, 
                                                          "letters_active":letters_active, 
                                                          "letters_other":letters_other})
        session.commit()
        ### update params
        params['choice'] = choice
        params['letters_active'] = letters_active
        params['letters_other'] = letters_other
        return redirect(url_for('guess_mode', **params))

    elif form2.validate_on_submit():
        game = session.query(Game).filter(Game.id == a).all()
        ### check if player chose same word as last turn
        # if choice == active[0]:
        #     letters_active, letters_other = letters_other, letters_active
        ### update value of choice to reflect player's choice
        choice = active[1]
        ### check whether more preview letters are available
        if len(board_list[choice]) > letters_other + 1:
            letters_other = game[0].letters_other + 1
        ### update database 
        session.query(Game).filter(Game.id == a).update({"choice": choice, 
                                                          "letters_active":letters_active, 
                                                          "letters_other":letters_other})
        session.commit()
        ### update params
        params['choice'] = choice
        params['letters_active'] = letters_active
        params['letters_other'] = letters_other
        return redirect(url_for('guess_mode', **params))
    else:
        return render_template('pick_mode.html', **params)

@app.route("/game/<a>/<b>/guess",methods=['GET','POST'])
def guess_mode(a, b):
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
              'a':a, 'b':b}
    
    if form.validate_on_submit():
        ans = request.form['answer']
        if ans == board_list[choice]:
            '''
            What happens when answer is right 
            '''
            turn += 2
            b = int(b) + 1
            solved.append(choice)
            solved = sorted(solved)
            if choice == active[0]:
                letters_active = 0
            else: 
                letters_other = 0
            active = find_active(solved)
            params['b'] = b
            params['turn'] = turn
            params['solved'] = solved
            params['active'] = active
            params['letters_active'] = letters_active
            params['letters_other']
            session.query(Game).filter(Game.id == a).update({'turn': turn,
                                                            'active': str(active),
                                                            'solved': str(solved),
                                                            'letters_active':letters_active,
                                                            'letters_other': letters_other})
        else:
            '''
            What happens when answer is wrong 
            '''
            turn += 1
            b = int(b) + 1
            params['b'] = b
            params['turn'] = turn
            game = session.query(Game).filter(Game.id == a).all()
            session.query(Game).filter(Game.id == a).update({'turn': turn})
            session.commit()

        return redirect(url_for('choose_mode', **params))
    
    return render_template('guess_mode.html', **params)

@app.route("/play2",methods=['GET','POST'])
def play2():
    return render_template('play2.html')

@app.route("/game/play",methods=['GET','POST'])
def play():
    
    ct = session.query(Game).count()
    game = session.query(Game).filter(Game.id == ct).all()
    board = enumerate(literal_eval(game[0].board))
    solved = literal_eval(game[0].solved)
    turn = game[0].turn
    not_solved = []
    for x in range(0,9):
        if x not in solved:
            not_solved.append(x)
    
    choices = [min(not_solved), max(not_solved)]
    return render_template('guess_mode.html', board=board, solved=solved, choices=choices, turn=turn)
# #This will let us Update our books and save it in our database
# @app.route("/books/<int:book_id>/edit/", methods = ['GET', 'POST'])
# def editBook(book_id):
#    editedBook = session.query(Book).filter_by(id=book_id).one()
#    if request.method == 'POST':
#        if request.form['name']:
#            editedBook.title = request.form['name']
#            return redirect(url_for('showBooks'))
#    else:
#        return render_template('editBook.html', book = editedBook)

# #This will let us Delete our book
# @app.route('/books/<int:book_id>/delete/', methods = ['GET','POST'])
# def deleteBook(book_id):
#    bookToDelete = session.query(Book).filter_by(id=book_id).one()
#    if request.method == 'POST':
#        session.delete(bookToDelete)
#        session.commit()
#        return redirect(url_for('showBooks', book_id=book_id))
#    else:
#        return render_template('deleteBook.html',book = bookToDelete)


# <div class="flex-container">
#     <div>1</div>
#     <div>2</div>
#     <div>3</div>
# </div>

if __name__ == '__main__':
   app.debug = True
   app.run(host='0.0.0.0', port=80)


'''
       <!-- {% for book in books %}
       <li> {{book.title}} by {{book.author}} </li>
       <a href="{{url_for('editBook', book_id = book.id )}}">
           Edit
       </a>
       <a href="{{url_for('deleteBook', book_id = book.id )}}" style="margin-left: 10px;">
           Delete
       </a>
       <br> <br>
       {% endfor %} -->
'''
