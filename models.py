from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
db = SQLAlchemy()


class User(db.Model):
    """User"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    living_things = db.relationship("UserLivingThing", backref="user")

    @classmethod
    def register(cls, username, password):
        """Signup a user and hash their password"""

        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode("utf8")
        user = cls(username=username, password=hashed_utf8)

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """validate that user exists and password is correct"""

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False


class LivingThing(db.Model):
    """Living thing (plant or animal)"""

    __tablename__ = "living_things"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nature_id = db.Column(db.Integer, unique=True, nullable=False)
    name = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.Text, nullable=True)


class UserLivingThing(db.Model):
    """relationship between user and the saved living thing"""

    __tablename__ = "users_living_thing"
    __table_args__ = (db.UniqueConstraint("user_id", "living_thing_id"),)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    living_thing_id = db.Column(
        db.Integer, db.ForeignKey("living_things.id"), primary_key=True
    )


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)
