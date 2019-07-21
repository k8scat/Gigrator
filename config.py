# type Git服务器类型, 例如: gitee, github, gitlab, gitea, gogs, coding, bitbucket, 必填
# self_hosted 是否是自托管的Git服务器, 例如: gitlab, gitea, gogs, 默认为False
# username 所在Git服务器的用户名, 必填
# token 用户所在Git服务器的授权令牌, 必填
# url Git服务器的访问地址, 如果是自托管的Git服务器, 则需要设置url, 例如: https://git.example.com (包括具体协议: http/https), 默认为None

# 迁移源Git服务器配置
source = {
    'type': '',
    'self_hosted': False,
    'username': '',
    'token': '',
    'url': ''
}

# 迁移目的Git服务器配置
dest = {
    'type': '',
    'self_hosted': False,
    'username': '',
    'token': '',
    'url': ''
}