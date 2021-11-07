"""
author: K8sCat <k8scat@gmail.com>
link: https://github.com/k8scat/gigrator.git
"""
import os
import re
import subprocess


class Git:
    provider = ""
    username = ""
    token = ""
    api = ""
    ssh_prefix = ""
    https_prefix = ""
    use_https = False
    headers = {}

    def __init__(self, config: dict):
        self.provider = config.get("provider", "").lower()
        if self.provider == "gogs":
            self.provider = "gitea"
        if not self.provider:
            raise ValueError("Invalid provider")

        self.username = config.get("username", "")
        if not self.username:
            raise ValueError("Invalid username")

        self.token = config.get("token", "")
        if not self.token:
            raise ValueError("Invalid token")

        self.ssh_prefix = config.get("ssh_prefix", "")
        if self.ssh_prefix.endswith(":"):
            self.ssh_prefix = self.ssh_prefix.rstrip(":")

        self.https_prefix = config.get("https_prefix", "")
        if self.https_prefix.endswith("/"):
            self.https_prefix = self.https_prefix.rstrip("/")
        self.https_prefix_auth = self._https_prefix_auth()

        self.use_https = config.get("use_https", False)

        self.api = config.get("api", "")
        if self.api:
            if not re.match(r"^http(s)?://.+$", self.api):
                raise ValueError("Invalid api")
            self.api = self.api.rstrip("/")

        self.clone_dir = config.get("clone_dir", "")
        if not self.clone_dir:
            self.clone_dir = os.path.join(os.getcwd(),
                                          ".gigrator",
                                          self.provider)
        else:
            self.clone_dir = os.path.join(self.clone_dir,
                                          self.provider)
        os.makedirs(self.clone_dir, exist_ok=True)

    def _https_prefix_auth(self) -> str:
        parts = self.https_prefix.split("://")
        schema = parts[0]
        domain = parts[1]
        return f"{schema}://{self.username}:{self.token}@{domain}"

    def clone_repo(self, repo_name: str, repo_owner: str = "") -> str:
        if not repo_owner:
            repo_owner = self.username
        remote_addr = f"{self.ssh_prefix}:{repo_owner}/{repo_name}.git"

        if self.use_https:
            remote_addr = f"{self.https_prefix_auth}/{repo_owner}/{repo_name}.git"

        clone_cmd = ["git", "clone", "--bare", remote_addr]
        ret = subprocess.run(args=clone_cmd,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             encoding="utf-8",
                             cwd=self.clone_dir)
        if ret.returncode == 0:
            return os.path.join(self.clone_dir, repo_name + ".git")
        print(ret.stderr, end='')
        return None

    def push_repo(self, repo_name: str, repo_dir: str, repo_owner: str) -> bool:
        if not repo_owner:
            repo_owner = self.username
        remote_addr = f"{self.ssh_prefix}:{repo_owner}/{repo_name}.git"

        if self.use_https:
            remote_addr = f"{self.https_prefix_auth}/{repo_owner}/{repo_name}.git"

        clone_cmd = ["git", "push", "--mirror", remote_addr]
        ret = subprocess.run(args=clone_cmd,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             encoding="utf-8",
                             cwd=self.clone_dir)
        if ret.returncode == 0:
            return os.path.join(self.clone_dir, repo_name + ".git")
        print(ret.stderr, end='')
        return None

    def list_repos(self) -> list:
        raise NotImplementedError

    def create_repo(self, name: str, desc: str, is_private: bool) -> bool:
        raise NotImplementedError

    def is_repo_existed(self, repo_name: str) -> bool:
        raise NotImplementedError
