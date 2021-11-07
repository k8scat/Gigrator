"""
author: K8sCat <k8scat@gmail.com>
link: https://github.com/k8scat/gigrator.git
"""
from urllib.parse import urlencode
import requests
from gigrator.git.git import Git


class GF(Git):
    def __init__(self, config: dict):
        super().__init__(config)
        self.headers = {
            "PRIVATE-TOKEN": self.token
        }

    def is_repo_existed(self, repo_name: str) -> bool:
        # repo_name如果包含命名空间需要URL编码
        repo_name_encoded = urlencode(repo_name)
        url = f"{self.api}/projects/{repo_name_encoded}/repository/tree"
        with requests.get(url, headers=self.headers) as r:
            return r.status_code == requests.codes.ok

    # repo_name = name_with_namespace
    def create_repo(self, repo_name: str, desc: str, is_private: bool) -> bool:
        url = f"{self.api}/projects"
        repo_full_name_list = repo_name.split("/")
        if len(repo_full_name_list) == 1:
            repo_name_namespace = ""
            repo_name_short = repo_name
        else:
            repo_name_namespace = repo_full_name_list[0]
            repo_name_short = repo_full_name_list[1]
        visibility_level = 0 if is_private else 10
        payload = {
            "name": repo_name_short,
            "namespace_id": repo_name_namespace,
            "description": desc,
            "visibility_level": visibility_level
        }
        with requests.post(url, headers=self.headers, json=payload) as r:
            return r.status_code == requests.codes.ok or r.status_code == requests.codes.created

    def list_repos(self) -> list:
        list_groups_url = f"{self.api}/groups"
        all_repos = []
        with requests.get(list_groups_url, headers=self.headers) as r:
            if r.status_code != requests.codes.ok:
                raise RuntimeError(r.content.decode("utf-8"))

            all_groups = []
            groups = r.json()
            for group in groups:
                all_groups.append(group["id"])

            for group_id in all_groups:
                group_detail_url = f"{list_groups_url}/{str(group_id)}"
                with requests.get(group_detail_url, headers=self.headers) as r:
                    if r.status_code != requests.codes.ok:
                        raise RuntimeError(r.content.decode("utf-8"))

                    group_detail = r.json()
                    for repo in group_detail["projects"]:
                        is_private = not repo["public"]
                        all_repos.append(dict(name=repo["name_with_namespace"],
                                              desc=repo["description"],
                                              is_private=is_private))
        return all_repos
