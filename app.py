from flask import Flask, render_template, request, json, jsonify
import requests
from flask_debugtoolbar import DebugToolbarExtension
from secret import SECRET_KEY
import os

MAP_API_BASE_URL = "http://www.mapquestapi.com/geocoding/v1"
NATURE_API_BASE_URL = "https://api.inaturalist.org/v1"

app = Flask(__name__)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = True
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "hellosecret1")

app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
toolbar = DebugToolbarExtension(app)


def get_coords(location):
    res = requests.get(
        f"{MAP_API_BASE_URL}/address", params={"key": SECRET_KEY, "location": location}
    )
    data = res.json()
    lat = data["results"][0]["locations"][0]["latLng"]["lat"]
    lng = data["results"][0]["locations"][0]["latLng"]["lng"]
    coords = {"lat": lat, "lng": lng}
    return coords


# show location name?


def get_results_list(a):
    """Change a list of plants/animals to an easily usable format."""

    res = json.loads(a.text)
    try:
        return res["results"]
    except:
        return False


# return name?
def get_info(coords):
    res = requests.get(
        f"{NATURE_API_BASE_URL}/observations/species_counts?geo=true&photos=true&popular=true&verifiable=true&lat={coords['lat']}&lng={coords['lng']}&radius=32&order=desc&order_by=created_at&quality_grade=research&per_page=200"
    )

    return get_results_list(res)


def get_animal_details(id):
    res = requests.get(f"{NATURE_API_BASE_URL}/taxa/{id}")
    return get_results_list(res)


@app.route("/")
def homepage():
    return render_template("home.html")


@app.route("/results", methods=["GET", "POST"])
def handle_search():
    """handle location and show search results"""

    location = request.args["location"]
    coords = get_coords(location)
    results = get_info(coords)
    return render_template("results.html", results=results)


@app.route("/details/<int:id>", methods=["GET", "POST"])
def view_animal(id):
    """handle location and show search results"""
    id = id
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
