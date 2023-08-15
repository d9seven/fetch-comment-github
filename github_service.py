import requests
import os
import re
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


class Github:
    def __init__(self):
        self.token = os.environ.get("PERSONAL_TOKEN")
        self.owner = os.environ.get("OWNER")
        self.repo = os.environ.get("REPO")
        self.since = os.environ.get("SINCE")
        self.header = {"Authorization": f"Bearer {self.token}"}
        self.base_url = self.get_base_url()

    def get_base_url(self):
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/pulls/comments?since={self.since}"
        url += "&per_page=100&sort=created&direction=desc"
        return url

    def pr_review_comments(self):
        data = []
        page = 1
        while True:
            url = f"{self.base_url}&page={page}"
            response = requests.get(url, headers=self.header)
            if response.status_code != 200:
                print("Error:", response.status_code)
                continue
            comments = response.json()
            if not comments:
                break
            for comment in comments:
                pr_link = comment['_links']["pull_request"]["href"]
                data.append({
                    "author": comment["user"]["login"],
                    "body": comment["body"],
                    "date": comment["created_at"],
                    "pr_id": re.findall(r'\d+$', pr_link)[0],
                    "pr_link": pr_link,
                })
            page += 1

        for dt in data:
            print(dt)
