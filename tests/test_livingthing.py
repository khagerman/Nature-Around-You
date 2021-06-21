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


class LivingThingTesting(TestCase):
    """Tests for livingthing"""

    def setUp(self):
        """Add sample user"""

        User.query.delete()

        user = User.register("TestingIsFun", "cookies")

        db.session.add(user)
        db.session.commit()
        self.id = user.id
        self.user = user

    def tearDown(self):

        res = super().tearDown()
        db.session.rollback()
        return res

    def test_save_livingthing(self):
        """Test adding living thing to db"""
        new_living_thing = LivingThing(
            nature_id=1223,
            name="Ptilopachus",
            image_url="https://inaturalist-open-data.s3.amazonaws.com/photos/2439655/square.jpg?1443360341",
        )
        db.session.add(new_living_thing)
        db.session.commit()
        self.assertTrue(new_living_thing.nature_id == 1223)

    def test_user_living_thing(self):
        """test user saving living thing"""
        another_new_living_thing = LivingThing(
            id=67,
            nature_id=12,
            name="cat",
            image_url="www.cat.com",
        )
        user = self.user
        db.session.add(another_new_living_thing)
        db.session.commit()
        user_living_thing = UserLivingThing(user_id=user.id, living_thing_id=67)
        db.session.add(user_living_thing)
        db.session.commit()
        self.assertIsNotNone(user.living_things)
