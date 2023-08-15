import requests
import os
import re
import xlsxwriter
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
        self.ignore_author = self.get_ignore_author()

    def get_ignore_author(self):
        ignore_author = os.environ.get("IGNORE_AUTHOR").split(',')
        if "" in ignore_author:
            ignore_author.remove("")
        return ignore_author

    def get_base_url(self):
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/pulls/comments?since={self.since}"
        url += "&per_page=100&sort=created&direction=asc"
        return url

    def create_excel(self, data):
        workbook = xlsxwriter.Workbook('result_comments.xlsx')
        worksheet = workbook.add_worksheet()

        col = 0

        worksheet.write(0, col, "Author")
        worksheet.write(0, col + 1, "Comment content")
        worksheet.write(0, col + 2, "Date")
        worksheet.write(0, col + 3, "PullRequest")
        worksheet.write(0, col + 4, "Comment URL")
        for idx, comment in enumerate(data):
            worksheet.write(idx + 1, col, comment["author"])
            worksheet.write(idx + 1, col + 1, comment["body"])
            worksheet.write(idx + 1, col + 2, comment["date"])
            worksheet.write(idx + 1, col + 3, comment["pr_id"])
            worksheet.write(idx + 1, col + 4, comment["pr_link"])
        workbook.close()

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
                author = comment["user"]["login"]
                if author in self.ignore_author:
                    continue
                pr_link = comment['_links']["pull_request"]["href"]
                data.append({
                    "author": author,
                    "body": comment["body"],
                    "date": comment["created_at"],
                    "pr_id": re.findall(r'\d+$', pr_link)[0],
                    "pr_link": pr_link,
                })
            page += 1
        self.create_excel(data)
