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
            "Authorization": f"token {self.token}",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
        }
        self.use_web_api = config.get("use_web_api", False)
        self.web_headers = {
            "accept": "application/json",
            "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "cache-control": "no-cache",
            "content-type": "application/x-www-form-urlencoded;charset=UTF-8",
            "pragma": "no-cache",
            "priority": "u=1, i",
            "sec-ch-ua": '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
            "Cookie": config.get("web_cookie", ""),
        }
        self.is_org = config.get("is_org", False)
        if self.is_org:
            self.org_name = config.get("org_name", "")
            if not self.org_name:
                raise ValueError("org_name is required when is_org is true")

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

    def get_group_id_all(self) -> int:
        """获取 ”全部项目“ 的分组"""
        url = f"{self.api}/api/platform/project/groups/group?needProjectNum=true"
        with requests.get(url, headers=self.web_headers) as r:
            if r.status_code != requests.codes.ok:
                raise RuntimeError(r.content.decode("utf-8"))

            data = r.json()
            if data["code"] != 0:
                raise RuntimeError(data)

            groups = data["data"]
            for group in groups:
                if group.get("type") == "ALL":
                    return group["id"]
        return 0

    def list_projects(self) -> list:
        group_id = self.get_group_id_all()
        if group_id == 0:
            raise RuntimeError("获取 ”全部项目“ 的分组失败")

        url = f"{self.api}/api/platform/project/projects/search?page=1&pageSize=100&groupId={group_id}&type=JOINED&archived=false&sort=VISIT&order=DESC"

        with requests.get(url, headers=self.web_headers) as r:
            if r.status_code != requests.codes.ok:
                raise RuntimeError(r.content.decode("utf-8"))

            data = r.json()
            if data["code"] != 0:
                raise RuntimeError(data)

            result = []
            projects = data["data"]["list"]
            for project in projects:
                result.append(project["name"])
        return result

    def list_web_repos(self, project_name: str) -> list:
        url = f"{self.api}/api/user/{self.username}/project/{project_name}/depot-group/depots?type=ALL&sort=DEFAULT&sortDirection=DESC"

        with requests.get(url, headers=self.web_headers) as r:
            if r.status_code != requests.codes.ok:
                raise RuntimeError(r.content.decode("utf-8"))

            data = r.json()
            if data["code"] != 0:
                raise RuntimeError(data)
            
            repo_owner = f"{self.org_name}/{project_name}" if self.is_org else self.username

            result = []
            repos = data["data"]
            for repo in repos:
                result.append(
                    dict(
                        name=repo["name"],
                        owner=repo_owner,
                    )
                )
        return result

    def list_repos(self) -> list:
        """
        当前用户的项目列表
        https://open.coding.net/api-reference/%E9%A1%B9%E7%9B%AE.html#%E5%BD%93%E5%89%8D%E7%94%A8%E6%88%B7%E7%9A%84%E9%A1%B9%E7%9B%AE%E5%88%97%E8%A1%A8
        GET /api/user/projects?type=all&page=1&pageSize=10
        Response 包含 totalPage
        """
        
        all_repos = []
        
        if self.use_web_api:
            projects = self.list_projects()
            for project in projects:
                repos = self.list_web_repos(project)
                for repo in repos:
                    all_repos.append(repo)
            return all_repos
        
        url = f"{self.api}/api/user/projects"
        params = {"type": "all", "pageSize": 10, "page": 1}
        total_page = 1
        
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
                        all_repos.append(
                            dict(
                                name=repo["name"],
                                desc=repo["description"],
                                is_private=is_private,
                            )
                        )
        return all_repos
