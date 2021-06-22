from app import app
from models import db, User, LivingThing, UserLivingThing

db.drop_all()
db.create_all()
