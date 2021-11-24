from datetime import timedelta
from flask import Flask, render_template, redirect, request, url_for, flash, session, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash 
from werkzeug.utils import secure_filename
import urllib.request
import os
import random

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
    promocional = db.Column(db.DECIMAL(10,2))
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

class Banner(db.Model):
    __tablename__ = "banners"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(45), nullable=False)
    image = db.Column(db.Unicode(124), nullable=False)
    link = db.Column(db.String(255))
    status = db.Column(db.Integer, default=True)
    priority = db.Column(db.Boolean, default=False, nullable=False)

    def __str__(self):
        return self.nome

class Pedido(db.Model):
    __tablename__ = "pedidos"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    numero_pedido = db.Column(db.String(86), nullable=False)
    nome = db.Column(db.String(86), nullable=False)
    telefone = db.Column(db.String(12), nullable=False)
    email = db.Column(db.String(86), nullable=False)
    cpf = db.Column(db.String(255), nullable=False)
    endereco = db.Column(db.String(255), nullable=False)
    tipo = db.Column(db.String(45), nullable=False)
    subtotal = db.Column(db.DECIMAL(10,2), nullable=False)
    total = db.Column(db.DECIMAL(10,2), nullable=False)
    status = db.Column(db.String(25), nullable=False)
    metodoPagamento = db.Column(db.String(25), nullable=False)

    def __str__(self):
        return self.id

class item_pedido(db.Model):
    __tablename__ = "itens_pedidos"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_item = db.Column(db.Integer, nullable=False)
    nmr_pedido = db.Column(db.String(25), nullable=False)

@app.route("/")
def index():
    users = User.query.all() # Select * from users; 
    cardapios = Cardapio.query.all()
    banners = Banner.query.all()
    active_banners = []
    for banner in banners:
        if banner.status == 1:
            active_banners.append(banner)
    nmr_banners_ativos = len(active_banners)

    return render_template("index.html", users=users, cardapios=cardapios, banners=banners, nmr_banners_ativos=nmr_banners_ativos)

@app.route('/cart/', methods=['POST', 'GET'])
@app.route('/cart/<int:id>', methods=['POST', 'GET'])
def carrinho(id=0):
    if id == 0:
        if 'carrinho' not in session:
            cartlist = []
            valorTotal = 0
            session['carrinho'] = {'items':cartlist, 'total':valorTotal}
        metacart = session['carrinho']
        lista = session['carrinho']['items']
        cart = []
        if len(lista) == 0:
            flash('Ops! Seu carrinho esta vazio.')
            return render_template("carrinho.html")
        for i in lista:
            item_id = Cardapio.query.filter_by(id=i) 
            item_id = Cardapio.query.filter_by(id=i).first()
            item = item_id
            cart.append(item) 
        return render_template('carrinho.html', cart=cart, total=session['carrinho']['total']) 
    if 'carrinho' in session:  
        cartlist = session['carrinho']['items']
        cartlist.append(id)
        lista = cartlist
        cart = []
        valores = []
        for i in lista:
            item_id = Cardapio.query.filter_by(id=i) 
            item_id = Cardapio.query.filter_by(id=i).first()
            item = item_id
            if item.promocional:
                valores.append(item.promocional)
            else:
                valores.append(item.valor)
            cart.append(item) 
        valorTotal = float(sum(valores))
        session['carrinho'] = {'items':cartlist, 'total':valorTotal}
    else:
        cartlist = []
        cartlist.append(id)
        lista = cartlist
        cart = []
        valores = []
        for i in lista:
            item_id = Cardapio.query.filter_by(id=i) 
            item_id = Cardapio.query.filter_by(id=i).first()
            item = item_id
            if item.promocional:
                valores.append(item.promocional)
            else:
                valores.append(item.valor)
            cart.append(item) 
        valorTotal = float(sum(valores))
        session['carrinho'] = {'items':cartlist, 'total':valorTotal}# setting session data
    return "Carrinho: {}".format(session.get('carrinho'))

@app.route('/delete-cart/<int:id>')
def delete_cart_item(id):
    cartlist = session['carrinho']['items']
    cartlist.remove(id)
    lista = cartlist
    cart = []
    valores = []
    for i in lista:
        item_id = Cardapio.query.filter_by(id=i) 
        item_id = Cardapio.query.filter_by(id=i).first()
        item = item_id
        valores.append(item.valor)
        cart.append(item) 
    valorTotal = float(sum(valores))
    session['carrinho'] = {'items':cartlist, 'total':valorTotal} # delete cart 
    return render_template('carrinho.html', cart=cart, total=session['carrinho']['total']) 



@app.route('/delete-cart/')
def delete_visits():
    cartlist = []
    valorTotal = 0
    session['carrinho'] = {'items':cartlist, 'total':valorTotal} # delete cart
    flash('Você esvaziou seu carrinho.')
    return redirect('/cart')

