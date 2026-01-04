from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash
import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import BytesIO
import random

app = Flask(__name__)
app.secret_key = "supersecretkey"


# Scrape jobs
def scrape_jobs():
    url = "https://realpython.github.io/fake-jobs/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    jobs = []
    job_cards = soup.find_all("div", class_="card-content")

    for job in job_cards:
        title = job.find("h2", class_="title").text.strip()
        company = job.find("h3", class_="subtitle").text.strip()
        location = job.find("p", class_="location").text.strip()

        job_types = ["Python Developer", "Java Developer", "UI/UX Designer", "Data Scientist", "Frontend Developer", "Backend Developer"]
        title = random.choice(job_types)

        jobs.append({"Job Title": title, "Company": company, "Location": location})

    return jobs


# Login
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == "admin" and password == "123":
            session["user"] = username
            return redirect(url_for("search"))
        else:
            return render_template("login.html", error="❌ Invalid Username or Password")
    return render_template("login.html")


# Search
@app.route("/search", methods=["GET", "POST"])
def search():
    if "user" not in session:
        return redirect(url_for("login"))

    results = []
    query = ""
    if request.method == "POST":
        query = request.form["query"].lower()
        jobs = scrape_jobs()
        results = [
            job for job in jobs
            if query in job["Job Title"].lower() or
               query in job["Company"].lower() or
               query in job["Location"].lower()
        ]
        session["filtered_jobs"] = results

    return render_template("search.html", results=results, query=query)


# Apply for a Job
@app.route("/apply/<job_title>", methods=["GET", "POST"])
def apply(job_title):
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        resume = request.form["resume"]

        flash(f"✅ Application submitted successfully for {job_title}!", "success")
        return redirect(url_for("search"))

    return render_template("apply.html", job_title=job_title)


# Download
@app.route("/download")
def download():
    if "user" not in session:
        return redirect(url_for("login"))

    filtered_jobs = session.get("filtered_jobs", [])
    if not filtered_jobs:
        return "<h3 style='text-align:center;'>No jobs to download. Please search first.</h3>"

    df = pd.DataFrame(filtered_jobs)
    buffer = BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="filtered_jobs.csv", mimetype="text/csv")


# Logout
@app.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("filtered_jobs", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
