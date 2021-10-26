# -*- coding: utf-8 -*-
from datetime import datetime
from random import randint
from flask import Flask, flash, request, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

from werkzeug.utils import secure_filename


ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}



app = Flask(__name__)
app.secret_key = b'_5#y2L"FGGRtyy4Q8z\n\xec]/'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MYSQL_DATABASE_CHARSET'] = 'utf8mb4'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123@localhost/barachlo'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///barachlo.db?check_same_thread=False'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 5*1024*1024
db = SQLAlchemy(app)

migrate = Migrate(app, db)

def create_app():
    app = Flask(__name__)
    db.init_app(app)
    migrate.init_app(app, db)
    return app

class Item(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable = False)
    price = db.Column(db.Integer, nullable = False)
    text = db.Column(db.Text, nullable = False)
    img_path = db.Column(db.String(200), default=r'static\uploads\img-1.jpg')
    created = db.Column(db.DateTime, default=datetime.now)
    isActive = db.Column(db.Boolean, default=True)
    views = db.Column(db.Integer, default=0)
    updated_on = db.Column(db.DateTime, default=datetime.now)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))

    def __repr__(self):
        return self.title


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), nullable=False)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    items = db.relationship('Item', backref='category')


    def __repr__(self):
        return "<{}:{}>".format(self.id, self.name)


class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), nullable=False)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)

    def __repr__(self):
        return "<{}:{}>".format(id, self.name)

list_cts = db.session.query(Category).all()

@app.route('/', methods=['GET', 'POST'])
def index():
    page = request.args.get('page', type=int, default=1)
    if request.method == 'POST' and 'search_input' in request.form:
        search_input = request.form["search_input"]
        search = "%{}%".format(search_input)
        search_query = Item.query.filter(Item.title.like(search), Item.isActive == 1)
        items = search_query.paginate(page=page, per_page=9)
        return render_template("index.html", data=items, search_input=search_input)

    items = Item.query.filter(Item.isActive!=0).order_by(Item.id)
    items = items.paginate(page=page, per_page=9)

    return render_template('index.html', data=items, for_sidebar=list_cts)


@app.route('/about')
def about():
    return render_template('about.html', for_sidebar=list_cts)


@app.route('/item/<int:id>', methods=['POST', 'GET'])
def item(id):
    page = request.args.get('page', type=int, default=1)
    if request.method == 'POST' and 'search_input' in request.form:
        search_input = request.form["search_input"]
        search = "%{}%".format(search_input)
        search_query = Item.query.filter(Item.title.like(search), Item.isActive == 1)
        items = search_query.paginate(page=page, per_page=9)
        return render_template("index.html", data=items, search_input=search_input)
    item = Item.query.get(id)
    if item:
        item.views +=1
        db.session.commit()
        return render_template('item_about.html', data=item, for_sidebar=list_cts)
    else:
        flash(f'Барахла с номером {id} не существует', category='message')
        return redirect(url_for('index'))


@app.route('/item/edit/<int:id>', methods=['POST', 'GET'])
def item_edit(id):
    page = request.args.get('page', type=int, default=1)
    if request.method == 'POST' and 'search_input' in request.form:
        search_input = request.form["search_input"]
        search = "%{}%".format(search_input)
        search_query = Item.query.filter(Item.title.like(search), Item.isActive == 1)
        items = search_query.paginate(page=page, per_page=9)
        return render_template("index.html", data=items, search_input=search_input)
    if request.method == 'POST':
        if request.form.get('is_active') == 'on':
            is_active = 0
        else: is_active = 1
        title = request.form['title']
        price = request.form['price']
        text = request.form['text']
        cat_select = request.form["cat_select"]
        # file = request.files['file']
        # if file and allowed_file(file.filename):
        #     filename = secure_filename(file.filename)
        #     path = os.path.join(app.config['UPLOAD_FOLDER'], datetime.now().strftime('%Y-%m-%d'))
        #     try:
        #         os.mkdir(path)
        #     except:
        #         pass
        #     filename = str(randint(100000, 999999))
        #     full_filename = os.path.join(path, filename)
        #     file.save(full_filename)
        item = dict(title=title, price=price, text=text, category_id=cat_select,
                    updated_on=datetime.utcnow(), isActive=is_active)

        try:
            db.session.query(Item).filter(Item.id == id).update(item)
            db.session.commit()
            return redirect('/')
        except:
            return "Ахтунг, все плохо"
    else:
        item = Item.query.get(id)
        ctgs = Category.query.all()
        return render_template('item_edit.html', data=item, ctgs = ctgs, for_sidebar=list_cts)


@app.route('/categories/<string:slug>', methods=['POST', 'GET'])
def categories(slug):
    page = request.args.get('page', type=int, default=1)
    if request.method == 'POST' and 'search_input' in request.form:
        search_input = request.form["search_input"]
        search = "%{}%".format(search_input)
        search_query = Item.query.filter(Item.title.like(search), Item.isActive == 1)
        items = search_query.paginate(page=page, per_page=9)
        return render_template("index.html", data=items, search_input=search_input)

    list_cts = db.session.query(Category).all()
    slug = db.session.query(Category, Item).join(Item).filter(Category.slug == slug)
    slug_pag = slug.paginate(page=page, per_page=9)

    print(slug_pag.items)

    if len(slug_pag.items) == 0:
        flash('В этой категории пока ничего нет')
        return redirect(url_for('index'))

    return render_template('categories.html', data=slug_pag, for_sidebar=list_cts)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/create', methods=['Post', 'GET'])
def create():
    categories = Category.query.all()
    if request.method == 'POST':
        title = request.form['title'].lower()
        price = request.form['price']
        text = request.form['text']
        cat_select = request.form["cat_select"]
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files.getlist('file')
        full_filenames = ''
        for file in file:
            # print(file.filename)
       # if user does not select file, browser also
       # submit an empty part without filename
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                path = os.path.join(app.config['UPLOAD_FOLDER'], datetime.now().strftime('%Y-%m-%d'))
                try:
                    os.mkdir(os.path.join('FlaskApp/static', path))
                except Exception as ex:
                    # flash(ex)
                    return redirect(request.url)
                filename = str(randint(100000, 999999))
                full_filename = os.path.join(path, filename)
                full_filenames = full_filenames + os.path.join(path, filename) + ','
                print(len(full_filenames))
                try:
                    file.save(os.path.join('FlaskApp/static', full_filename))
                except Exception as ex:
                    flash(ex)
                    return redirect(request.url)
        item = Item(title=title, price=price, text=text, img_path=full_filenames, category_id=cat_select,
                    created=datetime.utcnow())
        try:
            db.session.add(item)
            db.session.commit()
            return redirect('/')
        except:
            return "Ахтунг, все плохо"
    else:
        return render_template('create.html', data = categories, for_sidebar=list_cts)

if __name__ == '__main__':
    app.run(debug=True)