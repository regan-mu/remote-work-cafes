from flask import Flask, render_template, flash, request, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from forms import Comments, Login, Register, Rating, Cafes
from flask_gravatar import Gravatar
from flask_login import LoginManager, login_required, login_user, current_user, logout_user
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config['SECRET_KEY'] = '7b467666ba4153806eafc2c02ea33a795e291820'
# Bootstrap
bootstrap = Bootstrap(app)

# Gravatar
gravatar = Gravatar(app, rating='g', default='retro',
                    force_default=False, force_lower=False, use_ssl=False, base_url=None)

# Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# DataBase
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# DB Model - To be transferred to a separate file after making project a package
@login_manager.user_loader
def load_user(id):
    return User.query.get(id)


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    join_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    password = db.Column(db.String(200), nullable=False)
    cafes = db.relationship('Cafe', backref='user', lazy=True)

    def __repr__(self):
        return f"User({self.name}, {self.email})"


class Cafe(db.Model):
    __tablename__ = "cafes"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    map_link = db.Column(db.String(200), nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    wifi = db.Column(db.String(6), nullable=False)
    power = db.Column(db.String(6), nullable=False)
    coffee = db.Column(db.String(6), nullable=False)
    opening = db.Column(db.Time, nullable=False)
    closing = db.Column(db.Time, nullable=False)
    description = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, default=0, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    comments = db.relationship('Comment', backref='cafe', lazy=True)
    ratings = db.relationship('CafeRating', backref='cafe', lazy=True)

    def __repr__(self):
        return f"Cafe({self.name}, {self.location})"


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    body = db.Column(db.Text, nullable=False)
    cafe_id = db.Column(db.Integer, db.ForeignKey('cafes.id'))

    def __repr__(self):
        return f"Cafe({self.name}, {self.date_posted})"


class CafeRating(db.Model):
    __tablename__ = "caferatings"
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    cafe_id = db.Column(db.Integer, db.ForeignKey('cafes.id'))

    def __repr__(self):
        return f"CafeRating({self.rating}, {self.cafe_id})"
# END DB Models


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = Login()
    if current_user.is_authenticated:
        return redirect(url_for('all_cafes'))
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash('Logged in successfully.', 'success')
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('all_cafes'))
            else:
                flash('Wrong Password', 'danger')
        else:
            flash("Email doesn't exist", "danger")
            return redirect(url_for('register'))

    return render_template('login.html', form=form)


@app.route('/register', methods=['POST', 'GET'])
def register():
    form = Register()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(
            name=form.name.data,
            email=form.email.data,
            password=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        flash('Registration Successful', 'success')
        return redirect(url_for('all_cafes'))
    return render_template('registration.html', form=form)


@app.route('/rating/<int:cafe_id>', methods=['POST', 'GET'])
def rating(cafe_id):
    form = Rating()
    if form.validate_on_submit():
        rate = CafeRating(
            rating=form.rating.data,
            cafe_id=cafe_id
        )
        db.session.add(rate)
        db.session.commit()
        # Populate all the ratings for that cafe and get their average
        # Use that average to update the rating column for the cafe
        cafe = Cafe.query.get(cafe_id)
        all_ratings = cafe.ratings
        avg_ratings = round(sum([rate.rating for rate in all_ratings])/len(all_ratings))
        cafe.rating = avg_ratings
        db.session.commit()
        flash('Rating Added!', 'success')
        return redirect(url_for('cafe_profile', cafe_id=cafe_id))
    return render_template('rating.html', form=form)


@app.route('/add-cafe', methods=["POST", "GET"])
@login_required
def add_cafe():
    form = Cafes()
    form_role = "Add New Cafe"
    if form.validate_on_submit():
        cafe = Cafe(
            name=form.name.data,
            location=form.location.data,
            map_link=form.map_link.data,
            image_url=form.image_url.data,
            wifi=form.wifi.data,
            power=form.power.data,
            coffee=form.coffee.data,
            opening=form.opening.data,
            closing=form.closing.data,
            description=form.description.data,
            user_id=current_user.id
        )
        db.session.add(cafe)
        db.session.commit()
        flash('Cafe added!', 'success')
        return redirect(url_for('all_cafes'))
    return render_template('add.html', form=form, form_role=form_role)


@app.route("/cafes")
def all_cafes():
    cafes = Cafe.query.order_by(Cafe.rating.desc()).all()
    return render_template('all_cafes.html', cafes=cafes)


@app.route("/profile/<int:cafe_id>", methods=['POST', 'GET'])
def cafe_profile(cafe_id):
    form = Comments()
    comments = Comment.query.filter_by(cafe_id=cafe_id).order_by(Comment.date_posted.desc())
    cafe = Cafe.query.get(cafe_id)
    all_cafe_ratings = CafeRating.query.filter_by(cafe_id=cafe_id).all()
    ratings_list = [rate.rating for rate in all_cafe_ratings]
    rating_avg = 0
    if ratings_list:
        rating_avg = round(sum(ratings_list) / len(ratings_list))
    if form.validate_on_submit():
        comment = Comment(
            name=form.name.data,
            body=form.text.data,
            cafe_id=cafe_id
        )
        db.session.add(comment)
        db.session.commit()
        flash('Comment Saved!', 'success')
        return redirect(url_for('cafe_profile', cafe_id=cafe_id))
    return render_template('cafe_profile.html', form=form, cafe=cafe, comments=comments, ratings=rating_avg)


@app.route('/edit/<int:cafe_id>', methods=['POST', 'GET'])
@login_required
def edit(cafe_id):
    form = Cafes()
    cafe = Cafe.query.get(cafe_id)
    form_role = f"Edit {cafe.name}"
    if request.method == 'GET':
        form.name.data = cafe.name
        form.location.data = cafe.location
        form.map_link.data = cafe.map_link
        form.image_url.data = cafe.image_url
        form.coffee.data = cafe.coffee
        form.wifi.data = cafe.wifi
        form.power.data = cafe.power
        form.opening.data = cafe.opening
        form.closing.data = cafe.closing
        form.description.data = cafe.description
    elif form.validate_on_submit():
        cafe.name = form.name.data
        cafe.location = form.location.data
        cafe.map_link = form.map_link.data
        cafe.image_url = form.image_url.data
        cafe.coffee = form.coffee.data
        cafe.wifi = form.wifi.data
        cafe.power = form.power.data
        cafe.opening = form.opening.data
        cafe.closing = form.closing.data
        cafe.description = form.description.data
        db.session.commit()
        flash('Cafe Updated', 'success')
        return redirect(url_for('cafe_profile', cafe_id=cafe_id))
    return render_template('add.html', form=form, form_role=form_role)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('all_cafes'))


if __name__ == "__main__":
    app.run(debug=True)