@app.route("/cadastros/<tab>")
@app.route("/cadastros")
@login_required
def cadastros(tab='funcionarios'):
    users = User.query.all() # Select * from users; 
    cardapios = Cardapio.query.all() # Select * from users;  
    return render_template("cadastros.html", users=users, cardapios=cardapios, tab=tab)

    
    
@app.route("/banners")
@login_required
def banners(): 
    banners = Banner.query.all() # Select * from users;  
    return render_template("banners.html", banners=banners)


@app.route("/pedidos")
@login_required
def pedidos():
    users = User.query.all() # Select * from users; 
    return render_template("paginapedidos.html", users=users)    

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

@app.route("/deletebanner/<int:id>")
def deletebanner(id):
    banner = Banner.query.filter_by(id=id).first()
    db.session.delete(banner)
    db.session.commit()
    return redirect("/banners")


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

@app.route("/novobanner", methods=["GET", "POST"])
def novobanner():
    if request.method == "POST":
        img = Banner()
        img.nome = request.form['nome']
        img.link = request.form['link']
        img.status = request.form['status']
        file = request.files['img']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            img.image = filename
            #print('upload_image filename: ' + filename)
            flash('Upload realizado com sucesso')
        else:
            flash('Apenas permitimos os seguintes formatos: png, jpg, jpeg, gif')
            return redirect(request.url)
        
        db.session.add(img)
        db.session.commit()
    return render_template("novo-banner.html")

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

@app.route("/atualizar_cardapio/<int:id>", methods=["GET", "POST"])
def atualizarcardapio(id):
    item = Cardapio.query.filter_by(id=id).first()

    return render_template("atualizar-produto.html", item=item) 

@app.route("/update_banner/<int:id>", methods=["GET"])
def atualizabanner(id):
    item = Banner.query.filter_by(id=id).first()
    if item.status == 1:
        Banner.query.filter_by(id=id).update(dict(status=0))
    else:
        Banner.query.filter_by(id=id).update(dict(status=1))
    db.session.flush()
    db.session.commit()
    return redirect('/banners')

@app.route("/update_cardapio/<int:id>", methods=["POST"])
def updatecardapio(id):
    item = Cardapio.query.filter_by(id=id).first()
    if request.method == "POST": 
        cardapio = Cardapio()
        cardapio.id = id
        cardapio.nome = request.form["nome"] 
        #cardapio = Cardapio.query.filter_by(id=id).update(dict(nome=cardapio.nome))
        cardapio.valor = request.form["valor"]
        cardapio.promocional = request.form["promocional"]
        cardapio.descricao = request.form["descricao"]
        if request.files['thumb'].filename != '':
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
            Cardapio.query.filter_by(id=id).update(dict(thumb=cardapio.thumb))   

        Cardapio.query.filter_by(id=id).update(dict(nome=cardapio.nome))
        Cardapio.query.filter_by(id=id).update(dict(valor=cardapio.valor)) 
        Cardapio.query.filter_by(id=id).update(dict(promocional=cardapio.promocional)) 
        Cardapio.query.filter_by(id=id).update(dict(descricao=cardapio.descricao)) 
        db.session.flush()
        db.session.commit()
        return redirect(url_for("cadastros", tab='produtos'))


@app.route("/atualizar_funcionario/<int:id>", methods=["GET", "POST"])
def atualizarfuncionario(id):
    funcionario = User.query.filter_by(id=id).first()

    return render_template("atualizar-funcionario.html", funcionario=funcionario) 

@app.route("/update_funcionario/<int:id>", methods=["POST"])
def updatefuncionario(id):
    funcionario = User.query.filter_by(id=id).first()
    if request.method == "POST": 
        user = User()
        user.id = id
        if request.form["name"] != funcionario.name:
            old_name = funcionario.name
            user.name = request.form["name"]  
            User.query.filter_by(id=id).update(dict(name=user.name))
            msg = 'Nome de ' + old_name + ' alterado para ' + request.form["name"]
            flash(msg)

        if request.form["email"] != funcionario.email:
            user.email = request.form["email"]  
            User.query.filter_by(id=id).update(dict(email=user.email))
            msg = 'Email de ' + request.form["name"] + ' alterado com sucesso!'
            flash(msg) 

        if request.form["celular"] != funcionario.celular:
            user.celular = request.form["celular"] 
            User.query.filter_by(id=id).update(dict(celular=user.celular))
            msg = 'Celular de ' + request.form["name"] + ' alterado com sucesso!'
            flash(msg) 

        if request.form["cargo"] != funcionario.cargo:
            user.cargo = request.form["cargo"] 
            User.query.filter_by(id=id).update(dict(cargo=user.cargo))
            msg = 'Cargo de ' + request.form["name"] + ' alterado para ' + request.form["cargo"]
            flash(msg)

        if request.form["password"] != '':
            if request.form["password"] == request.form["confirmacao"]:
                user.password = generate_password_hash(request.form["password"]) 
                User.query.filter_by(id=id).update(dict(password=user.password))
                msg = 'Senha de ' + request.form["name"] + ' alterada com sucesso!'
                flash(msg) 
            else:
                flash("Assegure-se de que os campos Senha e Confirmar senha coincidem exatamente.")
                return redirect(url_for("atualizarfuncionario", id=id))
        
        #problema ao atualizar o cargo!!! 

        db.session.flush()
        db.session.commit()
        return redirect(url_for("cadastros", tab='funcionarios'))

        

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

