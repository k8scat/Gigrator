"""
author: K8sCat <k8scat@gmail.com>
link: https://github.com/k8scat/gigrator.git
"""
from gigrator.git.git import Git
import requests
from urllib.parse import quote


class Gitlab(Git):
    def __init__(self, config: dict):
        super().__init__(config)
        self.headers = {
            "Private-Token": self.token
        }

    def is_repo_existed(self, repo_name: str) -> bool:
        """
        Get single project
        GET /projects/:id
        """
        path = quote(f"{self.username}/{repo_name}", safe="")
        url = f"{self.api}/projects/{path}"
        with requests.get(url, headers=self.headers) as r:
            return r.status_code == requests.codes.ok

    def create_repo(self, name: str, desc: str, is_private: bool) -> bool:
        data = {
            "name": name,
            "description": desc,
            "visibility": "private" if is_private else "public"
        }
        url = f"{self.api}/projects"
        with requests.post(url, json=data, headers=self.headers) as r:
            return r.status_code == requests.codes.created

    def list_repos(self) -> list:
        """
        List user projects: GET /users/:user_id/projects (需要分页: ?page=1)
        不存在401的问题: 会返回公开的仓库
        """
        url = f"{self.api}/users/{self.username}/projects"
        params = {
            "page": 1
        }
        all_repos = []
        while True:
            with requests.get(url, headers=self.headers, params=params) as r:
                if r.status_code != requests.codes.ok:
                    raise RuntimeError(r.content)

                repos = r.json()
                if len(repos) == 0:
                    break

                params["page"] += 1
                for repo in repos:
                    is_private = repo["visibility"] != "public"
                    all_repos.append(dict(name=repo["name"],
                                          desc=repo["description"],
                                          is_private=is_private))
        return all_repos
