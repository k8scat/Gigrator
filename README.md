# Gigrator

Migrate repos from one GitServer to another.

## 支持

* [x] GitLab
* [x] GitHub
* [ ] 码云
* [ ] Gitea

## 配置

在项目下新建一个文件`config.py`, 不同Git服务器必须有以下五个属性配置:

* 服务器地址
* API
* 授权令牌
* 用户名
* SSH(前缀)

参考配置:

```py
# GitLab 服务器地址
gitlab = 'https://git.xxx.com'
# GitLab API
gitlab_api = 'https://git.xxx.com/api/v4'
# GitLab 授权令牌
gitlab_token = ''
# GitLab 用户名
gitlab_username = 'hsowan'
# GitLab SSH
gitlab_ssh = 'git@git.xxx.com:'

# Git 服务器地址(不用修改)
github = 'https://github.com'
# GitHub API(不用修改)
github_api = 'https://api.github.com'
# GitHub 授权令牌
github_token = ''
# GitHub 用户名
github_username = 'hsowan'
# GitHub SSH(不用修改)
github_ssh = 'git@github.com:'

```

## 使用

```bash
# 安装 pipenv
pip install --user pipenv

git clone git@github.com:hsowan/Gigrator.git
cd gigrator

# 初始化环境
pipenv --python 3
pipenv install

pipenv run python gigrator.py

```

## 思路

1. 提供源Git服务器和目的Git服务器
2. 列出用户在其中源Git服务器的所有仓库
3. 选择需要迁移的仓库
4. 向目的Git服务器迁移所选仓库

## Packages

* [Requests](https://2.python-requests.org/en/master/)

## Servers

### GitLab

* [GitLab API](https://docs.gitlab.com/ee/api/)
* [GitLab Create Repo](https://docs.gitlab.com/ee/api/projects.html#create-project)
* [GitLab Personal Access Token](https://gitlab.com/profile/personal_access_tokens)
* [Project visibility level](https://docs.gitlab.com/ee/api/projects.html#project-visibility-level)

### GitHub

* [GitHub API v3](https://developer.github.com/v3/)
* [GitHub Create Repo](https://developer.github.com/v3/repos/#create)
* [GitHub Personal Access Token](https://github.com/settings/tokens)

### 码云

* [Gitee OpenAPI](https://gitee.com/api/v5/swagger#/getV5ReposOwnerRepoStargazers?ex=no)
* [Gitee Personal Access Token](https://gitee.com/profile/personal_access_tokens)

### Gitea

* [Gitea API](https://try.gitea.io/api/swagger#/)

## License

MIT

