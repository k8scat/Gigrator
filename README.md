# Gigrator

## GitHub Action 来了: [action-mirror-git](https://github.com/k8scat/action-mirror-git) 镜像同步 Git 仓库

[![](https://img.shields.io/badge/GitHub-success)](https://github.com/k8scat/gigrator)
[![](https://img.shields.io/badge/Gitee-red)](https://gitee.com/k8scat/gigrator)

Gigrator 是一个 Git 代码仓批量迁移工具，支持多种 Git 平台，包括 Gitee、GitLab、GitHub、Gitea、Coding、Gogs 和腾讯工蜂，同时支持自行扩展更多 Git 平台。

![gigrator.png](images/gigrator.png)

## 快速开始

```shell script
git clone https://github.com/k8scat/gigrator.git
cd gigrator
pip3 install -r requirements.txt

# 迁移前需在配置文件(settings.py)中配置 SOURCE_GIT 和 DEST_GIT
# 配置参考: settings_example.py
python3 gigrator.py
```

## 支持平台

* [x] [Gitee](https://gitee.com/)
* [x] [GitLab](https://gitlab.com/)
* [x] [GitHub](https://github.com/)
* [x] [Gitea](https://gitea.io/zh-cn/)
* [x] [Coding](https://coding.net/)
* [x] [Gogs](https://gogs.io/)
* [x] [腾讯工蜂](https://code.tencent.com/)
* [ ] [Bitbucket](https://bitbucket.org/)

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

## 交流群

<img src="./images/weixin.png" alt="交流群" width="300" height="auto">

> 二维码失效可添加微信 「kennn007」，请备注「Gigrator」。
