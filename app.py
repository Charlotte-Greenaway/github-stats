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


class GitHubAPIError(Exception):
    """Raised when the GitHub API returns an error."""
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message
        super().__init__(f"{status_code}: {message}")


# get data from github with given url
def get_data(url):
    response = requests.get(url, headers=headers)
    if not response.ok:
        try:
            body = response.json()
            message = body.get("message", response.text or f"HTTP {response.status_code}")
        except Exception:
            message = response.text or f"HTTP {response.status_code}"
        raise GitHubAPIError(response.status_code, message)
    return response.json()


# Get repository data and process it (all pages)
def get_repo_data(username):
    url = f"https://api.github.com/users/{username}/repos"
    repos = []
    page = 1
    per_page = 100
    while True:
        data = get_data(f"{url}?per_page={per_page}&page={page}")
        if not data:
            break
        repos.extend(data)
        if len(data) < per_page:
            break
        page += 1
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
    if total > 0:
        for key in languages:
            languages[key] = round((languages[key] / total) * 100, 2)
    return languages

# Get commit timeline
def get_commit_timeline(username):
    # get commits from the last month and count them
    url = f"https://api.github.com/users/{username}/events"
    timeline = {}
    page = 1
    thirty_days_ago = datetime.now() - timedelta(days=30)
    should_stop = False

    while not should_stop:
        data = get_data(url + f"?page={page}")
        if not data:
            break
        for event in data:
            event_date = event["created_at"].split("T")[0]
            if datetime.strptime(event_date, "%Y-%m-%d").date() < thirty_days_ago.date():
                should_stop = True
                break
            if event["type"] == "PushEvent":
                if event_date not in timeline:
                    timeline[event_date] = 0
                timeline[event_date] += 1
        page += 1

    return timeline
        

# Get top 6 repositories
def get_top_repos(repos):
    repos.sort(key=lambda x: x["updated_at"], reverse=True)
    return repos[:6]

# Get total number of repositories, total size of all repositories and most recently updated repository
def get_repo_stats(repos):
    total_repos = len(repos)
    total_size = sum(repo["size"] for repo in repos)
    total_size = round(total_size / 1024, 2)
    if not repos:
        most_recent_details = {"name": "—", "url": "#", "updated_at": "—"}
        return total_repos, total_size, most_recent_details
    most_recent = max(repos, key=lambda x: x["updated_at"])
    most_recent_details = {
        "name": most_recent["name"],
        "url": most_recent["html_url"],
        "updated_at": datetime.strptime(most_recent["updated_at"], "%Y-%m-%dT%H:%M:%SZ").strftime("%d/%m/%Y"),
    }
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
    try:
        repos = get_repo_data(username)
        languages = get_languages(repos)
        timeline = get_commit_timeline(username)
        top_repos = get_top_repos(repos)
        total_repos, total_size, most_recent = get_repo_stats(repos)
        return make_response(
            render_template(
                "index.html",
                languages=languages,
                timeline=timeline,
                repos=top_repos,
                most_recent=most_recent,
                total_repos=total_repos,
                total_size=total_size,
                error=None,
            )
        )
    except GitHubAPIError as e:
        status = e.status_code if e.status_code in (401, 403, 404) else 502
        return (
            render_template(
                "index.html",
                error=e.message,
                error_code=e.status_code,
                languages={},
                timeline={},
                repos=[],
                most_recent={"name": "", "url": "#", "updated_at": ""},
                total_repos=0,
                total_size=0,
            ),
            status,
        )


if __name__ == "__main__":
    app.run(port=3000, debug=True)
