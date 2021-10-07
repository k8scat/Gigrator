"""
author: K8sCat <k8scat@gmail.com>
link: https://github.com/k8scat/gigrator.git
"""
from gigrator.git.git import Git
import requests


class Gitee(Git):
    def __init__(self, config: dict):
        super().__init__(config)
        self.headers = {
            "Content-Type": "application/json;charset=UTF-8"
        }

    def is_repo_existed(self, repo_name: str) -> bool:
        """
        获取用户的某个仓库: GET /repos/{owner}/{repo}
        https://gitee.com/api/v5/swagger#/getV5ReposOwnerRepo
        """
        url = f"{self.api}/repos/{self.username}/{repo_name}"
        params = {
            "access_token": self.token
        }
        with requests.get(url, headers=self.headers, params=params) as r:
            return r.status_code == requests.codes.ok

    def create_repo(self, name: str, desc: str, is_private: bool) -> bool:
        data = {
            "access_token": self.token,
            "name": name,
            "description": desc,
            "private": is_private
        }
        url = f"{self.api}/user/repos"
        with requests.post(url, json=data, headers=self.headers) as r:
            return r.status_code == requests.codes.created

    def list_repos(self) -> list:
        """
        列出授权用户的所有仓库: GET /user/repos
        https://gitee.com/api/v5/swagger#/getV5UserRepos
        """
        url = f"{self.api}/user/repos"
        params = {
            "access_token": self.token,
            "type": "personal",
            "sort": "full_name",
            "per_page": 100,
            "page": 1
        }
        all_repos = []
        while True:
            with requests.get(url, headers=self.headers, params=params) as r:
                if r.status_code != requests.codes.ok:
                    raise RuntimeError(r.content.decode("utf-8"))

                repos = r.json()
                if len(repos) == 0:
                    break

                for repo in repos:
                    all_repos.append(dict(name=repo["name"],
                                          desc=repo["description"],
                                          is_private=repo["private"]))
                params["page"] += 1
        return all_repos
