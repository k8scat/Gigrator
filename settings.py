# -*- coding: utf-8 -*-

"""
@author: hsowan <hsowan.me@gmail.com>
@date: 2020/2/10

"""
import os

# type Git服务器类型, 例如: gitee, github, gitlab, gitea, gogs, coding, 必填
# username 所在Git服务器的用户名, 必填
# token 用户所在Git服务器的授权令牌, 必填
# url Git服务器的访问地址, 例如: https://git.example.com (包括具体协议: http/https)
# 需要设置url的Git服务器有: gitlab, gitea, gogs, 其他Git服务器默认为空即可
# 源Git服务器配置
SOURCE_GIT = {
    'type': '',
    'username': '',
    'token': '',
    'url': ''
}
# 目的Git服务器配置
DEST_GIT = {
    'type': 'gitlab',
    'username': 'hsowan',
    'token': '8MUV39-3fHTyn5-Vf2n6',
    'url': 'https://git.ncucoder.com'
}

# 支持的Git服务器
SUPPORT_GITS = ['gitlab', 'github', 'gitee', 'gitea', 'coding', 'gogs', 'gf']

# 仓库暂存目录
TEMP_DIR = os.path.join(os.path.dirname(__file__), '.repos')

# GitLab
GITLAB_API_VERSION = '/api/v4'

# GitHub
# 暂不支持GitHub Enterprise
GITHUB_API = 'https://api.github.com/graphql'
GITHUB_SSH_PREFIX = 'git@github.com:'

# 码云
GITEE_API = 'https://gitee.com/api/v5'
GITEE_SSH_PREFIX = 'git@gitee.com:'

# Coding
# 暂不支持私有部署
CODING_SSH_PREFIX = 'git@e.coding.net:'

# Gitea/Gogs
GITEA_API_VERSION = '/api/v1'


#工蜂私有化部署
#GF_SSH_PREFIX = 'git@git.xxx.com'
#GF_API = 'https://git.xxx.com/api/v3'

#腾讯工蜂
GF_SSH_PREFIX = 'git@code.tencent.com'
GF_API = 'https://code.tencent.com/api/v3'