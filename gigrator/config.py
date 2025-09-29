"""
author: K8sCat <k8scat@gmail.com>
link: https://github.com/k8scat/gigrator.git
"""
import yaml
from gigrator.git.git import Git
from gigrator.git import gitlab, github, gitee, gitea, coding, gongfeng

# https://pyyaml.org/wiki/PyYAMLDocumentation
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


def load_config(cfg_file: str) -> dict:
    with open(cfg_file, "r") as f:
        cfg = yaml.load(f, Loader=Loader)

    return cfg


def git_factory(cfg: dict) -> Git:
    provider = cfg.get("provider", "")
    if not provider:
        raise RuntimeError("Invalid provider")

    if provider == "gitlab":
        return gitlab.Gitlab(cfg)
    if provider == "github":
        return github.Github(cfg)
    if provider == "coding":
        return coding.Coding(cfg)
    if provider in ["gitea", "gogs"]:
        return gitea.Gitea(cfg)
    if provider == "gitee":
        return gitee.Gitee(cfg)
    if provider == "gf":
        return gongfeng.GF(cfg)

    raise ValueError(f"Invalid provider: {provider}")


def prepare_migrate(cfg: dict):
    migrate_cfg = cfg.get("migrate", None)
    if not migrate_cfg:
        raise RuntimeError("Invalid migrate")

    # 源 Git
    migrate_from = migrate_cfg.get("from", None)
    if not migrate_from:
        raise RuntimeError("Invalid migrate.from")
    migrate_from_cfg = cfg.get(migrate_from, None)
    if not migrate_from_cfg:
        raise ValueError("Not found: migrate.from cfg")
    from_git = git_factory(migrate_from_cfg)
    
    # 目标 Git
    migrate_to = migrate_cfg.get("to", None)
    if not migrate_to:
        raise RuntimeError("Invalid migrate.to")
    migrate_to_cfg = cfg.get(migrate_to, None)
    if not migrate_to_cfg:
        raise ValueError("Not found: migrate.to cfg")
    to_git = git_factory(migrate_to_cfg)

    all_repos = from_git.list_repos()
    repos = []
    cfg_repos = migrate_cfg.get("repos", [])
    if len(cfg_repos) == 0:
        repos = all_repos
    else:
        for repo in all_repos:
            for repo_name in cfg_repos:
                if repo["name"] == repo_name:
                    repos.append(repo)

    return from_git, to_git, repos
