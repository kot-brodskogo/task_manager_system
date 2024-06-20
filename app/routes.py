from flask import Blueprint, render_template, redirect, url_for, flash, request
from . import db, bcrypt, login_manager
from .forms import RegistrationForm, LoginForm, ProjectForm
from .models import User, Project
from flask_login import login_user, current_user, logout_user, login_required

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('home.html')


@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Register', form=form)


@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@main.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@main.route('/projects', methods=['GET', 'POST'])
@login_required
def projects():
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(name=form.name.data, description=form.description.data, owner=current_user)
        db.session.add(project)
        db.session.commit()
        flash('Project created successfully!', 'success')
        return redirect(url_for('main.projects'))
    user_projects = Project.query.filter_by(user_id=current_user.id).all()
    return render_template('projects.html', title='Projects', form=form, projects=user_projects)

@main.route('/project/<int:project_id>', methods=['GET', 'POST'])
@login_required
def project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.owner != current_user:
        abort(403)
    form = ProjectForm()
    if form.validate_on_submit():
        project.name = form.name.data
        project.description = form.description.data
        db.session.commit()
        flash('Project updated successfully!', 'success')
        return redirect(url_for('main.projects'))
    elif request.method == 'GET':
        form.name.data = project.name
        form.description.data = project.description
    return render_template('project.html', title='Edit Project', form=form, project=project)

@main.route('/project/<int:project_id>/delete', methods=['POST'])
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.owner != current_user:
        abort(403)
    db.session.delete(project)
    db.session.commit()
    flash('Project deleted successfully!', 'success')
    return redirect(url_for('main.projects'))
