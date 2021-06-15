from flask import (
    Flask,
    render_template,
    request,
    json,
    jsonify,
    redirect,
    session,
    flash,
)
import requests
from flask_debugtoolbar import DebugToolbarExtension
from secret import SECRET_KEY, secret
from models import db, connect_db, User, LivingThing, UserLivingThing
from sqlalchemy.exc import IntegrityError
from forms import UserForm, LoginForm

MAP_API_BASE_URL = "http://www.mapquestapi.com/geocoding/v1"
NATURE_API_BASE_URL = "https://api.inaturalist.org/v1"

app = Flask(__name__)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///nature"
app.config["SECRET_KEY"] = secret

app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
toolbar = DebugToolbarExtension(app)

connect_db(app)
db.create_all()


def get_coords(location):
    res = requests.get(
        f"{MAP_API_BASE_URL}/address", params={"key": SECRET_KEY, "location": location}
    )
    data = res.json()
    lat = data["results"][0]["locations"][0]["latLng"]["lat"]
    lng = data["results"][0]["locations"][0]["latLng"]["lng"]
    coords = {"lat": lat, "lng": lng}
    session["coords"] = coords
    return coords


# show location name?


def get_results(data):
    """turn json into python"""

    res = json.loads(data.text)
    return res["results"]


def get_info(coords):
    """Get species based on location"""
    res = requests.get(
        f"{NATURE_API_BASE_URL}/observations/species_counts?geo=true&photos=true&popular=true&verifiable=true&lat={coords['lat']}&lng={coords['lng']}&radius=32&order=desc&order_by=created_at&quality_grade=research&per_page=200"
    )

    return get_results(res)


def get_animal_details(id):
    res = requests.get(f"{NATURE_API_BASE_URL}/taxa/{id}")
    return get_results(res)


@app.route("/")
def homepage():
    return render_template("home.html")


@app.route("/results", methods=["GET", "POST"])
def handle_search():
    """handle location and show search results"""

    location = request.args["location"]
    session["location"] = location
    coords = get_coords(location)
    results = get_info(coords)
    return render_template("results.html", results=results)


@app.route("/details/<int:id>", methods=["GET", "POST"])
def view_animal(id):
    """handle location and show search results"""
    id = id
    session["nature_id"] = id
    classify_info = {"results": []}
    results = get_animal_details(id)
    classifications = results[0]["ancestor_ids"]

    for id in classifications:
        data = get_animal_details(id)
        # name = data["taxon"]["preferred_common_name"]
        # photo = data["taxon_photos"]["small_url"]
        classify_info["results"].append(data)
        # classify_info["photo"] = photo

    return render_template(
        "details.html",
        results=results,
        id=id,
        classifications=classifications,
        classify_info=classify_info,
    )


############login/logout logic######################
@app.route("/register", methods=["GET", "POST"])
def register_user():
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        new_user = User.register(username, password)

        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append("Username taken.  Please pick another")
            return render_template("register.html", form=form)
        session["user_id"] = new_user.id
        flash("Welcome! Successfully Created Your Account!", "success")
        return redirect("/")

    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login_user():
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            flash(f"Welcome Back, {user.username}!", "info")
            session["user_id"] = user.id
            return redirect("/")
        else:
            form.username.errors = ["Invalid username/password."]

    return render_template("login.html", form=form)


@app.route("/logout")
def logout_user():
    session.pop("user_id")
    flash("Goodbye!", "info")
    return redirect("/")


################logic for user adding animal to journal###################


@app.route("/<id>/naturejournal")
def show_saved_animals(id):
    """show users saved plants/animals"""

    if "user_id" not in session:
        flash(f"You do not have permisson to view this page!", "danger")
        return redirect("/login")

    user = User.query.filter_by(id=id).first()
    users_living_things = (
        db.session.query(LivingThing)
        .join(UserLivingThing)
        .filter(LivingThing.id == UserLivingThing.living_thing_id)
        .filter(UserLivingThing.user_id == user.id)
        .all()
    )
    return render_template(
        "naturejournal.html", user=user, users_living_things=users_living_things
    )


# def is_saved_by_user(living_thing):
#     """See if living_thing has been saved"""

#     is_saved = (
#         db.session.query(UserLivingThing)
#         .filter(int(LivingThing.nature_id) == int(living_thing[0]["id"]))
#         .filter(UserLivingThing.user_id == session["user_id"])
#         .first()
#     )
#     if is_saved:
#         return True
#     return False


def in_database(living_thing_entered):
    """Check if animal has been saved to db before"""

    data = LivingThing.query.filter(
        (LivingThing.nature_id) == str(living_thing_entered[0]["id"])
    ).one_or_none()
    if data == None:
        new_living_thing = LivingThing(
            nature_id=living_thing_entered[0]["id"],
            name=living_thing_entered[0]["preferred_common_name"],
            image_url=living_thing_entered[0]["taxon_photos"][0]["photo"]["medium_url"],
        )
        db.session.add(new_living_thing)
        db.session.commit()


def show_saved_animals(id):
    """show users saved plants/animals"""

    if "user_id" not in session:
        flash(f"You do not have permisson to view this page!", "danger")
        return redirect("/login")

    user = User.query.filter_by(id=id).first()
    return render_template("naturejournal.html", user=user)


@app.route("/<int:user_id>/save/<int:nature_id>", methods=["GET", "POST"])
def save_animal(user_id, nature_id):
    """save animal to user's nature journal"""
    if "user_id" not in session:
        flash(f"Please login to save!", "danger")
        return redirect("/login")
    user = User.query.get_or_404(user_id)
    living_thing = get_animal_details(nature_id)
    in_database(living_thing)
    living_thing_id = (
        db.session.query(LivingThing)
        .filter(LivingThing.nature_id == nature_id)
        .one_or_none()
    )
    save_new = UserLivingThing(user_id=user.id, living_thing_id=living_thing_id.id)
    db.session.add(save_new)
    try:
        db.session.commit()
    except:
        db.session.rollback()
        flash(f"Oops, you already saved this!", "info")
    flash(f"Plant or Animal Added!", "success")
    return redirect(f"/{user_id}/naturejournal")


####simular species#######


@app.route("/similarspecies")
def show_similar():
    nature_id = session["nature_id"]
    return jsonify({"nature_id": nature_id})


############filter##################
