"""
author: K8sCat <k8scat@gmail.com>
link: https://github.com/k8scat/gigrator.git
"""
from gigrator.util import git_version
from gigrator.config import load_config
import argparse
from gigrator.git.git import Git
from gigrator.git import gitlab, github, gitee, gitea, coding, gongfeng


def precheck():
    git_version()


def parse_args():
    parser = argparse.ArgumentParser(
        description="Git repositories migration tool.")
    parser.add_argument("-c", "--config", dest="cfg_file", default="./config.yml",
                        help="config file (default: ./config.yml)")
    args = parser.parse_args()
    return args


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


def main():
    args = parse_args()
    cfg = load_config(args.cfg_file)

    precheck()

    migrate = cfg.get("migrate", None)
    if not migrate:
        raise RuntimeError("Invalid migrate")

    migrate_from = migrate.get("from", None)
    if not migrate_from:
        raise RuntimeError("Invalid migrate.from")
    migrate_to = migrate.get("to", None)
    if not migrate_to:
        raise RuntimeError("Invalid migrate.to")

    migrate_from_cfg = cfg.get(migrate_from, None)
    if not migrate_from_cfg:
        raise ValueError("Not found: migrate.from cfg")
    migrate_to_cfg = cfg.get(migrate_to, None)
    if not migrate_to_cfg:
        raise ValueError("Not found: migrate.to cfg")

    migrate_from_git = git_factory(migrate_from_cfg)
    migrate_to_git = git_factory(migrate_to_cfg)

    all_repos = migrate_from_git.list_repos()
    repos = []
    migrate_repos = migrate.get("repos", [])
    if len(migrate_repos) == 0:
        repos = all_repos
    else:
        for repo in all_repos:
            for repo_name in migrate_repos:
                if repo["name"] == repo_name:
                    repos.append(repo)
    for repo in repos:
        try:
            repo_dir = migrate_from_git.clone_repo(repo["name"])
            if repo_dir:
                has_create = migrate_to_git.create_repo(**repo)
                if has_create:
                    migrate_to_git.push_repo(repo["name"], repo_dir)
        except Exception as e:
            raise RuntimeError(e)


if __name__ == "__main__":
    main()
