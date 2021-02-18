from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, escape, abort, flash
from forms import LoginUser, PostForm, RegisterUser, TokenUser, ChangePassword
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from hashlib import sha256


# TAREA 1: Añadir atributos, características y funcionalidades extras al sitio
# TAREA 2: Pulir y corregir detalles que hayan en el codigo.


app = Flask(__name__)

# Configuraciones generales de la app
app.config['SECRET_KEY'] = '819cb36b0994a6d14e1ee16ca6d31e0abf0e92586e1fcda7d3310d58f5e7dae3cd8177ca8bc57b6cbd4349a8273a1be977b9f70e183b7c39cf04c0a854144620'
app.config['WTF_CSRF_SECRET_KEY'] = '6cab0b8ff2de3ecc1c64e4e9cea8dc749d5ab8ad518ec72b193b8e92735e62e19a273724f3980d9672157bec384c4af9504baa3f0a6cf33ed8f36b0e76c815f2'

app.config['RECAPTCHA_PUBLIC_KEY'] = ''
app.config['RECAPTCHA_PRIVATE_KEY'] = ''

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/DLine.db'

# Protección contra CSRF
csrf = CSRFProtect(app)

# BBDD, Cursor y Módelos
db = SQLAlchemy(app)
from models import User, Post


############################################################################################################

# VISTAS DE LA APP


def user_in_session():
    if 'username' in session and 'password' in session and 'id' in session:
        return True
    else:
        return False


# Inicio -> Se muestran publicaciones de todos los usuarios
@app.route('/')
def index():
    username = None
    if user_in_session():
        username = escape(session['username'])

    return render_template('index.html', username=username)

def coincidence_user_post(post_user_id):
    query_user = User.query.filter_by(id=post_user_id).first()
    if query_user is not None:
        return query_user.username
    else:
        return'Anonymous'

# Vista de posts publicos para todos
@app.route('/public-posts')
def public_posts():
    # Enlace entre tabla User y Post

    posts = Post.query.filter_by(public=1).order_by(Post.id.desc()).all()

    return render_template('public_posts.html', posts=posts, coincidence_user_post=coincidence_user_post)

# VALIDADORES PARA REGISTRO DE USUARIOS

# Validador de cuenta email
def validate_email(email):
    query = User.query.filter_by(email=email).first()
    if query is None:
        return False
    else:
        return True

# Validador de nombre de usuario
def validate_username(username):
    query = User.query.filter_by(username=username).first()
    if query is None:
        return False
    else:
        return True


############################################################################################################

# VISTA DE REGISTRO DE USUARIOS 

# Registro de usuarios -> Funciona correctamente
@app.route('/auth/register', methods=['GET', 'POST'])
def register():
    if not user_in_session():
        form = RegisterUser()
        error = None

        if form.validate_on_submit() and request.method == 'POST':
            email = form.email.data

            if not validate_email(email):
                username = form.username.data
                
                if not validate_username(username):       
                    password = sha256((form.password.data).encode())
                    password_confirm = sha256((form.password_confirm.data).encode())

                    if password.hexdigest() == password_confirm.hexdigest():
                        name = form.name.data
                        age = form.age.data


                        user = User(
                            name=name, 
                            age=age, 
                            email=email, 
                            username=username, 
                            password=password.hexdigest(),
                            created_at=datetime.now().date()
                        )
                        db.session.add(user)
                        db.session.commit()
                        
                        flash('Your account has been created successfully!')

                        return redirect(url_for('login'))
                    
                    else:
                        error = 'Passwords no match!'

                else:
                    error = 'Username already exist!'

            else:
                error = 'Email already exist!'

        return render_template('auth/register.html', form=form, error=error)
    
    else:
        abort(404)


############################################################################################################


# VISTA DE INICIO DE SESION

