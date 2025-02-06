from flask import (
    current_app,
    Blueprint,
    render_template,
    request,
    jsonify,
    url_for,
    flash,
    redirect,
)
from flask_login import login_user, current_user, logout_user, login_required

from ChatbotWebsite import db, bcrypt
from ChatbotWebsite.models import User, ChatMessage, Journal
from ChatbotWebsite.users.forms import (
    RegistrationForm,
    LoginForm,
    UpdateAccountForm,
    RequestResetForm,
    ResetPasswordForm,
)
from ChatbotWebsite.users.utils import save_picture, send_reset_email
import os
import secrets
import jwt

users = Blueprint("users", __name__)

# Helper function to generate a secure token (useful for password reset)
def generate_reset_token(user_id):
    token = jwt.encode({'user_id': user_id}, current_app.config['SECRET_KEY'], algorithm='HS256')
    return token

# register page/route
@users.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        new_user = User(
            username=form.username.data, email=form.email.data, password=hashed_password
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Your account has been created! You are now able to log in.", "success")
        return redirect(url_for("users.login"))
    
    return render_template("register.html", title="Register", form=form)

# login page/route
@users.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash("You have been logged in!", "success")
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("main.home"))
        else:
            flash("Login Unsuccessful. Please check your credentials and try again.", "danger")
    
    return render_template("login.html", title="Login", form=form)

# account page/route
@users.route("/account", methods=["GET", "POST"])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            old_picture = current_user.profile_image
            picture_file = save_picture(form.picture.data)
            current_user.profile_image = picture_file
            if old_picture != "default.jpg":
                os.remove(os.path.join(current_app.root_path, "static/profile_images", old_picture))
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Your account has been updated!", "success")
        return redirect(url_for("users.account"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    
    return render_template("account.html", title="Account", form=form)

# logout route
@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.home"))

# delete conversation route
@users.route("/delete_conversation", methods=["POST"])
@login_required
def delete_conversation():
    messages = ChatMessage.query.filter_by(user_id=current_user.id).all()
    for message in messages:
        db.session.delete(message)
    db.session.commit()
    flash("Your conversation has been deleted!", "success")
    return redirect(url_for("users.account"))

# delete account route
@users.route("/delete_account", methods=["POST"])
@login_required
def delete_account():
    # Delete messages and journals associated with the user
    messages = ChatMessage.query.filter_by(user_id=current_user.id).all()
    for message in messages:
        db.session.delete(message)
    journals = Journal.query.filter_by(user_id=current_user.id).all()
    for journal in journals:
        db.session.delete(journal)
    
    # Delete user
    db.session.delete(current_user)
    db.session.commit()
    flash("Your account has been deleted!", "success")
    return redirect(url_for("users.logout"))

# reset password route to request a password reset token
@users.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_reset_email(user)
            flash("An email has been sent with instructions to reset your password.", "info")
        else:
            flash("No account found with that email. Please check and try again.", "danger")
        return redirect(url_for("users.login"))
    
    return render_template("reset_request.html", title="Reset Password", form=form)

# reset password route to reset password
@users.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    
    try:
        user = User.verify_reset_token(token)
    except jwt.ExpiredSignatureError:
        flash("That token has expired, please request a new one.", "warning")
        return redirect(url_for("users.reset_request"))
    
    if user is None:
        flash("That is an invalid or expired token", "warning")
        return redirect(url_for("users.reset_request"))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        if bcrypt.check_password_hash(user.password, form.password.data):
            flash("Your new password must be different from the old password.", "warning")
            return redirect(url_for("users.reset_token", token=token))
        
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user.password = hashed_password
        db.session.commit()
        flash("Your password has been updated!", "success")
        return redirect(url_for("users.login"))
    
    return render_template("reset_token.html", title="Reset Password", form=form)
