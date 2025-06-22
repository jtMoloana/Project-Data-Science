from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'changeme'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///qapro.db'
app.config['UPLOAD_FOLDER'] = 'uploads'

db = SQLAlchemy(app)

if not os.path.exists('uploads'):
    os.makedirs('uploads')

class Provider(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    provider_id = db.Column(db.Integer, db.ForeignKey('provider.id'))
    completed = db.Column(db.Boolean, default=False)

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200))
    provider_id = db.Column(db.Integer, db.ForeignKey('provider.id'))

@app.route('/')
def index():
    providers = Provider.query.all()
    return render_template('index.html', providers=providers)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        provider = Provider(name=name, email=email)
        db.session.add(provider)
        db.session.commit()
        flash('Provider registered!')
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/provider/<int:provider_id>')
def provider_detail(provider_id):
    provider = Provider.query.get_or_404(provider_id)
    tasks = Task.query.filter_by(provider_id=provider.id).all()
    docs = Document.query.filter_by(provider_id=provider.id).all()
    return render_template('provider_detail.html', provider=provider, tasks=tasks, docs=docs)

@app.route('/provider/<int:provider_id>/add_task', methods=['POST'])
def add_task(provider_id):
    title = request.form['title']
    desc = request.form.get('description', '')
    task = Task(title=title, description=desc, provider_id=provider_id)
    db.session.add(task)
    db.session.commit()
    return redirect(url_for('provider_detail', provider_id=provider_id))

@app.route('/task/<int:task_id>/complete')
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.completed = True
    db.session.commit()
    return redirect(url_for('provider_detail', provider_id=task.provider_id))

@app.route('/provider/<int:provider_id>/upload', methods=['POST'])
def upload(provider_id):
    file = request.files['document']
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        doc = Document(filename=file.filename, provider_id=provider_id)
        db.session.add(doc)
        db.session.commit()
    return redirect(url_for('provider_detail', provider_id=provider_id))

@app.route('/audit/<int:provider_id>')
def audit(provider_id):
    provider = Provider.query.get_or_404(provider_id)
    tasks = Task.query.filter_by(provider_id=provider.id).all()
    if all(t.completed for t in tasks):
        flash('Audit passed. QAPRO certificate issued.')
    else:
        flash('Audit failed. Complete all tasks.')
    return redirect(url_for('provider_detail', provider_id=provider.id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