# Inicio de sesión -> Funciona correctamente
@app.route('/auth/login', methods=['GET', 'POST'])
def login():
    if not 'username' in session and not 'password' in session and not 'id' in session:
        form = LoginUser()
        error = None
        if form.validate_on_submit() and request.method == 'POST':
            username = form.username.data
            query = User.query.filter_by(username=username).first()

            if query is not None and query.username==username:
                password = sha256((form.password.data).encode())

                if query.password == password.hexdigest():
                    session['id'] = query.id
                    session['username'] = username
                    session['password'] = password.hexdigest()
                    return redirect(url_for('index'))
                else:
                    error = 'Username and/or password incorrect'
            else:
                error = 'Username and/or password incorrect'

        return render_template('auth/login.html', form=form, error=error)

    else:
        abort(404)

############################################################################################################

# VISTAS DE OPCIONES PARA EL USUARIO

# Cuenta de usuario -> Funciona correctamente
@app.route('/auth/session-started/profile')
def profile():
    if user_in_session():
        query = User.query.filter_by(id=session['id']).first()

        return render_template('auth/session-started/profile.html', user={
            'id': query.id,
            'name': query.name,
            'age': query.age,
            'email': query.email,
            'username': query.username,
            'created_at': query.created_at
        })

    else:
        abort(404)

# ----------------------------------------------------------------------------------------------------------

# Clase con métodos de validación para que el usuario pueda editar su perfil y posts
class EditValidator:
    def username_validator(self, actual, new):
        query = User.query.filter_by(username=new).first()
        if query is None:
            return True
        elif actual == query.username and new == query.username:
            return True
        else:
            return False
    def email_validator(self, actual, new):
        query = User.query.filter_by(email=new).first()
        if query is None:
            return True
        elif actual == query.email and new == query.email:
            return True
        else:
            return False

    def title_validator(self, actual_title, new_title):
        query = Post.query.filter_by(title=new_title).first()
        if query is None:
            return True
        elif actual_title == query.title and new_title == query.title:
            return True
        else:
            return False    
    
    def content_validator(self, actual_content, new_content):
        query = Post.query.filter_by(content=new_content).first()
        if query is None:
            return True
        elif actual_content == query.content and new_content == query.content:
            return True
        else:
            return False            

# Editar datos de perfil -> Funciona correctamente
@app.route('/auth/session-started/edit-profile/<int:id>', methods=['GET', 'POST'])
def edit_profile(id):
    if user_in_session():
        error = None
        update_user = User.query.filter_by(id=int(id)).first()
        token = TokenUser()

        if token.validate_on_submit() and request.method == 'POST':
            # Datos envidados

            edit_data = EditValidator()
            
            username = request.form['username']
            if edit_data.username_validator(actual=update_user.username, new=username):
                print('\nTodo bien hasta aquí\n')

                email = request.form.get('email')
                if edit_data.email_validator(actual=update_user.email, new=email):
                    
                    name = request.form.get('name')
                    age = request.form.get('age')
                    

                    # Actualización de usuario 
                    update_user.name = name
                    update_user.age = age
                    update_user.email = email
                    update_user.username = username
                    
                    db.session.add(update_user)
                    db.session.commit()

                    flash('Your profile has been updated successfully!')
                    
                    return redirect(url_for('profile'))

                else:
                    error = 'Email already exist!'

            else:
                error = 'Username already exist!'

            

        return render_template('auth/session-started/edit_profile.html', token=token, user=update_user, error=error)

    else:
        abort(404)

# ----------------------------------------------------------------------------------------------------------

# Validador de contraseña
def validate_password(username, password):
    query = User.query.filter_by(username=username).first()
    if query is not None and password == query.password:
        return True
    else:
        return False


# Cambiar contraseña
#
# TAREA: Mostrar un mensaje flash cuando el usuario haya cambiado la contraseña 
@app.route('/auth/session-started/change-password/<int:id>', methods=['GET', 'POST'])
def change_password(id):
    if user_in_session():
        error = None
        user = User.query.filter_by(id=int(id)).first()
        form = ChangePassword()

        if form.validate_on_submit() and request.method == 'POST':
            password_user = sha256((form.password_user.data).encode())

            if validate_password(user.username, password_user.hexdigest()):
                new_password = sha256((form.new_password.data).encode())
                confirm_new_password = sha256((form.confirm_new_password.data).encode())

                if new_password.hexdigest() == confirm_new_password.hexdigest():
                    user.password = new_password.hexdigest()
                    db.session.add(user)
                    db.session.commit()

                    flash('Your password has been changed successfuly!')

                    return redirect(url_for('profile'))

                else:
                    error = 'New passwords no match!'
            else:
                error = 'Incorrect actual password'

        return render_template('auth/session-started/change_password.html', form=form, error=error)

    else:
        abort(404)

