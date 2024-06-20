from flask_wtf import FlaskForm
from wtforms import BooleanField, DateTimeField, PasswordField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class ProjectForm(FlaskForm):
    name = StringField('Project Name', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Project Description', validators=[Length(max=200)])
    submit = SubmitField('Create Project')


class TaskForm(FlaskForm):
    name = StringField('Task Name', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Task Description', validators=[Length(max=200)])
    deadline = DateTimeField('Due Date (YYYY-MM-DD HH:MM:SS)', format='%Y-%m-%d %H:%M:%S')
    status = SelectField('Status', choices=[('Not Started', 'Not Started'), ('In Progress', 'In Progress'), ('Completed', 'Completed')])
    submit = SubmitField('Save Task')
