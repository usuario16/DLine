from flask_wtf import FlaskForm
from flask_wtf.html5 import EmailField
from flask_wtf.recaptcha import RecaptchaField
from wtforms.fields import StringField, IntegerField, PasswordField, BooleanField
from wtforms.fields.core import SelectField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired, Length


# Formulario para crear una nueva cuenta en el sitio
class RegisterUser(FlaskForm):
    name = StringField(render_kw={'placeholder':'Name'}, validators=[DataRequired(), Length(min=4, max=15)])
    age = IntegerField(render_kw={'placeholder':'Age'}, validators=[DataRequired()])
    email = EmailField(render_kw={'placeholder':'Email'}, validators=[DataRequired(), Length(min=12, max=45)])
    username = StringField(render_kw={'placeholder':'Username'}, validators=[DataRequired(), Length(min=4, max=30)])
    password = PasswordField(render_kw={'placeholder':'Password'}, validators=[DataRequired(), Length(min=8, max=20)])
    password_confirm = PasswordField(render_kw={'placeholder':'Confirm password'}, validators=[DataRequired(), Length(min=8, max=20)])
    recaptcha = RecaptchaField()


# Formulario para iniciar sesión en el sitio
class LoginUser(FlaskForm):
    username = StringField(render_kw={'placeholder':'Username'}, validators=[DataRequired(), Length(min=4, max=14)])
    password = PasswordField(render_kw={'placeholder':'Password'}, validators=[DataRequired(), Length(min=8, max=20)])
    recaptcha = RecaptchaField()


# Token para que el usuario modifique su perfil
class TokenUser(FlaskForm):
    pass


# Formulario para cambiar contraseña
class ChangePassword(FlaskForm):
    password_user = PasswordField(render_kw={'placeholder':'Your password'}, validators=[DataRequired(), Length(min=8, max=20)])
    new_password = PasswordField(render_kw={'placeholder':'New password'}, validators=[DataRequired(), Length(min=8, max=20)])
    confirm_new_password = PasswordField(render_kw={'placeholder':'Confirm your new password'}, validators=[DataRequired(), Length(min=8, max=20)])
    recaptcha = RecaptchaField()


# Formulario para que el usuario pueda crear o módficar un post
class PostForm(FlaskForm):
    title = StringField(render_kw={'placeholder':'Title'}, validators=[DataRequired(), Length(min=8, max=30)])
    topic = SelectField(choices=[
        ('', 'Select a topic'), ('Bussines', 'Bussines'), 
        ('Politics', 'Politics'), ('Technology', 'Technology'), 
        ('Science','Science'), ('History', 'History'),
        ('Languajes', 'Languajes'), ('Books', 'Books'),
        ('Movies', 'Movies'), ('Music', 'Music'), 
        ('Sports', 'Sports'), ('Other', 'Other')
    ], validators=[DataRequired()])
    content = TextAreaField(render_kw={'placeholder':'Content'}, validators=[DataRequired(), Length(min=20, max=550)])
    public = BooleanField()