# ----------------------------------------------------------------------------------------------------------

# Cierre de sesión -> Funciona correctamente
@app.route('/auth/logout')
def logout():
    if user_in_session():
        session.pop('username', None)
        session.pop('password', None)
        session.pop('id', None)
        return redirect(url_for('index'))
    else:
        abort(404)

# ----------------------------------------------------------------------------------------------------------

# Validación de título y contenido del post -> SOLO PARA CREAR POST
def validate_title(title):
    query_title = Post.query.filter_by(title=title).first()

    if query_title is None:
        return True
    else: 
        return False

def validate_content(content):
    query_content = Post.query.filter_by(content=content).first()

    if query_content is None:
        return True
    else: 
        return False


# Creación de post(solo para usuarios registrados)
@app.route('/auth/session-started/posts-user/create-post', methods=['GET', 'POST'])
def create_post():
    if user_in_session():
        form = PostForm()
        error = None

        if form.validate_on_submit() and request.method == 'POST':
            title = form.title.data

            if validate_title(title):
                content = form.content.data

                if validate_content(content):
                    topic = form.topic.data
                    public = form.public.data        

                    if public:
                        public = 1
                    else:
                        public = 0

                    post = Post(user_id=session['id'], title=title, topic=topic, content=content, public=public, created_at=datetime.now().date())
                    db.session.add(post)
                    db.session.commit()

                    flash('Your post has been created successfully!')

                    # La idea es redireccionar a la ventana de post del usuario                    
                    return redirect(url_for('user_posts'))

                else:
                    error = 'Post content already exists!'
            else:
                error = 'Post title already exists!'

        return render_template('auth/session-started/posts-user/create_post.html', form=form, error=error)

    else:
        abort(404)


# Vista de posts de usuario -> Funciona correctamente
@app.route('/auth/session-started/posts-user/user-posts')
def user_posts():
    if user_in_session():
        posts = Post.query.filter_by(user_id=session['id']).order_by(Post.id.desc()).all()

        return render_template('auth/session-started/posts-user/user_posts.html', posts=posts)
    else:
        abort(404)


# Eliminar post de usuario
@app.route('/auth/session-started/posts-user/delete-post/<int:post_id>')
def delete_post(post_id):
    if user_in_session():
        Post.query.filter_by(id=post_id).delete()
        db.session.commit()
        return redirect(url_for('user_posts'))
    else:
        abort(404)


# Cambiar estado de post(Public or Private)
@app.route('/auth/session-started/posts-user/change-public/<int:post_id>')
def change_public(post_id):
    if user_in_session():
        post = Post.query.filter_by(id=post_id).first()
        if post.public == True:
            post.public = False
        elif post.public == False:
            post.public = True

        db.session.add(post)
        db.session.commit()
        
        return redirect(url_for('user_posts'))


# Editar post de usuario
@app.route('/auth/session-started/posts-user/edit-post/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    if user_in_session():
        error = None
        post = Post.query.filter_by(id=post_id).first()
        post_form = PostForm()


        # ERROR: No se hace la petición POST
        if post_form.validate_on_submit() and request.method == 'POST':
            print('\ntodo bien\n')


            edit = EditValidator()


            title = post_form.title.data
            

            if edit.title_validator(post.title, title):
                content = request.form['content']
                if edit.content_validator(post.content, content):
                    topic = post_form.topic.data
                    public = post_form.public.data

                    if public:
                        public = 1
                    elif not public:
                        public = 0

                    post.title = title
                    post.topic = topic
                    post.content = content
                    post.public = public

                    db.session.add(post)
                    db.session.commit()

                    flash('Your has been updated successfully!')

                    return redirect(url_for('user_posts'))
                else:
                    error = 'Post content already exists!'
            else:
                error = 'Post title already exists!'

        return render_template('auth/session-started/posts-user/edit_post.html', post=post_form, post_values=post, error=error)

    else:
        abort(404)
