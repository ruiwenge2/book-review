from replit import db
from flask import Flask, render_template, redirect, request, make_response, send_file
import pickledb
from dbactions import *

app = Flask("app")
allposts = pickledb.load("allposts.json", True)

@app.route("/")
def index():
	loggedIn = request.cookies.get("loggedIn")
	username = request.cookies.get("username")
	if loggedIn == "true":
		if username != None and username in db["accounts"].keys():
			return render_template("loggedin/home.html", username=username)
		else:
			return redirect("/logout")
	else:
		return render_template("home.html")

@app.route("/login")
def login():
	loggedIn = request.cookies.get("loggedIn")
	if loggedIn == "true":
		return redirect("/")
	else:
		return render_template("login.html")

@app.route("/signup")
def signup():
	if "accounts" not in db.keys():
		db["accounts"] = {}
	loggedIn = request.cookies.get("loggedIn")
	if loggedIn == "true":
		return redirect("/")
	else:
		return render_template("signup.html")

@app.route("/loginsubmit", methods=["GET", "POST"])
def loginsubmit():
  if request.method == "POST":
    username = request.form.get("username")
    password = request.form.get("password")
    if username in db["accounts"].keys():
      if password == db["accounts"][username]:
        resp = make_response(render_template('readcookie.html'))
        resp.set_cookie("loggedIn", "true")
        resp.set_cookie("username", username)
        return resp
      else:
        return render_template("message.html", message="Incorrect password.")
    else:
      return render_template("message.html", message="Account not found.")
  return redirect("/")

@app.route("/createaccount", methods=["GET", "POST"])
def createaccount():
  if request.method == "POST":
    newusername = request.form.get("newusername")
    newpassword = request.form.get("newpassword")
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    cap_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    allchars = letters + cap_letters + numbers + ['_']
    print(newusername)
    for i in newusername:
      if i not in allchars:
        return render_template("message.html", message="Username can only contain alphanumeric characters and underscores.")
    if newusername in db["accounts"].keys():
      return render_template("message.html", message="Username taken.")
    if newusername == "":
      return render_template("message.html", message="Please enter a username.")
    if newpassword == "":
      return render_template("message.html", message="Please enter a password.")
    db["accounts"][newusername] = newpassword
    resp = make_response(render_template('readcookie.html'))
    resp.set_cookie("loggedIn", "true")
    resp.set_cookie("username", newusername)
    return resp
  return redirect("/")

@app.route("/logout")
def logout():
	resp = make_response(render_template('readcookie.html'))
	resp.set_cookie("loggedIn", "false")
	resp.set_cookie("username", "None")
	return resp

@app.route("/books")
def books():
	loggedIn = request.cookies.get("loggedIn")
	username = request.cookies.get("username")
	if loggedIn == "true":
		if username != None and username in db["accounts"].keys():
			return render_template("loggedin/books.html")
		else:
			return redirect("/logout")
	else:
		return render_template("books.html")

@app.route("/books/<bookid>")
def post(bookid):
  if bookid not in allposts.getall():
    return redirect("/books")
  reviewer = allposts.get(bookid)["reviewer"]
  title = allposts.get(bookid)["title"]
  author = allposts.get(bookid)["author"]
  details = allposts.get(bookid)["details"]
  loggedIn = request.cookies.get("loggedIn")
  username = request.cookies.get("username")
  if loggedIn == "true":
    if username != None and username in db["accounts"].keys():
      if username == reviewer:
        return render_template("loggedin/reviewer.html", reviewer=reviewer, title=title, author=author, details=details, bookid=bookid)
      return render_template("loggedin/bookreview.html", reviewer=reviewer, title=title, author=author, details=details)
    else:
      return redirect("/logout")
  else:
    return render_template("bookreview.html",reviewer=reviewer, title=title, author=author, details=details)

@app.route("/books/<bookid>/edit")
def edit(bookid):
  if bookid not in allposts.getall():
    return redirect("/books/" + bookid)
  reviewer = allposts.get(bookid)["reviewer"]
  title = allposts.get(bookid)["title"]
  author = allposts.get(bookid)["author"]
  details = allposts.get(bookid)["details"]
  if request.cookies.get("username") != reviewer:
    return redirect("/books/" + bookid)
  return render_template("editbookreview.html", title=title, author=author, details=details, bookid=bookid)

@app.route("/books/<bookid>/editreviewsubmit", methods=["GET", "POST"])
def editbookreview(bookid):
  if request.method == "POST":
    title = request.form.get("title")
    author = request.form.get("author")
    details = request.form.get("details")
    if title == "":
      return render_template("loggedin/message.html", message="Please enter a title.")
    if author == "":
      return render_template("loggedin/message.html", message="Please enter an author.")
    if details == "":
      return render_template("loggedin/message.html", message="Please enter some background information.")
    username = request.cookies.get("username")
    allposts.set(bookid, {
      "reviewer": username,
      "author": author,
      "title": title,
      "details": details
		})
  return redirect("/books/" + bookid)


