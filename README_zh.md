# Gigrator

[en](./README.md) | zh

Git 仓库迁移助手

## 待做

* [ ] **[ADMIN]迁移整个Git服务器的仓库**
* [ ] 检测是否为空仓库(空仓库将导致推送失败)

## 支持

* [x] [码云](https://gitee.com/)
* [x] [GitLab](https://gitlab.com/)
* [x] [GitHub](https://github.com/)
* [x] [Gitea](https://gitea.io/zh-cn/)
* [x] [Coding](https://coding.net/)
* [x] [Gogs](https://gogs.io/)

注:
* **`Coding` 只支持迁出**
* 使用前请确认已在迁移源和目的Git服务器上添加了 `SSH Key`
* 目前只能迁移指定用户下的仓库, 即 `:username/:repo`, 不包括参与的或者组织的仓库
* 迁移包括commits、branches和tags, 不包括issues、pr和wiki
* 影响迁移速度的因素: Git服务器带宽、本地网速

## 基础环境

* Git
* Python

本人开发环境: `git version 2.20.1 (Apple Git-117)` + `Python 3.7.2`

## 依赖

* [Requests](https://2.python-requests.org/en/master/)

## 配置

[config.py](./config.py)

## 使用

```bash
# 安装 pipenv
pip install --user pipenv

# 拉取仓库
git clone git@github.com:hsowan/Gigrator.git
cd gigrator

# 初始化环境
pipenv --python 3
pipenv install

# 运行
pipenv run python gigrator.py

```

## 思路

1. 提供源Git服务器和目的Git服务器
2. 列出在源Git服务器的所有仓库
3. 选择需要迁移的仓库
4. 向目的Git服务器迁移所选仓库:
    1. 检查目的Git服务器是否有同名仓库
    2. 拉取源Git服务器的仓库
    3. 在目的Git服务器创建仓库
    4. 向目的Git服务器推送仓库
    
## 希望

希望大家可以尽情放肆地给这个项目提 **Issues/PR** :pray:

## 文档

### GitLab

* [GitLab API](https://docs.gitlab.com/ee/api/)
* [GitLab Create Repo](https://docs.gitlab.com/ee/api/projects.html#create-project)
* [Project visibility level](https://docs.gitlab.com/ee/api/projects.html#project-visibility-level)

### GitHub

* [GitHub API v3](https://developer.github.com/v3/)
* [GitHub Create Repo](https://developer.github.com/v3/repos/#create)
* [GitHub Personal Access Token](https://github.com/settings/tokens)

### 码云

* [Gitee OpenAPI](https://gitee.com/api/v5/swagger#/getV5ReposOwnerRepoStargazers?ex=no)
* [Gitee Personal Access Token](https://gitee.com/profile/personal_access_tokens)

### Gitea

* [Gitea API](https://gitea.com/api/v1/swagger)
* [Get a repo](https://gitea.com/api/v1/swagger#/repository/repoGet)
* [Create a repo](https://gitea.com/api/v1/swagger#/repository/createCurrentUserRepo)
* [List the repos that the authenticated user owns or has access to](https://gitea.com/api/v1/swagger#/user/userCurrentListRepos)

### Gogs

* [gogs/docs-api](https://github.com/gogs/docs-api)

### Coding

* [开放 API](https://open.coding.net/open-api/?_ga=2.122224323.99121124.1563808661-1235584671.1544277191)

## 开源许可协议

[MIT](https://github.com/hsowan/Gigrator/blob/master/LICENSE)

