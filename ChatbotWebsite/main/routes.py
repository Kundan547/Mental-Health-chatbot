from flask import render_template, Blueprint
from flask_login import current_user, login_required

main = Blueprint("main", __name__)

# Home Page
@main.route("/")
def home():
    return render_template("home.html", title="Mental Health Chatbot")

# About Page
@main.route("/about")
def about():
    return render_template("about.html", title="About")

# SOS Page
@main.route("/sos")
def sos():
    return render_template("sos.html", title="SOS")

# Journal Page (Restricted to logged-in users)
@main.route("/journal")
@login_required  # Ensures only logged-in users can access the journal
def journal():
    return render_template("journal.html", title="Journal", user=current_user)
