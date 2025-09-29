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

        self.enterprise_id = config.get("enterprise_id", "")

    def list_repos(self) -> list:
        """
        获取授权用户参与的仓库列表
        GET https://api.gitee.com/enterprises/{enterprise_id}/projects

        https://gitee.com/api/v8/swagger#/getEnterpriseIdProjects
        """
        url = f"{self.base_api}/{self.enterprise_id}/projects"
        print(f"List repos: {url}")
        params = {
            "access_token": self.token,
            "per_page": 100,
            "page": 1
        }
        all_repos = []
        while True:
            with requests.get(url, headers=self.headers, params=params) as r:
                if r.status_code != requests.codes.ok:
                    raise RuntimeError(r.content.decode("utf-8"))
                
                print(r.text)

                repos = r.json().get("data", [])
                if len(repos) == 0:
                    break

                for repo in repos:
                    all_repos.append(dict(name=repo["path_with_namespace"],
                                          desc=repo["description"],
                                          is_private=True))
                params["page"] += 1
        return all_repos
