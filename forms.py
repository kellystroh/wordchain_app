from flask_wtf import FlaskForm
from wtforms import StringField, TextField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length

class SubmitForm(FlaskForm):
    """Submit form."""
    submit = SubmitField('Generate New Game')

class SelectForm(FlaskForm):
    """Submit form."""
    select = SubmitField('Guess This Word')

class ConcedeForm(FlaskForm):
    """Concede form."""
    concede = SubmitField('I Quit! Show me the Answers.')

class RestartForm(FlaskForm):
    restart = SubmitField('Leave game & Start Anew')

class AnswerForm(FlaskForm):
    """Answer form."""
    answer = TextField(label='Your Guess')
    submit = SubmitField('Submit')