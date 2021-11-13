# CODE ATTRIBUTION:
# The code for this website is based on the excellent Data Centric Design
# Mini Project Walk-through by Tim Nelson (https://github.com/TravelTimN)
# of Code Institute. Where custom functionality was required it was
# generally based on modifying Tim's original logic to fulfill the
# project requirements.

import os, datetime
from flask import (
    Flask, flash, render_template, redirect,
    request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")

app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


# Render main page
@app.route("/")
@app.route("/get_overview")
def get_overview():
    rooms = list(mongo.db.electricalRooms.find())
    return render_template("overview.html", rooms=rooms)


# Render registration page
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Check if username already exists in database.
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})
        flash("existing_user")

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        register_details = {
            "username": request.form.get("username").lower(),
            "first_name": request.form.get("first_name"),
            "last_name": request.form.get("last_name"),
            "company": request.form.get("company"),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register_details)

        # Put user into session cookie.
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful")
        return redirect(url_for("profile", username=session["user"]))
    return render_template("register.html")


# Render login page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # Check hashed password against password provided.
            if check_password_hash(
                existing_user["password"],
                    request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome, {}".format(request.form.get("username")))
                return redirect(
                    url_for("profile", username=session["user"]))
            else:
                # Display message in case password incorrect.
                flash("Incorrect username or password")
                return redirect(url_for("login"))
        else:
            # Display message in case username incorrect.
            flash("Incorrect username or password")
            return redirect(url_for("login"))

    return render_template("login.html")


# Render user profile page
@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    first_name = mongo.db.users.find_one(
        {"username": session["user"]})["first_name"]
    last_name = mongo.db.users.find_one(
        {"username": session["user"]})["last_name"]
    company = mongo.db.users.find_one(
        {"username": session["user"]})["company"]

    if session["user"]:
        return render_template(
            "profile.html",
            username=username,
            first_name=first_name,
            last_name=last_name,
            company=company)

    return redirect(url_for("login"))


# Logout function
@app.route("/logout")
def logout():
    # remove session from cookies
    flash("You've been safely logged out.")
    session.pop("user")
    return redirect(url_for("login"))


# Render new survey page
@app.route("/new_survey")
def new_survey():
    return render_template("new-survey.html")

#  testhigh ##############################   WORKING IN HERE   #################################################################

# Render new issue page
@app.route("/new_issue", methods=["GET", "POST"])
def new_issue():
    if request.method == "POST":
        new_issue = {
            "roomRef": request.form.get("room_ref"),
            "questionNumber": request.form.get("question_no"),
            "issueComment": request.form.get("issue_comment"),
            "createdBy": session["user"],
            "createdAt": datetime.datetime.now(),
        }
        mongo.db.surveyIssues.insert_one(new_issue)
        flash("New electrical issue raised.")
        return redirect(url_for("get_overview"))
    rooms = list(mongo.db.electricalRooms.find().sort("_id", 1))
    questions = list(mongo.db.surveyQuestions.find().sort("_id", 1))
    voltages = list(mongo.db.voltages.find().sort("_id", 1))
    types = list(mongo.db.roomTypes.find().sort("_id", 1))
    return render_template("new-issue.html", rooms=rooms, questions=questions, voltages=voltages, types=types)

#  testhigh ##############################   WORKING IN HERE   #################################################################


# Manage section
# Render electrical rooms list page
@app.route("/get_room_list")
def get_room_list():
    rooms = list(mongo.db.electricalRooms.find())
    return render_template("room-list.html", rooms=rooms)


# Edit an individual electrical room's details
@app.route("/edit_room/<room_id>", methods=["GET", "POST"])
def edit_room(room_id):
    if request.method == "POST":
        edited_room = {
            "roomRef": request.form.get("room_ref"),
            "roomDesc": request.form.get("room_desc"),
            "roomVolts": request.form.get("room_volts"),
            "roomType": request.form.get("room_type"),
            "editedBy": session["user"]
        }
        mongo.db.electricalRooms.update(
            {"_id": ObjectId(room_id)}, edited_room)
        flash("Electrical room edited successfully.")
        return redirect(url_for("get_room_list"))
    room = mongo.db.electricalRooms.find_one({"_id": ObjectId(room_id)})
    voltages = list(mongo.db.voltages.find().sort("_id", 1))
    types = list(mongo.db.roomTypes.find().sort("_id", 1))
    return render_template(
        "edit_room.html",
        room=room,
        voltages=voltages,
        types=types)


# Delete an electrical room function
@app.route("/delete_room/<room_id>")
def delete_room(room_id):
    mongo.db.electricalRooms.remove({"_id": ObjectId(room_id)})
    flash("Room successfully deleted.")
    return redirect(url_for("get_rooms_list"))


# Render add electrical room page
@app.route("/add_room", methods=["GET", "POST"])
def add_room():
    if request.method == "POST":
        new_room = {
            "roomRef": request.form.get("room_ref"),
            "roomDesc": request.form.get("room_desc"),
            "roomVolts": request.form.get("room_volts"),
            "roomType": request.form.get("room_type"),
            "createdBy": session["user"]
        }
        mongo.db.electricalRooms.insert_one(new_room)
        flash("New electrical room added successfully.")
        return redirect(url_for("get_overview"))
    voltages = list(mongo.db.voltages.find().sort("_id", 1))
    types = list(mongo.db.roomTypes.find().sort("_id", 1))
    return render_template("addroom.html", voltages=voltages, types=types)


# Render survey questions list page
@app.route("/survey_question_list")
def survey_question_list():
    questions = list(mongo.db.surveyQuestions.find().sort("_id", 1))
    return render_template("survey-question-list.html", questions=questions)


# Render survey questions edit page
@app.route("/survey_question_edit", methods=["GET", "POST"])
def survey_question_edit(question_id):
    if request.method == "POST":
        edited_question = {
            "questionShort": request.form.get("question_short"),
            "questionLong": request.form.get("question_long"),
            "editedBy": session["user"]
        }
        mongo.db.surveyQuestions.update(
            {"_id": ObjectId(question_id)}, edited_question)
        flash("Survey question edited successfully.")
        return redirect(url_for("survey_question_list"))

    questions = list(mongo.db.surveyQuestions.find().sort("_id", 1))
    return render_template("survey-question-edit.html", questions=questions)


# Render test page testhigh to be deleted
@app.route("/test_page")
def test_page():
    # reports = list(mongo.db.surveyReport.find_one())
    # questions = list(mongo.db.surveyQuestions.find().sort("_id", 1))
    now = datetime.datetime.now()
    date_time_string = now.strftime("%A, %d. %B %Y %I:%M%p")
    # testing code here for renedering survey issues testhigh------------------------------------------------
    
    # Query MongoDB for Survey Issues and turn it into a list.
    survey_issues = list(mongo.db.surveyIssues.find().sort("_id", 1))
    # Create a new list for holding the fully rendered issues to be sent to html.
    rendered_survey_issues = []
    # Loop through Mongo DB's returned list.
    for budgie in survey_issues:
        room_ref = budgie['roomRef']
        # Look up electricalRooms collection to get room type, description and voltage.
        room_dictionary = mongo.db.electricalRooms.find_one({"roomRef": room_ref})
        room_type = room_dictionary['roomType']
        room_desc = room_dictionary['roomDesc']
        room_volts = room_dictionary['roomVolts']
        # Look up surveyQuestions collection to get full question texts.
        question_no = budgie['questionNumber']
        question_dictionary = mongo.db.surveyQuestions.find_one({"questionNumber": question_no})
        question_short = question_dictionary['questionShort']
        question_long = question_dictionary['questionLong']
        # Get the comment added by the surveyor.
        issue_comment = budgie['issueComment']
        # Look up user collections to get the surveyor's full name and company 
        created_by = budgie['createdBy']
        created_by_dictionary = mongo.db.users.find_one({"username": created_by})
        created_by_fullname = created_by_dictionary['first_name'] + " " + created_by_dictionary['last_name']
        created_by_company = created_by_dictionary['company']
        # Convert date time stamp to full text formatting.
        created_at = budgie['createdAt'].strftime("%A, %d. %B %Y %I:%M%p")
        # Pack all values into a dictionary and append it to the
        # rendered_survey_issues list.
        issue = {
            'roomRef': room_ref,
            'roomType': room_type,
            'roomDesc': room_desc,
            'roomVolts': room_volts,
            'questionNumber': question_no,
            'questionShort': question_short,
            'questionLong': question_long,
            'issueComment': issue_comment,
            'createdBy': created_by,
            'createdByFullname': created_by_fullname,
            'createdByCompany': created_by_company,
            'createdAt': created_at,
        }
        rendered_survey_issues.append(issue)
    # end testing code here testhigh ------------------------------------------
    rooms = list(mongo.db.electricalRooms.find().sort("_id", 1))
    questions = list(mongo.db.surveyQuestions.find().sort("_id", 1))
    voltages = list(mongo.db.voltages.find().sort("_id", 1))
    types = list(mongo.db.roomTypes.find().sort("_id", 1))
    return render_template("test-page.html", rendered_survey_issues=rendered_survey_issues,survey_issues=survey_issues, now=now, date_time_string=date_time_string, rooms=rooms, questions=questions, voltages=voltages, types=types)


# Render user list
@app.route("/user_list")
def user_list():
    return render_template("user-list.html")


# Main function
if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)  # testhigh