@app.route("/checkout") 
def checkout(): 
    metacart = session['carrinho']
    lista = session['carrinho']['items']
    cart = []
    if len(lista) == 0:
        flash('Ops! Seu carrinho esta vazio.')
        return render_template("carrinho.html")
    for i in lista:
        item_id = Cardapio.query.filter_by(id=i) 
        item_id = Cardapio.query.filter_by(id=i).first()
        item = item_id
        cart.append(item) 
    return render_template('checkout.html', cart=cart, total=session['carrinho']['total']) 

@app.route("/checkout/entrega") 
def entrega(): 
    metacart = session['carrinho']
    lista = session['carrinho']['items']
    cart = []
    taxaDeEntrega = 5
    if len(lista) == 0:
        flash('Ops! Seu carrinho esta vazio.')
        return render_template("carrinho.html")
    for i in lista:
        item_id = Cardapio.query.filter_by(id=i) 
        item_id = Cardapio.query.filter_by(id=i).first()
        item = item_id
        cart.append(item) 
    return render_template('entrega.html', cart=cart, subtotal=session['carrinho']['total'], total=session['carrinho']['total']+taxaDeEntrega, taxaDeEntrega=taxaDeEntrega)


@app.route("/checkout/retirar") 
def retirar(): 
    metacart = session['carrinho']
    lista = session['carrinho']['items']
    cart = []
    #taxaDeEntrega = 5
    if len(lista) == 0:
        flash('Ops! Seu carrinho esta vazio.')
        return render_template("carrinho.html")
    for i in lista:
        item_id = Cardapio.query.filter_by(id=i) 
        item_id = Cardapio.query.filter_by(id=i).first()
        item = item_id
        cart.append(item) 
    return render_template('retirar.html', cart=cart, subtotal=session['carrinho']['total'], total=session['carrinho']['total'])

@app.route("/finalizarpedido", methods=["POST"]) 
def finalizarpedido(): 
    if request.method == 'POST':
        numeroDoPedido = random.randint(1486,9999)
        metacart = session['carrinho']
        lista = session['carrinho']['items']
        cart = []
        if len(lista) == 0:
            flash('Ops! Seu carrinho esta vazio.')
            return render_template("carrinho.html")
        for i in lista:
            item_id = Cardapio.query.filter_by(id=i) 
            item_id = Cardapio.query.filter_by(id=i).first()
            item = item_id
            cart.append(item) 
            itempedido = item_pedido()
            itempedido.id_item = item.id
            itempedido.nmr_pedido =  numeroDoPedido
            db.session.add(itempedido)
            db.session.commit()
        if request.form["tipo"] == 'entrega':
            endereco = "{}, {}, {}, {} - {}, {}".format(request.form["rua"],request.form["numero"], request.form["bairro"],request.form["cidade"],request.form["uf"],request.form["cep"])
        else:
             endereco = "não aplicável"
        pedido = Pedido()
        pedido.numero_pedido = numeroDoPedido
        pedido.nome = request.form["nome"]
        if request.form["tipo"] == 'entrega':
            pedido.telefone = request.form["celular"]
            pedido.email = request.form["email"]
        else:
            pedido.telefone = 'não aplicável'
            pedido.email = 'não aplicável'
        pedido.cpf = request.form["cpf"]
        pedido.endereco = endereco
        pedido.tipo = request.form["tipo"]
        pedido.subtotal = request.form["subtotal"]
        pedido.total = request.form["total"]
        pedido.status = 'pendente'
        pedido.metodoPagamento = request.form["metodoPgto"]
        db.session.add(pedido)
        db.session.commit()
    return render_template('finalizarpedido.html', cart=cart, subtotal=session['carrinho']['total'], total=session['carrinho']['total']+5, tipo = pedido.tipo,metodoPgto=pedido.metodoPagamento, endereco=pedido.endereco, numero = pedido.numero_pedido)  

if __name__ == "__main__":
    app.run(debug=True)