@app.route("/reviews")
def reviews():
  html = """<!DOCTYPE html><html><head><style>@import url(https://fonts.googleapis.com/css2?family=Roboto&display=swap); body {text-align:center; color:white;font-family:'Roboto';} a, a:visited {font-size:20px;color:white;} a:hover, a:active {text-decoration:none;}</style></head><body><h1>Book Reviews</h1>"""
  link = "/books/"
  posts = list(allposts.getall())
  posts.reverse() # put the newest reviews on the top
  for i in posts:
    html += "<a href={} target=_blank>{}</a><br><br>".format(link + i, allposts.get(i)["title"])
  html += "</body></html>"
  return html

@app.route("/searchresults")
def searchresults():
  loggedIn = request.cookies.get("loggedIn")
  username = request.cookies.get("username")
  search = request.args.get("search")
  if loggedIn == "true":
    if username != None and username in db["accounts"].keys():
      return render_template("loggedin/searchresults.html", search=search)
    else:
      return redirect("/logout")
  else:
    return render_template("searchresults.html", search=search)
  

@app.route("/searchbooks")
def search():
  html = """<!DOCTYPE html><html><head><style>@import url(https://fonts.googleapis.com/css2?family=Roboto&display=swap); body {text-align:center; color:white;font-family:'Roboto';} a, a:visited {font-size:20px;color:white;} a:hover, a:active {text-decoration:none;}</style></head><body>"""
  link = "/books/"
  search = request.args.get("search")
  posts = list(allposts.getall())
  posts.reverse()
  for i in posts:
    if search.lower() in allposts.get(i)["title"].lower():
      html += "<a href={} target=_blank>{}</a><br><br>".format(link + i, allposts.get(i)["title"])
  html += "</body></html>"
  return html

@app.route("/user/<user>")
def profile(user):
	if user not in db["accounts"].keys():
		return redirect("/")
	loggedIn = request.cookies.get("loggedIn")
	username = request.cookies.get("username")
	if loggedIn == "true":
		if username != None and username in db["accounts"].keys():
			return render_template("loggedin/profile.html", username=user)
		else:
			return redirect("/logout")
	else:
		return render_template("profile.html", username=user)


@app.route("/user/<username>/posts")
def posts(username):
  html = """<!DOCTYPE html><html><head><style>@import url(https://fonts.googleapis.com/css2?family=Roboto&display=swap); body {text-align:center; color:white;font-family:'Roboto';} a, a:visited {font-size:20px;color:white;} a:hover, a:active {text-decoration:none;}</style></head><body><h1>Book Reviews by """ + username + "</h1>"
  link = "/books/"
  posts = list(allposts.getall())
  posts.reverse()
  for i in posts:
    if allposts.get(i)["reviewer"] == username:
      html += "<a href={} target=_blank>{}</a><br><br>".format(
          link + i, allposts.get(i)["title"])
  html += "</body></html>"
  return html

@app.route("/createreview")
def create():
  loggedIn = request.cookies.get("loggedIn")
  username = request.cookies.get("username")
  if loggedIn == "true":
    if username != None and username in db["accounts"].keys():
      return render_template("createreview.html")
  return redirect("/login")

@app.route("/createreviewsubmit", methods=["GET", "POST"])
def createreviewsubmit():
  if request.method == "POST":
    username = request.cookies.get("username")
    title = request.form.get("title")
    author = request.form.get("author")
    details = request.form.get("details")
    if "number" not in db.keys():
      db["number"] = 0
    if title == "":
      return render_template("loggedin/message.html", message="Please enter a title.")
    if author == "":
      return render_template("loggedin/message.html", message="Please enter an author.")
    if details == "":
      return render_template("loggedin/message.html", message="Please enter some background information.")
    reviewid = str(db["number"] + 1)
    db["number"] += 1
    allposts.set(reviewid, {"reviewer": username,"author": author,"title": title,"details": details})
    return redirect("/books/" + reviewid)
  return redirect("/")

@app.route("/about")
def about():
  return render_template("about.html")

@app.route("/allposts")
def showallposts():
  return send_file("allposts.json")

@app.errorhandler(404)
def page_not_found(e):
	loggedIn = request.cookies.get("loggedIn")
	username = request.cookies.get("username")
	if loggedIn == "true":
		if username != None and username in db["accounts"].keys():
			return render_template("loggedin/404.html")
		else:
			return redirect("/logout")
	else:
		return render_template("404.html")

app.run(host="0.0.0.0", port=8080)