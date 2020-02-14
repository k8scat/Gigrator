# GitHub 配置
GITHUB = {
    'type': 'github',
    'username': 'your_username',
    'token': 'your_token',
    'url': ''  # 不用填写
}

# Gitee
GITEE = {
    'type': 'gitee',
    'username': 'your_username',
    'token': 'your_token',
    'url': ''  # 不用填写
}

# GitLab
GITLAB = {
    'type': 'gitlab',
    'username': 'your_username',
    'token': 'your_token',
    'url': 'https://git.your_domain.com'  # Git服务器地址
}

# Gitea/Gogs,
GITEA_OR_GOGS = {
    'type': 'gitea',  # Gitea和Gogs都填写gitea即可
    'username': 'your_username',
    'token': 'your_token',
    'url': 'https://git.your_domain.com'  # Git服务器地址
}

# Coding
CODING = {
    'type': 'coding',  # Gitea和Gogs都填写gitea即可
    'username': 'your_username',  # username即Coding地址的二级域名, 例如我的Coding地址是https://hsowan.coding.net, hsowan就是我的username
    'token': 'your_token',
    'url': 'https://git.your_domain.com'  # Git服务器地址
}
