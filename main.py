from googletrans import Translator
from flask import Flask,render_template,redirect,request,url_for,jsonify, session
from dictionary import language_codes
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, SelectField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
from flask_bcrypt import Bcrypt
app=Flask(__name__)
bootstrap = Bootstrap5(app)
app.config['SECRET_KEY'] = 'AlooPaloo'
translator = Translator()



class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///userinfo.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

class UserInfo(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(250), nullable=False)

choice_list = [key for key in language_codes.keys()]
class TranslateLanguage(FlaskForm):
    
    source_language = SelectField(label="Enter your language", choices=choice_list,  validators=[DataRequired()])
    text = StringField(label = "Enter text", validators=[DataRequired()])
    destination_language = SelectField(label="Enter Destination Language", choices=choice_list,  validators=[DataRequired()])
    converted_text = StringField(label = "Converted text", validators=[DataRequired()])
    add = SubmitField(label="Add Language")
    submit = SubmitField(label="Submit")

class LoginForm(FlaskForm):
    email = StringField(label='Email', validators=[DataRequired()])
    username = StringField(label='Username', validators=[DataRequired()])
    password = StringField(label='Password', validators=[DataRequired()])
    submit = SubmitField(label="Log In")

class RegisterForm(FlaskForm):
    email = StringField(label='Email', validators=[DataRequired()])
    username = StringField(label='Username', validators=[DataRequired()])
    password = StringField(label='Password', validators=[DataRequired()])
    confirm_password = StringField(label='Confirm Password', validators=[DataRequired()])
    submit = SubmitField(label="Register")

with app.app_context():
    db.create_all()


current_user = {
    "email":"",
    "username":"",
    "password":"",
}


@app.route('/translate', methods=['GET', 'POST'])
def translate():
    translate_form = TranslateLanguage()
    if request.method == 'POST':
        source = request.form['source_language']
        text = request.form['text']
        destination = request.form['destination_language']
        translation = translator.translate(text, src=language_codes[source], dest=language_codes[destination])
        return jsonify({'data': translation.text})
    return render_template("translate.html", form2=translate_form, bootstrap=bootstrap)

@app.route('/login', methods=['GET', 'POST'])
def login():
     login_form = LoginForm()
     if request.method == 'POST':
        entered_username = login_form.username.data
        entered_password = login_form.password.data
        user = UserInfo.query.filter_by(username=entered_username).first()
        print("Stored Password:",user.password)
        print("Entered Password:", entered_password)
        if user:
            stored_password = user.password
            if stored_password == entered_password:
                current_user["email"] = user.email
                current_user["username"] = user.username
                current_user["password"] = user.password
                session['logged_in'] = True
                return redirect(url_for('translate'))
            else:
                return "Invalid Password"
        else:
            return "Oops User not found please register"
     return render_template("login.html", form=login_form, bootstrap=bootstrap)

@app.route('/login_status')
def login_status():
    return jsonify({'logged_in': session.get('logged_in', False)})

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session['logged_in'] = False
    return redirect(url_for('home'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    register_form = RegisterForm()
    lgf = LoginForm()
    if request.method == 'POST':
        current_user["email"] = register_form.email.data
        current_user["username"] = register_form.username.data
        current_user["password"] = register_form.password.data
        with app.app_context():
            info = UserInfo(
                    email = register_form.email.data,
                    username=register_form.username.data,
                    password=register_form.password.data)
            db.session.add(info)
            db.session.commit()
        return redirect(url_for('login'))
    if request.method == 'GET':
        return render_template("signup.html", form1=register_form, bootstrap=bootstrap)

@app.route("/")
def home():
    return render_template('index.html', bootstrap=bootstrap)

if __name__ == '__main__':
    app.run(debug=True, port=3002)

