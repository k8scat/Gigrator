# Gigrator

Gigrator 是一个 Git 代码仓批量迁移工具，支持众多流行的代码托管平台，包括 GitHub、码云（Gitee）、GitLab、Gitea、Coding、Gogs、腾讯工蜂，同时可以基于本项目进行拓展其他代码托管平台。

## 支持的平台

- [x] [Gitee](https://gitee.com/)
- [x] [GitLab](https://gitlab.com/)
- [x] [GitHub](https://github.com/)
- [x] [Gitea](https://gitea.io/zh-cn/)
- [x] [Coding](https://coding.net/)
- [x] [Gogs](https://gogs.io/)
- [x] [腾讯工蜂](https://code.tencent.com/)
- [ ] [Bitbucket](https://bitbucket.org/)
- [ ] [云效 Codeup](https://codeup.aliyun.com/)

说明：

- 暂不支持迁移至 `Coding`，可从 Coding 迁移至其他 `Git` 服务器
- 由于 `Coding` 的升级，其基础 `API` 不再是 `https://coding.net`，而改为: `https://{username}.coding.net`
- 迁移前请确认已在Git服务器上添加 `SSH Key`
- 只能迁移指定用户下的仓库，即 `{username}/{repo_name}`，不包括参与的或者组织的仓库
- 迁移包括commits、branches和tags，不包括issues、pr和wiki

## 安装

### pip 安装

```bash
pip install gigrator
```

### 源码安装

```shell script
git clone https://github.com/k8scat/gigrator.git
cd gigrator
make
```

## 使用

### 环境要求

- Git
- Python3

### 配置文件

参考 [config.yml](./config.yml)

### 运行

```bash
gigrator -c config.yml
```

## 扩展更多平台

基于 `Git` 类实现其他平台的代码仓迁移

```python
class Git:
    def list_repos(self) -> list:
        raise NotImplementedError

    def create_repo(self, name: str, desc: str, is_private: bool) -> bool:
        raise NotImplementedError

    def is_repo_existed(self, repo_name: str) -> bool:
        raise NotImplementedError
```

## 贡献

<a href="https://github.com/k8scat/gigrator/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=k8scat/gigrator" />
</a>

Note:

* 不支持迁移至 `Coding`, 可从 Coding 迁移至其他 `Git` 服务器
* 由于 `Coding` 的升级, 其基础 `API` 不再是 `https://coding.net`, 而改为: `https://{username}.coding.net`
* 迁移前请确认已在Git服务器上添加 `SSH Key`
* 只能迁移指定用户下的仓库, 即 `{username}/{repo_name}`, 不包括参与的或者组织的仓库
* 迁移包括commits、branches和tags, 不包括issues、pr和wiki

## 环境

* Git
* Python

开发环境: `git version 2.20.1 (Apple Git-117)` + `Python 3.7.2`

## 开发手册

[开发手册](./dev.md)

## 开源协议

[MIT](./LICENSE)
