from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, validators
from dotenv import load_dotenv
import os

# Load the env
load_dotenv()

# Init the app
app = Flask(__name__)

app.config['SECRET_KEY'] = os.urandom(24).hex()
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init the database connection
db = SQLAlchemy(app)


# Define User model
class User(db.Model):
    __tablename__='users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    
    # Class constuctor
    def __init__(self, username, first_name, last_name, password, email):
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.password = password
        self.email = email
    
    # Print the User info
    def __repr__(self):
        return f'<User {self.username} with {self.email}>'

# Register Form
class RegistrationForm(FlaskForm):
    username = StringField('Username:', [validators.Length(min=4, max=25)])
    first_name = StringField('First Name:', [validators.Length(min=4, max=25)])
    last_name = StringField('Last Name:', [validators.Length(min=4, max=25)])
    email = StringField('Email:', [validators.Email()])
    password = PasswordField('Password:', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password:')
    submit = SubmitField('Register')

with app.app_context():
    # Create the database tables
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=["GET", "POST"])
def submit():
    if request.method == "POST":
        username = request.form['username']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        password = request.form['password']
        email = request.form['email']
        
        
        user = User(username, first_name, last_name, password, email)
        db.session.add(user)
        db.session.commit()
        
        userResult = db.session.query(User).filter(User.id == 1)
        for result in userResult:
            print(result.username)
            
    return render_template('account_created.html', data = username)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        password = form.password.data

        # Check if the username or email already exists
        existing_user = User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first()
        if existing_user:
            flash('Username or email already exists. Please choose different ones.', 'danger')
        else:
            # Create a new user and add it to the database
            new_user = User(username=username, first_name = first_name, last_name = last_name, email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('index'))

    return render_template('register.html', form=form)
        

# @app.route('/register')
# def register():
#     return render_template('register.html')

if __name__ == "__main__":
    app.run(debug=True)