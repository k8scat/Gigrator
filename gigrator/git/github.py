"""
author: K8sCat <k8scat@gmail.com>
link: https://github.com/k8scat/gigrator.git
"""
from gigrator.git.git import Git
import requests


class Github(Git):
    def __init__(self, config: dict):
        super().__init__(config)
        self.headers = {
            "Authorization": "token " + self.token
        }

    def is_repo_existed(self, repo_name: str) -> bool:
        query = """
        query ($repo_owner: String!, $repo_name: String!) {
          repository(owner: $repo_owner, name: $repo_name) {
            id
          }
        }
        """
        variables = {
            "repo_owner": self.username,
            "repo_name": repo_name
        }
        payload = {
            "query": query,
            "variables": variables
        }
        with requests.post(self.api, json=payload, headers=self.headers) as r:
            if r.status_code != requests.codes.ok:
                raise RuntimeError(r.content.decode("utf-8"))

            data = r.json()
            try:
                return data["data"]["repository"].get("id", None) is not None
            except KeyError:
                return False

    def create_repo(self, name: str, desc: str, is_private: bool) -> bool:
        mutation = """
        mutation ($name: String!, $desc: String!, $isPrivate: RepositoryVisibility!) {
          createRepository(input: {name: $name, description: $desc, visibility: $isPrivate}) {
            clientMutationId
            repository {
              id
            }
          }
        }
        """
        variables = {
            "name": name,
            "desc": desc,
            "isPrivate": "PRIVATE" if is_private else "PUBLIC"
        }
        payload = {
            "query": mutation,
            "variables": variables
        }
        with requests.post(self.api, json=payload, headers=self.headers) as r:
            if r.status_code != requests.codes.ok:
                raise RuntimeError(r.content.decode("utf-8"))

            data = r.json()
            return "errors" not in data.keys()

    def list_repos(self) -> list:
        query = """
        query ($first: Int!, $after: String) {
          viewer {
            repositories(first: $first, after: $after, ownerAffiliations: [OWNER]) {
              edges {
                node {
                  name
                  isPrivate
                  description
                }
                cursor
              }
              pageInfo {
                hasNextPage
              }
            }
          }
        }
        """
        variables = {
            "first": 100
        }
        payload = {
            "query": query,
            "variables": variables
        }

        all_repos = []
        def parse_data(data):
            repos = data["data"]["viewer"]["repositories"]["edges"]
            for repo in repos:
                repo = repo["node"]
                all_repos.append(dict(name=repo["name"],
                                      desc=repo["description"],
                                      is_private=repo["isPrivate"]))
        while True:
            with requests.post(self.api, json=payload, headers=self.headers) as r:
                if r.status_code != requests.codes.ok:
                    raise RuntimeError(r.content.decode("utf-8"))

                data = r.json()
                try:
                    parse_data(data)
                    has_next_page = data["data"]["viewer"]["repositories"]["pageInfo"]["hasNextPage"]
                    if not has_next_page:
                        break

                    variables["after"] = data["data"]["viewer"]["repositories"]["edges"][-1]["cursor"]
                    payload = {
                        "query": query,
                        "variables": variables
                    }
                except Exception as e:
                    print(data)
                    raise RuntimeError(e)
        return all_repos
