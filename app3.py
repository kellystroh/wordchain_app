from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)

from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker, scoped_session
from database_setup import Base, Game
import numpy as np
import random
from functions import pick_new, pick_set, find_active
from functions import Generate_Board, Display_Choose_Mode, Display_Guess_Mode, Enact_Choice, Enact_Guess, Concede
from forms import AnswerForm, SelectForm, SubmitForm, RestartForm, ConcedeForm
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

with open("word_dict.pickle", 'rb') as inputfile:
    word_dict = pickle.load(inputfile)

#landing page to start a new game
@app.route('/',methods=['GET','POST'])
def index():
    form = SubmitForm()
    if form.validate_on_submit():
        try:
            session = DBSession()
            a = Generate_Board().go(session)
            b = 0
            session.commit()
        except:
            session.rollback()
            a, b = random.randint(50, 100), 0
        finally:
            session.close()

        return redirect(url_for('choose_mode', a=a, b=b))
    return render_template("books.html", form=form)

#This will let us Create a new book and save it in our database
@app.route('/game/<a>/<b>/choose',methods=['GET','POST'])
def choose_mode(a, b):
    session = DBSession()
    try:
        params = Display_Choose_Mode().go(session, a, b)
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

    if params['restart'].validate_on_submit():
        return redirect(url_for('index')) 
    
    if params['concede'].validate_on_submit():
        session = DBSession()
        try:
            params = Concede().go(session, params, a, b)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
        return redirect(url_for('choose_mode', **params)) 

    if params['form1'].validate_on_submit():
        session = DBSession()
        try:
            params = Enact_Choice().go(session, params, a, 0)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

        return redirect(url_for('guess_mode', **params))

    elif params['form2'].validate_on_submit():
        session = DBSession()
        try:
            params = Enact_Choice().go(session, params, a, 1)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

        return redirect(url_for('guess_mode', **params))
    else:
        return render_template('pick_mode.html', **params)

@app.route("/game/<a>/<b>/guess",methods=['GET','POST'])
def guess_mode(a, b):
    session = DBSession()
    try:
        params = Display_Guess_Mode().go(session, a, b)
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
    
    if params['restart'].validate_on_submit():
        return redirect(url_for('index'))   

    if params['concede'].validate_on_submit():
        session = DBSession()
        try:
            params = Concede().go(session, params, a, b)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
        return redirect(url_for('choose_mode', **params)) 

    if params['form'].validate_on_submit():
        session = DBSession()
        try:
            params = Enact_Guess().go(session, params, a, b)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

        return redirect(url_for('choose_mode', **params))
    
    return render_template('guess_mode.html', **params)

if __name__ == '__main__':
   app.debug = True
   app.run(host='0.0.0.0', port=8080)


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
