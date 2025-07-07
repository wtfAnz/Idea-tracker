from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ideas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key_here'
db = SQLAlchemy(app)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    ideas = db.relationship('Idea', backref='category', lazy=True)

class Idea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)

@app.route('/')
def index():
    category_id = request.args.get('category')
    if category_id:
        ideas = Idea.query.filter_by(category_id=category_id).all()
    else:
        ideas = Idea.query.all()
    categories = Category.query.all()
    return render_template('index.html', ideas=ideas, categories=categories, selected_category=category_id)

@app.route('/add', methods=['GET', 'POST'])
def add_idea():
    categories = Category.query.all()
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        category_id = request.form.get('category_id')
        idea = Idea(title=title, description=description, category_id=category_id or None)
        db.session.add(idea)
        db.session.commit()
        flash('Idea added!')
        return redirect(url_for('index'))
    return render_template('add_idea.html', categories=categories)

@app.route('/edit/<int:idea_id>', methods=['GET', 'POST'])
def edit_idea(idea_id):
    idea = Idea.query.get_or_404(idea_id)
    categories = Category.query.all()
    if request.method == 'POST':
        idea.title = request.form['title']
        idea.description = request.form['description']
        idea.category_id = request.form.get('category_id') or None
        db.session.commit()
        flash('Idea updated!')
        return redirect(url_for('index'))
    return render_template('edit_idea.html', idea=idea, categories=categories)

@app.route('/delete/<int:idea_id>', methods=['POST'])
def delete_idea(idea_id):
    idea = Idea.query.get_or_404(idea_id)
    db.session.delete(idea)
    db.session.commit()
    flash('Idea deleted!')
    return redirect(url_for('index'))

@app.route('/categories', methods=['GET', 'POST'])
def manage_categories():
    if request.method == 'POST':
        name = request.form['name']
        if not Category.query.filter_by(name=name).first():
            db.session.add(Category(name=name))
            db.session.commit()
            flash('Category added!')
        else:
            flash('Category already exists!')
        return redirect(url_for('manage_categories'))
    categories = Category.query.all()
    return render_template('categories.html', categories=categories)

@app.route('/categories/delete/<int:category_id>', methods=['POST'])
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted!')
    return redirect(url_for('manage_categories'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)