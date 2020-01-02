from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)

from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker, scoped_session
from database_setup import Base, Game
import numpy as np
import random
from functions import pick_new, pick_set, find_active
from functions import Generate_Board, Display_Choose_Mode, Display_Guess_Mode, Enact_Choice, Enact_Guess
from functions import AnswerForm, SelectForm, SubmitForm
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
# session = scoped_session(DBSession)

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
