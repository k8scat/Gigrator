"""
author: K8sCat <k8scat@gmail.com>
link: https://github.com/k8scat/gigrator.git
"""
from gigrator.git.git import Git
import requests


class Gitea(Git):
    def __init__(self, config: dict):
        super().__init__(config)
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"token {self.token}"
        }

    def is_repo_existed(self, repo_name: str) -> bool:
        # GET
        # ​/repos​/{owner}​/{repo}
        # Get a repository
        url = f"{self.api}/repos/{self.username}/{repo_name}"
        with requests.get(url, headers=self.headers) as r:
            return r.status_code == requests.codes.ok

    def create_repo(self, name: str, desc: str, is_private: bool) -> bool:
        data = {
            "auto_init": False,
            "description": desc,
            "name": name,
            "private": is_private
        }
        url = f"{self.api}/user/repos"
        with requests.post(url, headers=self.headers, json=data) as r:
            return r.status_code == requests.codes.created

    def list_repos(self) -> list:
        # GET
        # ​/user​/repos
        # List the repos that the authenticated user owns or has access to
        # 没有做分页: https://github.com/go-gitea/gitea/issues/7515
        url = f"{self.api}/user/repos"
        all_repos = []
        with requests.get(url, headers=self.headers) as r:
            if r.status_code != requests.codes.ok:
                raise RuntimeError(r.content.decode("utf-8"))

            repos = r.json()
            for repo in repos:
                if repo["owner"]["username"] == self.username:
                    all_repos.append(dict(name=repo["name"],
                                          desc=repo["description"],
                                          is_private=repo["private"]))
        return all_repos
