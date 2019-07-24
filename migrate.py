import requests
import json
import os
from urllib import parse
from settings import repos_dir


def is_existed(server, repo_name):
    """
    检查Git服务器是否存在同名仓库

    :param server: Git服务器配置
    :param repo_name: 仓库名
    :return: bool
    """
    server_type = server['type']
    username = server['username']
    api = server['api']
    token = server['token']
    headers = server['headers']

    # 判断在目的Git服务器上是否已有同名的仓库
    # 有则不做迁移操作, 并进行提示
    check_url = ''
    if server_type == 'gitlab':
        # Get single project: GET /projects/:id
        # urlencode 需要加上safe='', / 就会转成%2F
        path = parse.quote(username + '/' + repo_name, safe='')
        check_url = api + '/projects/' + path
    elif server_type == 'github':
        # Get: GET /repos/:owner/:repo
        check_url = api + '/repos/' + username + '/' + repo_name
    elif server_type == 'gitee':
        # 获取用户的某个仓库: GET /repos/{owner}/{repo}
        # https://gitee.com/api/v5/swagger#/getV5ReposOwnerRepo
        check_url = api + '/repos/' + username + '/' + repo_name + '?access_token=' + token
    elif server_type == 'gitea' or server_type == 'gogs':
        # GET
        # ​/repos​/{owner}​/{repo}
        # Get a repository
        check_url = api + '/repos/' + username + '/' + repo_name

    r = requests.get(check_url, headers=headers)
    if r.status_code == 200:
        return True
    return False


def clone_repo(server, repo_name):
    """
    从Git服务器拉取仓库

    :param server: Git服务器的配置
    :param repo_name: 仓库名
    :return: str
    """

    # 不同用户的仓库存放在单独的目录下(基于repos_dir)
    clone_space = repos_dir + server['username'] + '/'
    if not os.path.isdir(clone_space):
        os.mkdir(clone_space)

    # 检查本地是否存在repo, 存在则删除
    repo_dir = clone_space + repo_name + '.git'
    if os.path.isdir(repo_dir):
        cmd = 'rm -rf ' + repo_dir
        if os.system(cmd) != 0:
            print('删除已有仓库失败')
            return None

    clone_cmd = 'cd ' + clone_space + ' && git clone --bare ' + server['ssh_prefix'] \
                + server['username'] + '/' + repo_name + '.git'

    if os.system(clone_cmd) != 0:
        return None

    return repo_dir


def create_repo(server, repo, source_type):
    """
    在Git服务器上创建仓库

    :param server: Git服务器配置
    :param repo: 完整的仓库信息
    :param source_type: 仓库所在源Git服务器的类型
    :return: bool
    """
    server_type = server['type']
    api = server['api']
    token = server['token']
    headers = server['headers']

    # 不同的Git服务器获取到的数据格式不一样, 所以在这里设置private
    if source_type == 'gitlab':
        private = True if repo['visibility'] == 'private' else False
    elif source_type == 'coding':
        private = repo['is_public']
    else:
        private = repo['private']

    # create repo through API
    create_repo_url = None
    data = None
    # GitLab
    # Create project for user: POST /projects/user/:user_id (status_code: 201)
    if server_type == 'gitlab':
        description = '' if repo['description'] is None else repo['description']
        visibility = 'private' if private else 'public'
        data = 'name=' + repo['name'] + '&description=' + description + '&visibility=' + visibility
        create_repo_url = api + '/projects'

    # GitHub
    # Create project for user: POST /user/repos (status_code: 201)
    elif server_type == 'github':
        json_data = {
            'name': repo['name'],
            'description': repo['description'],
            'private': private
        }
        data = json.dumps(json_data)
        create_repo_url = api + '/user/repos'

    # 创建一个仓库: POST /user/repos
    # https://gitee.com/api/v5/swagger#/postV5UserRepos
    elif server_type == 'gitee':
        json_data = {
            'access_token': token,
            'name': repo['name'],
            'description': repo['description'],
            'private': private,
            'has_issues': True,
            'has_wiki': True
        }
        data = json.dumps(json_data)
        create_repo_url = api + '/user/repos'

    elif server_type == 'gitea' or server_type == 'gogs':
        # POST
        # ​/user​/repos
        # Create a repository
        json_data = {
            "auto_init": False,
            'description': repo['description'],
            'name': repo['name'],
            'private': private
        }
        data = json.dumps(json_data)
        # bug
        # \u200b: 看不见的分隔符 Zero-width space
        # create_repo_url = config.gitea_api + '/user​/repos?access_token=' + config.gitea_token
        create_repo_url = api + '/user/repos'

    r = requests.post(create_repo_url, headers=headers, data=data)
    if r.status_code != 201:
        print(r.content.decode('utf-8'))
        return False
    return True


def push_repo(server, repo_name, repo_dir):
    """
    向Git服务器推送仓库

    :param server: Git服务器配置
    :param repo_name: 仓库名
    :param repo_dir: 仓库在本地的路径
    :return: bool
    """
    push_cmd = 'cd ' + repo_dir + ' && git push --mirror ' \
               + server['ssh_prefix'] + server['username'] + '/' + repo_name + '.git'
    return os.system(push_cmd) == 0


def migrate(repo, source, dest):
    """
    迁移单个仓库

    :param repo: 完整的仓库信息
    :param source: 源Git服务器配置
    :param dest: 目的Git服务器配置
    :return: bool
    """
    repo_name = repo['name']

    if is_existed(dest, repo_name):
        print('您所在目的Git服务已存在' + repo_name + '仓库! 故此仓库无法迁移')
        return False

    repo_dir = clone_repo(source, repo_name)
    if repo_dir is None:
        return False
    print('仓库拉取成功: ' + repo_name)

    if not create_repo(dest, repo, source['type']):
        return False
    print('仓库创建成功: ' + repo_name)

    if not push_repo(dest, repo_name, repo_dir):
        return False
    print('仓库推送成功: ' + repo_name)
    return True
