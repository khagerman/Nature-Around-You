from unittest import TestCase
from sqlalchemy import exc
from app import app
from models import db, User, LivingThing, UserLivingThing


app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///nature_test"
app.config["SQLALCHEMY_ECHO"] = False


app.config["TESTING"] = True


app.config["DEBUG_TB_HOSTS"] = ["dont-show-debug-toolbar"]

db.drop_all()
db.create_all()


class UserTesting(TestCase):
    """Tests for Users"""

    def setUp(self):
        """Add sample user"""

        User.query.delete()

        user = User.register("TestingIsFun", "cookies")
        db.session.add(user)
        db.session.commit()

        self.id = user.id
        self.user = user

    def tearDown(self):

        db.session.rollback()

    def test_add_user(self):
        with app.test_client() as client:
            """test creation of new user and redirect"""
            new_user = User.register("JaneGoodall", "apes123")
            id = 22
            new_user.id = id
            db.session.commit()
            new_user_test = User.query.get(id)
            self.assertTrue(new_user_test.username == "JaneGoodall")
            self.assertFalse(new_user_test.password == "apes123")
            self.assertTrue(new_user_test.password.index("$2b$") != -1)

    def test_add_bad_user(self):
        with app.test_client() as client:
            """test creation of already used username"""
            User.register("TestingIsFun", "123")
            with self.assertRaises(exc.IntegrityError) as e:
                db.session.commit()

    def test_wrong_password(self):
        with app.test_client() as client:
            """make sure ditects wrong password/username combo"""
            self.assertTrue(User.authenticate("TestingIsFun", "cookies"))
            self.assertFalse(User.authenticate("JaneGoodall", "wrongpassword"))
            self.assertFalse(User.authenticate("TestingIsNotFun", "cookies"))
