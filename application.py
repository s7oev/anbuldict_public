import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import requests

from helpers import error, login_required, only_cyr_letters, only_lat_letters, only_anbul_letters, get_word, search_word, add_new_word, add_favorite, remove_favorite, word_in_favorite, get_favorites, delete_word, get_suggestions, admin_review

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
#app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("DATABASE_HERE_(POSTGRESQL_URI_HIDDEN_FOR_SECURITY_REASONS)")

@app.route("/")
def index():
    # Home page
    content = dict()

    """Confirmation alerts to be printed on the homepage"""
    # Login confirmation
    if session.get("loginconfirm_show"):
        content["has_alert"] = True
        content["alert"] = "Successfully logged in!"
        content["alert_type"] = "success"
        session["loginconfirm_show"] = False

    # Word deletion confirmation
    elif session.get("delconfirm_show"):
        content["has_alert"] = True
        content["alert"] = "Word successfully deleted"
        content["alert_type"] = "danger"
        session["delconfirm_show"] = False

    else:
        content["has_alert"] = False

    return render_template("index.html", home_active="active", content=content)


@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""
    username = request.args.get("username")

    valid = 1  # 1: username okay

    # If length is not at least 3 characters, username not valid
    if not username or len(username) < 3:
        return jsonify(2)  # immediate return to catch a theoretical situation where the user visited check by themselves

    # If length is more than 20 characters, username not valid
    if len(username) > 20:
        valid = 3

    # If the username is already taken, it is not valid
    rows = db.execute("SELECT * FROM users WHERE username = :username",
                      username=username)

    if len(rows) == 1:
        valid = 4

    return jsonify(valid)


@app.route("/exsearch", methods=["GET", "POST"])
def exsearch():
    # More advanced search queries
    userid = session.get("user_id")
    content = dict()

    # On extended search form submission
    if request.method == "POST":
        lang = request.form.get("lang")
        method = request.form.get("method")
        term = request.form.get("term")
        all_words = bool(request.form.get("all_words"))

        if not lang:
            return error("Please select a language")

        if method == "contains":
            content["query"] = term
            if lang == "en" and not all_words:  # this is the standard search
                return redirect(url_for('.search', en=term))
            else:
                content["results"] = search_word(lang, term, userid, db, all_words=all_words)

        else:
            content["query"] = term + " (exact)"
            content["results"] = search_word(lang, term, userid, db, contains=False, all_words=all_words)

        # No results on query
        if not content["results"]:
            return render_template("results.html", found_results=False, content=content)

        # Found results on query
        content["total"] = len(content["results"])
        return render_template("results.html", found_results=True, content=content)

        return error("TODO")

    else:
        return render_template("exsearch.html", exsearch_active="active")

@app.route("/favorites", methods=["GET", "POST"])
@login_required
def favorites():
    # List of favorite words
    userid = session.get("user_id")
    content = dict()

    if request.method == "POST":
        wordid = request.form.get("wordid")
        fav_code = int(request.form.get("fav_code"))  # 0: add, 1: remove
        content["has_alert"] = True

        if fav_code == 0:
            add_favorite(userid, wordid, db)
            content["alert"] = "Awesome! You successfully added this word to your favorites!"
            content["alert_type"] = "success"
        else:
            remove_favorite(userid, wordid, db)
            content["alert"] = "Word successfully removed from favorites"
            content["alert_type"] = "danger"

        content["favorites"] = get_favorites(userid, db)
        return render_template("favorites.html", fav_active="active", content=content)

    else:
        content["has_alert"] = False if not request.args.get("alert") else True
        if content["has_alert"]:
            content["alert"] = request.args.get("alert")
            content["alert_type"] = "success" if not request.args.get("alert_type") else request.args.get("alert_type")
        content["favorites"] = get_favorites(userid, db)
        return render_template("favorites.html", fav_active="active", content=content)


