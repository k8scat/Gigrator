"""
author: K8sCat <k8scat@gmail.com>
link: https://github.com/k8scat/gigrator.git
"""
from gigrator.util import git_version
from gigrator.config import load_config, prepare_migrate
import argparse


def precheck():
    git_version()


def parse_args():
    parser = argparse.ArgumentParser(
        description="Git repositories migration tool.")
    parser.add_argument("-c", "--config", dest="cfg_file", default="./config.yml",
                        help="config file (default: ./config.yml)")
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    cfg = load_config(args.cfg_file)

    precheck()

    from_git, to_git, repos = prepare_migrate(cfg)
    for repo in repos:
        try:
            repo_dir = from_git.clone_repo(repo["name"], repo_owner=repo.get("owner", ""))
            if repo_dir:
                has_create = to_git.create_repo(name=repo["name"], desc=repo.get("desc", ""), is_private=repo.get("is_private", True))
                if has_create:
                    ok = to_git.push_repo(repo["name"], repo_dir)
                    if ok:
                        print(f"push {repo['name']} success")
                    else:
                        print(f"push {repo['name']} failed")
                else:
                    print(f"create {repo['name']} failed")
            else:
                print(f"clone {repo['name']} failed")
        except Exception as e:
            raise RuntimeError(e)


if __name__ == "__main__":
    main()
