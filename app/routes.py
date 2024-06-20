from flask import abort, Blueprint, render_template, redirect, url_for, flash, request
from . import db, bcrypt, login_manager
from .forms import RegistrationForm, LoginForm, ProjectForm, TaskForm
from .models import User, Project, Task
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


@main.route('/project/<int:project_id>/tasks', methods=['GET', 'POST'])
@login_required
def project_tasks(project_id):
    project = Project.query.get_or_404(project_id)
    if project.owner != current_user:
        abort(403)
    form = TaskForm()
    if form.validate_on_submit():
        task = Task(name=form.name.data, description=form.description.data, deadline=form.deadline.data, status=form.status.data, project=project, user=current_user)
        db.session.add(task)
        db.session.commit()
        flash('Task created successfully!', 'success')
        return redirect(url_for('main.project_tasks', project_id=project.id))
    project_tasks = Task.query.filter_by(project_id=project.id).all()
    return render_template('tasks.html', title='Project Tasks', form=form, project=project, tasks=project_tasks)


@main.route('/task/<int:task_id>', methods=['GET', 'POST'])
@login_required
def task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user != current_user:
        abort(403)
    form = TaskForm()
    if form.validate_on_submit():
        task.name = form.name.data
        task.description = form.description.data
        task.deadline = form.deadline.data
        task.status = form.status.data
        db.session.commit()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('main.project_tasks', project_id=task.project_id))
    elif request.method == 'GET':
        form.name.data = task.name
        form.description.data = task.description
        form.deadline.data = task.deadline
        form.status.data = task.status
    return render_template('task.html', title='Edit Task', form=form, task=task)


@main.route('/task/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user != current_user:
        abort(403)
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('main.project_tasks', project_id=task.project_id if task.project_id else None))
