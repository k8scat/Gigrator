# 开发手册

## 新增其他Git平台

```python
# Base class
class Git:
    pass

# Other GitServer class should inherit Git
class OtherGit(Git):
    pass
```

## Dependencies

* [Requests](https://2.python-requests.org/en/master/)

## References

### GitLab

* [GitLab API Docs](https://docs.gitlab.com/ee/api/)
* [GitLab Create Repo](https://docs.gitlab.com/ee/api/projects.html#create-project)
* [Project visibility level](https://docs.gitlab.com/ee/api/projects.html#project-visibility-level)

## [GitLab GraphQL API](https://docs.gitlab.com/ee/api/graphql/)

Can not create a project!

It will co-exist with the current v4 REST API. If we have a v5 API, this should be a compatibility layer on top of GraphQL.

* [Introduction to GraphQL](https://developer.github.com/v4/guides/intro-to-graphql/)
* [GraphQL API Resources](https://docs.gitlab.com/ee/api/graphql/reference/index.html)

### [GitHub REST API v3](https://developer.github.com/v3/)

* [GitHub Create Repo](https://developer.github.com/v3/repos/#create)
* [GitHub Personal Access Token](https://github.com/settings/tokens)

## [GitHub GraphQL API v4](https://developer.github.com/v4/)

* [GraphQL resource limitations](https://developer.github.com/v4/guides/resource-limitations/)
* [Forming Calls with GraphQL](https://developer.github.com/v4/guides/forming-calls/)


### Gitee

* [Gitee OpenAPI](https://gitee.com/api/v5/swagger#/getV5ReposOwnerRepoStargazers?ex=no)
* [Gitee Personal Access Token](https://gitee.com/profile/personal_access_tokens)

### Gitea

* [Gitea API](https://gitea.com/api/v1/swagger)
* [Get a repo](https://gitea.com/api/v1/swagger#/repository/repoGet)
* [Create a repo](https://gitea.com/api/v1/swagger#/repository/createCurrentUserRepo)
* [List the repos that the authenticated user owns or has access to](https://gitea.com/api/v1/swagger#/user/userCurrentListRepos)

### Gogs

* [gogs/docs-api](https://github.com/gogs/docs-api)
* [Demo site](https://try.gogs.io/)

### Coding

* [Open API](https://open.coding.net/open-api/?_ga=2.122224323.99121124.1563808661-1235584671.1544277191)

### GF (腾讯工蜂)

* [Open API](https://code.tencent.com/help/api/prepare)

### GraphQL Client

* [sgqlc](https://github.com/profusion/sgqlc)
