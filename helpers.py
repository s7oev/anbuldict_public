import os
import requests
import urllib.parse
import re

from flask import redirect, render_template, request, session
from functools import wraps

from cs50 import SQL

def error(message, code=400):
    # Render error message and code
    return render_template("error.html", message=message, code=code)


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


# Function for adding a new word, ensuring field "Bulgarian"
# is composed only of Bulgarian letters
def only_cyr_letters(bgtext):
    cyr = []
    for letter in bgtext:
        cyr.append(bool(re.search('[а-яА-Я]', letter)))
    return all(cyr)


# Same as above but for English
def only_lat_letters(entext):
    lat = []
    for letter in entext:
        lat.append(bool(re.search('[a-zA-Z]', letter)))
    return all(lat)


# Similar to above but for Ancient Bulgarian letters
def only_anbul_letters(anbultext):
    anbul = []
    for letter in anbultext:
        anbul.append(bool(re.search('^[ꙃѫѭѧѩꙙыꙋѳѡѣꙗюертꙁуопшщасдфгхїклжъьцвбнмꙑѹг҄л҄]*$', letter)))
    return all(anbul)

###################################
###     DATABASE OPERATIONS     ###
###################################

def search_word(lang, term, userid, db, contains=True, all_words=False):
    term = term.lower()

    # Modify contains in the form of an SQL query that matches only part of string
    if contains:
        term = "%" + term + "%"

    if not all_words:
        if lang == "en":
            results = db.execute("SELECT * FROM words WHERE en LIKE :term AND approved LIKE 'y'", term=term)
        else:
            results = db.execute("SELECT * FROM words WHERE bg LIKE :term AND approved LIKE 'y'", term=term)
    else:
        if lang =="en":
            results = db.execute("SELECT * FROM words WHERE en LIKE :term", term=term)
        else:
            results = db.execute("SELECT * FROM words WHERE bg LIKE :term", term=term)

    return results


def get_word(wordid, db):
    word = db.execute("SELECT * FROM words WHERE id = :wordid", wordid=wordid)

    if word:
        word = word[0]  # a list with 1 entry of dictionary ==> just dictionary

    return word


# This function returns the ID of the new word
def add_new_word(suhistdict, en, bg, anbul, userid, db):
    # Check if word was added by admin; if yes,
    # automatically approve it. Field explanation:
    # 0: not checked; "y" - checked and approved;
    # "n" - checked and not approved
    approved = "y" if userid == 1 else "0"

    db.execute("INSERT INTO words (id, suhistdict, en, bg, anbul, addedby, approved) VALUES (nextval('words_seq'), :suhistdict, :en, :bg, :anbul, :userid, :approved)",
               suhistdict=suhistdict, en=en, bg=bg, anbul=anbul, userid=userid, approved=approved)

    new_word_id = (db.execute("SELECT MAX(id) FROM words"))[0]["max"]  # the latest ID will be the one with highest value (max)

    return new_word_id

def delete_word(wordid, db):
    # Delete word from main table
    db.execute("DELETE FROM words WHERE (id = :wordid)", wordid=wordid)

    # Also delete all occurences of this word in favorites
    db.execute("DELETE FROM favorites WHERE wordid = :wordid",
               wordid=wordid)


def add_favorite(userid, wordid, db):
    db.execute("INSERT INTO favorites (favid,userid,wordid) VALUES (nextval('favorites_seq'), :userid, :wordid)",
                userid=userid, wordid=wordid)


def remove_favorite(userid, wordid, db):
    db.execute("DELETE FROM favorites WHERE userid = :userid AND wordid = :wordid",
               userid=userid, wordid=wordid)


def word_in_favorite(userid, wordid, db):
    check = db.execute("SELECT * FROM favorites WHERE userid = :userid AND wordid = :wordid",
                       userid=userid, wordid=wordid)

    # If no rows were returned, it is not yet favorited by that user
    return True if len(check) == 1 else False


def get_favorites(userid, db):
    favorites = db.execute("SELECT wordid FROM favorites WHERE userid = :userid",
                           userid=userid)

    # Convert to list of IDs
    tmp = []
    for favorite in favorites:
        tmp.append(favorite["wordid"])
    favorites = tmp

    # Finally, get all available data for the word
    tmp = []
    for favorite in favorites:
        tmp.append(get_word(favorite, db))
    favorites = tmp

    return favorites


def get_suggestions(userid, db):
    if userid == 1:
        return db.execute("SELECT * FROM words WHERE approved LIKE '0'")
    else:
        return db.execute("SELECT * FROM words WHERE addedby = :userid", userid=userid)


# The following function takes as input "approve" or "reject" and word ID to perform that action on
def admin_review(action, wordid, db):
    if action == "approve":
        db.execute("UPDATE words SET approved = 'y' WHERE id = :wordid", wordid=wordid)
    else:
        db.execute("UPDATE words SET approved = 'n' WHERE id = :wordid", wordid=wordid)