@app.route("/login", methods=["GET", "POST"])
def login():
    # Log user in

    # Forget any user_id
    session.clear()

    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return error("Username not provided", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return error("Password not provided", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return error("Invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        session["loginconfirm_show"] = True
        return redirect("/")

    else:
        return render_template("login.html", login_active="active")


@app.route("/logout")
def logout():
    # Log user out

    # Forget any user id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/new_word", methods=["GET", "POST"])
@login_required
def new_word():
    # Adding (admin) or suggesting (regular user) new word
    userid = session.get("user_id")
    content = dict()

    if request.method == "POST":
        suhistdict = request.form.get("suhistdict")
        en = request.form.get("en").lower()
        bg = request.form.get("bg").lower()
        anbul = request.form.get("anbul")

        """Ensure a valid form was sent"""
        # Ensure none of the fields were empty
        if not (suhistdict and en and bg and anbul):
            return error("One or more of the fields have not been filled")

        # Ensure the link to SU dictionary is valid
        if not "histdict.uni-sofia.bg" in suhistdict:
            return error('The link to SU dictionary entry is not valid (hint: the field should contain "histdict.uni-sofia.bg"). Feel free to copy-paste this (without the quotes) if you are just testing the website.')

        # Ensure English field contains only Latin letters
        if not (only_lat_letters(en)):
            return error('Only Latin (English) letters allowed in the English field.')

        # Ensure Bulgarian field contains only Cyrillic letters
        if not (only_cyr_letters(bg)):
            return error('"Български (Bulgarian)" field (third one) should contain only (modern) Bulgarian /Cyrillic/ characters. Just want to test the website? Copy-paste "тест" (test in Bulgarian) in the field!')

        # Ensure Ancient Bulgarian field contains only Ancient Bulgarian letters
        if not (only_anbul_letters(anbul)):
            return error('Only Ancient Bulgarian letters allowed in the last field. Just want to test the website? Input random letters from the provided keyboard.')


        """If all checks passed, add the new word to the database"""
        new_word_id = add_new_word(suhistdict, en, bg, anbul, userid, db)

        return redirect(url_for('.word', id=new_word_id))

    else:
        # If user is admin, use verb "Add";
        # otherwise, use verb "Suggest"
        if userid == 1:
            content["action"] = "Add"
        else:
            content["action"] = "Suggest"
        return render_template("new.html", new_active="active", content=content)


@app.route("/register", methods=["GET", "POST"])
def register():
    # Register user

    # Forget any user_id in case user manually goes to /register when logged in
    session.clear()

    if request.method == "POST":
        """Ensure a valid form was sent"""
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Ensure username was submitted
        if not username:
            return error("Username not provided")

        # Ensure username consists of at least 3 and no more than 20 characters
        elif len(username) < 3 or len(username) > 20:
            return error("Username too short (<3 characters) or too long (>20 characters)")

        # Ensure password was submitted
        elif not password:
            return error("Password not provided")

        # Ensure password confirmation was submitted
        elif not confirmation:
            return error("Password confirmation not provided")

        # Ensure password and password confirmation match
        elif password != confirmation:
            return error("Password and password confirmation don't match")

        # Ensure password consists of at least 5 and no more than 200 characters
        elif len(password) < 5 or len(password) > 200:
            return error("Password too short (<5 characters) or too long (>200 characters)")

        """Register user, if chosen username is free"""
        # Ensure provided username does not exist
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=username)
        if len(rows) == 1:
            return error("Username already taken")

        # Insert user
        db.execute("INSERT INTO users (id,username,hash) VALUES (nextval('users_seq'),:username,:password)",
                   username=username,
                   password=generate_password_hash(request.form.get("password")))

        # Redirect to login page and confirm registration
        return render_template("login.html", login_active="active", new_registration=True)

    else:
        return render_template("register.html", reg_active="active")


@app.route("/search", methods=["GET"])
def search():
    # Display search results
    userid = session.get("user_id")
    content = dict()

    # Get query
    content["query"] = request.args.get("en")

    # If user manually visits "/search"
    if content["query"] is None:
        return error("Page not found", 404)

    # Too long query
    if len(content["query"]) > 45:
        return error("This search query is too long", 400)
    content["results"] = search_word("en", content["query"], userid, db)

    # No results on query
    if not content["results"]:
        return render_template("results.html", found_results=False, content=content)

    # Found results on query
    content["total"] = len(content["results"])
    return render_template("results.html", found_results=True, content=content)


@app.route("/suggestions", methods=["GET"])
@login_required
def suggestions():
    # Show user's suggested words (or all users' suggestions to admin)
    userid = session.get("user_id")
    content = dict()

    # Admin approval/rejection of word is handled by a GET argument
    admin_action = request.args.get("admin")
    if admin_action is not None:
        if userid != 1:
            return error("You do not have the rights to perform this action", 403)

        # The request would be in the format, e.g., "approve_5" or "reject_5" where the number is the word ID
        if (admin_action.startswith("approve_") or admin_action.startswith("reject_")) and admin_action.count("_") == 1:
            action, wordid = admin_action.split("_")

            # If user manually entered nonexisting word ID
            if not get_word(wordid, db): return error("This word does not exist.", "404")

            admin_review(action, wordid, db)  # e.g., admin_review(approve, 5)
            session["admin_approve_show"] = True if action == "approve" else False
            return redirect(url_for('.word', id=wordid))
        else:
            return error("Please do not manually enter values in admin field")

    else:
        content["title"] = "My suggestions" if userid != 1 else "User suggestions"

        # Note that the function returns all suggestions (approved, unreviewed AND unapproved)
        # to regular users and only unreviewed to admin
        content["suggestions"] = get_suggestions(userid, db)
        print(content["suggestions"])

        return render_template("suggestions.html", sug_active="active", content=content)


@app.route("/word", methods=["GET", "POST"])
def word():
    # See word in ancient Bulgarian and translations
    userid = session.get("user_id")
    content = dict()

    # POST method is a form to delete the word
    if request.method == "POST":
        confirmation = int(request.form.get("confirmation"))
        wordid = int(request.form.get("wordid"))

        delete_word(wordid, db)

        if confirmation == 0:
            return error("Word was deleted, but since you have disabled JavaScript, you were not asked for confirmation.", "199")

        session["delconfirm_show"] = True
        return redirect("/")

    # GET method displays word
    else:
        # Get word
        wordid = request.args.get("id")

        # If user manually entered a string as id
        if not wordid.isnumeric():
            return error("This word does not exist.", "404")

        word = get_word(wordid, db)

        # If user manually entered nonexisting word ID
        if not word:
            return error("This word does not exist.", "404")

        # If user is logged in, see if this word has already been favored by them
        if word_in_favorite(userid, wordid, db):
            fav_action = "Remove from favorites"
            fav_code = 1
        else:
            fav_action = "Add to favorites"
            fav_code = 0

        # Content to return
        content["word"] = word
        content["fav_action"] = fav_action
        content["fav_code"] = fav_code
        content["user_is_author"] = True if (userid == 1 or word["addedby"] == userid) else False  # to allow authors and admin word deletion

        # Alerts
        if session.get("admin_approve_show"):
            content["has_alert"] = True
            content["alert"] = "Successfully approved word!"
            content["alert_type"] = "success"
            session["admin_approve_show"] = False
        else:
            content["has_alert"] = True if word["approved"] != "y" else False
            if content["has_alert"]:
                content["alert"] = ("This word is still not reviewed by admin, so it is not shown in default search" if word["approved"] == "0"
                                    else "This word was rejected by admin, so it will not be shown in default search")
                content["alert_type"] = "warning" if word["approved"] == "0" else "danger"

        return render_template("word.html", content=content)