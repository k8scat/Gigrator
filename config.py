# type Git服务器类型, 例如: gitee, github, gitlab, gitea, gogs, coding, 必填
# username 所在Git服务器的用户名, 必填
# token 用户所在Git服务器的授权令牌, 必填
# url Git服务器的访问地址, 例如: https://git.example.com (包括具体协议: http/https)
# 需要设置url的Git服务器有: gitlab, gitea, gogs, 其他Git服务器默认为空即可

# 迁移源Git服务器配置
source = {
    'type': '',
    'username': '',
    'token': '',
    'url': ''
}

# 迁移目的Git服务器配置
dest = {
    'type': '',
    'username': '',
    'token': '',
    'url': ''
}
