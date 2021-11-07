"""
author: K8sCat <k8scat@gmail.com>
link: https://github.com/k8scat/gigrator.git
"""
import requests
from gigrator.git.git import Git


class Coding(Git):
    def __init__(self, config: dict):
        super().__init__(config)
        self.headers = {
            "Authorization": f"token {self.token}"
        }

    def is_repo_existed(self, repo_name: str) -> bool:
        """
        GET /api/user/{username}/project/{project_name}
        """
        url = f"{self.api}/api/user/{self.username}/project/{repo_name}"
        with requests.get(url, headers=self.headers) as r:
            if r.status_code == requests.codes.ok:
                data = r.json()
                return data["code"] == 0 and data["data"]["name"] == repo_name
            return False

    def create_repo(self, name: str, desc: str, is_private: bool) -> bool:
        raise PermissionError("Coding 不支持通过API创建仓库")

    def list_repos(self) -> list:
        """
        当前用户的项目列表
        https://open.coding.net/api-reference/%E9%A1%B9%E7%9B%AE.html#%E5%BD%93%E5%89%8D%E7%94%A8%E6%88%B7%E7%9A%84%E9%A1%B9%E7%9B%AE%E5%88%97%E8%A1%A8
        GET /api/user/projects?type=all&page=1&pageSize=10
        Response 包含 totalPage
        """
        url = f"{self.api}/api/user/projects"
        params = {
            "type": "all",
            "pageSize": 10,
            "page": 1
        }
        total_page = 1
        all_repos = []
        while True:
            if params["page"] > total_page:
                break

            with requests.get(url, headers=self.headers, params=params) as r:
                if r.status_code != requests.codes.ok:
                    raise RuntimeError(r.content.decode("utf-8"))

                data = r.json()
                if data["code"] != 0:
                    raise RuntimeError(data)

                total_page = data["data"]["totalPage"]
                params["page"] += 1

                repos = data["data"]["list"]
                for repo in repos:
                    if str.lower(repo["owner_user_name"]) == str.lower(self.username):
                        is_private = not repo["is_public"]
                        all_repos.append(dict(name=repo["name"],
                                              desc=repo["description"],
                                              is_private=is_private))
        return all_repos
