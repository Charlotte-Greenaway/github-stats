# GitHub Stats Dashboard

A Flask application to visualize GitHub activity and contributions. This project displays various statistics including the languages used, commit timeline, and top repositories for a given GitHub user.

## Live Demo

Check out the live demo [here](https://github-stats.charlotte-greenaway.com/).

## Features

- **Languages Used**: Displays the percentage of different programming languages used in the repositories.
- **Commit Timeline**: Shows the number of commits made over the past 30 days.
- **Top Repositories**: Lists the top repositories by recent activity.

## Getting Started

### Prerequisites

- Python 3.x
- Flask
- Requests
- dotenv

### Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/Charlotte-Greenaway/github-stats-dashboard.git
    cd github-stats-dashboard
    ```

2. Create a virtual environment and activate it:

    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. Install the required dependencies:

    ```sh
    pip install -r requirements.txt
    ```

4. Create a `.env` file in the root directory of the project and add your GitHub access token and username:

    ```sh
    GITHUB_ACCESS_TOKEN="your_access_token"
    GITHUB_USERNAME="your_username"
    ```

### Running the App

1. Start the Flask application:

    ```sh
    flask run
    ```

2. Open your web browser and go to `http://127.0.0.1:5000`.

## Deployment to Vercel

1. Install the Vercel CLI:

    ```sh
    npm install -g vercel
    ```

2. Run the deployment command:

    ```sh
    vercel
    ```

3. Follow the prompts to configure your project.

### Example `.env` file

```plaintext
GITHUB_ACCESS_TOKEN="your_access_token"
GITHUB_USERNAME="your_username"
```
