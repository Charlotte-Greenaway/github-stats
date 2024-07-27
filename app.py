import os
import requests
from dotenv import load_dotenv
from flask import Flask, render_template, make_response
from datetime import datetime, timedelta

# Load environment variables from .env file
load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
username = GITHUB_USERNAME
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}


# get data from github with given url
def get_data(url):
    response = requests.get(url, headers=headers)
    return response.json()


# Get repository data and process it
def get_repo_data(username):
    url = f"https://api.github.com/users/{username}/repos"
    repos = get_data(url)
    return repos

# Get languages used in repositories
def get_languages(repos):
    languages = {}
    for repo in repos:
        if repo["language"]:
            if repo["language"] in languages:
                languages[repo["language"]] += 1
            else:
                languages[repo["language"]] = 1
    total = sum(languages.values())
    for key in languages:
        languages[key] = round((languages[key] / total) * 100, 2)
    return languages

# Get commit timeline
def get_commit_timeline(username):
    #get commits from the last month and count them
    url = f"https://api.github.com/users/{username}/events"
    timeline={}
    page = 1
    #get todays datw
    today = datetime.now()
    #get the date 30 days ago
    thirty_days_ago = today - timedelta(days=30)
    #while the date is less than 30 days ago
    while today > thirty_days_ago:
        #get the data
        data = get_data(url + f"?page={page}")
        #if there is no data, break
        if not data:
            break
        #for each event
        for event in data:
            #if the event is a push event
            if event["type"] == "PushEvent":
                #get the date
                date = event["created_at"].split("T")[0]
                #if the date is not in the dictionary, add it
                if date not in timeline:
                    timeline[date] = 0
                #add 1 to the date
                timeline[date] += 1
            #if the date is less than 30 days ago, break
            if datetime.strptime(date, "%Y-%m-%d") < thirty_days_ago:
                break
        #add 1 to the page
        page += 1
    return timeline
        

# Get top 6 repositories
def get_top_repos(repos):
    repos.sort(key=lambda x: x["updated_at"], reverse=True)
    return repos[:6]

# Get total number of repositories, total size of all repositories and most recently updated repository
def get_repo_stats(repos):
    #get total number of repos
    total_repos = len(repos)
    #get total size of all repos
    total_size = sum(repo["size"] for repo in repos)
    #get most recently updated repo
    most_recent = max(repos, key=lambda x: x["updated_at"])
    most_recent_details = {
        "name": most_recent["name"],
        "url": most_recent["html_url"],
        #format updated at date to dd/mm/yyyy
        "updated_at": datetime.strptime(most_recent["updated_at"], "%Y-%m-%dT%H:%M:%SZ").strftime("%d/%m/%Y")
    }
    #return total size in MB and ensure it is rounded to 2 decimal places
    total_size = round(total_size / 1024, 2)

    return total_repos, total_size, most_recent_details


app = Flask(__name__)
# Add headers to all responses
@app.after_request
def add_headers(response):
    response.headers["Cache-Control"] = "public, max-age=86400"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response
# Home route
@app.route("/", methods=["GET", "POST"])
def home():
    repos = get_repo_data(username)
    languages = get_languages(repos)
    timeline = get_commit_timeline(username)
    top_repos = get_top_repos(repos)
    total_repos, total_size, most_recent = get_repo_stats(repos)
    response = make_response(
        render_template(
            "index.html", 
            languages=languages, 
            timeline=timeline, 
            repos=top_repos, 
            most_recent=most_recent, 
            total_repos=total_repos, 
            total_size=total_size
        )
    )
    return response


if __name__ == "__main__":
    app.run(port=3000, debug=True)
