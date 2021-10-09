from datetime import timedelta
from flask import Flask, render_template, redirect, request, url_for, flash, session, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash 
from werkzeug.utils import secure_filename
import urllib.request
import os

UPLOAD_FOLDER = '/templates/static/img'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
app = Flask(__name__,
            static_url_path='', 
            static_folder='templates/static',
            template_folder='templates')

UPLOAD_FOLDER = 'templates/static/uploads/'
app.config["SECRET_KEY"] = 'secret'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

db = SQLAlchemy(app) 
login_manager = LoginManager(app)


@login_manager.user_loader
def current_user(user_id):
    return User.query.get(user_id)


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(84), nullable=False)
    email = db.Column(db.String(84), nullable=False, unique=True, index=True)
    password = db.Column(db.String(255), nullable=False)
    cargo = db.Column(db.String(84))
    celular = db.Column(db.String(84),)
    profile = db.relationship('Profile', backref='user', uselist=False)

    def __str__(self):
        return self.name

class Cardapio(db.Model):
    __tablename__ = "cardapio"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(84), nullable=False)
    tipo = db.Column(db.String(84), nullable=False)
    valor = db.Column(db.DECIMAL(10,2), nullable=False)
    descricao = db.Column(db.String(120))
    thumb = db.Column(db.String(240))
    

    def __str__(self):
        return self.nome

class Profile(db.Model):
    __tablename__ = "profiles"
    id = db.Column(db.Integer, primary_key=True)
    photo = db.Column(db.Unicode(124), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))


    def __str__(self):
        return self.name

@app.route("/")
def index():
    users = User.query.all() # Select * from users; 
    cardapios = Cardapio.query.all()
    return render_template("index.html", users=users, cardapios=cardapios)

@app.route('/cart/', methods=['POST', 'GET'])
@app.route('/cart/<int:id>', methods=['POST', 'GET'])
def carrinho(id=0):
    if id == 0:
        cartlist = session['carrinho']  
        cart = []
        for i in cartlist:
            item_id = Cardapio.query.filter_by(id=i) 
            item_id = Cardapio.query.filter_by(id=i).first()
            item = item_id
            cart.append(item) 
        return render_template('carrinho.html', cart=cart) 
    if 'carrinho' in session: 
        cartlist = session['carrinho'] 
        cartlist.append(id)
        session['carrinho'] = cartlist
    else:
        session['carrinho'] = [] # setting session data
    return "Carrinho: {}".format(session.get('carrinho'))

@app.route('/delete-cart/')
def delete_visits():
    session['carrinho'] = [] # delete cart
    return 'carrinho deletado'

@app.route("/cadastros")
@login_required
def cadastros():
    users = User.query.all() # Select * from users; 
    cardapios = Cardapio.query.all() # Select * from users; 
    return render_template("cadastros.html", users=users, cardapios=cardapios)

@app.route("/pedidos")
@login_required
def pedidos():
    users = User.query.all() # Select * from users; 
    return render_template("pedidos.html", users=users)    

@app.route("/user/<int:id>")
@login_required
def unique(id):
    user = User.query.get(id)
    return render_template("user.html", user=user)

@app.route("/buscar", methods=['GET']) 
def buscar():
    query = request.args.get("query") # here query will be the search inputs name
    cardapios = Cardapio.query.filter(Cardapio.nome.contains(query))
    cardapios = Cardapio.query.filter(Cardapio.nome.contains(query)).all()
    return render_template("buscar.html", cardapios=cardapios, query=query)

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login')

@app.route("/user/delete/<int:id>")
def delete(id):
    user = User.query.filter_by(id=id).first()
    db.session.delete(user)
    db.session.commit()

    return redirect("/cadastros")

@app.route("/cardapio/delete/<int:id>")
def delete_cardapio(id):
    cardapio = Cardapio.query.filter_by(id=id).first()
    db.session.delete(cardapio)
    db.session.commit()

    return redirect("/cadastros")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user = User()
        user.name = request.form["name"]
        user.email = request.form["email"]
        user.password = generate_password_hash(request.form["password"])
        user.celular = request.form["celular"]
        user.cargo = request.form["cargo"]

        db.session.add(user)
        db.session.commit()

        return redirect(url_for("cadastros"))

    return render_template("cadastros.html")

@app.route("/register_cardapio", methods=["GET", "POST"])
def registerCardapio():
    if request.method == "POST":
        cardapio = Cardapio()
        cardapio.nome = request.form["nome"]
        cardapio.tipo = request.form["tipo"]
        cardapio.valor = request.form["valor"]
        cardapio.descricao = request.form["descricao"]  
        file = request.files['thumb']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            cardapio.thumb = filename
            #print('upload_image filename: ' + filename)
            flash('Upload realizado com sucesso')
        else:
            flash('Apenas permitimos os seguintes formatos: png, jpg, jpeg, gif')
            return redirect(request.url)

        db.session.add(cardapio)
        db.session.commit()

        return redirect(url_for("cadastros"))

    return render_template("cadastros.html")    

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"] 

        user = User.query.filter_by(email=email).first()

        if not user:
            flash("Credênciais incorretas")
            return redirect(url_for("login"))

        if not check_password_hash(user.password, password):
            flash("Credênciais incorretas")
            return redirect(url_for("login"))

        login_user(user)
        return redirect(url_for("pedidos"))

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)