import requests
import config as config
import json
import os
import sys
from urllib import parse

# 支持的Git服务器
support = ['gitlab', 'github', 'gitee', 'gitea', 'coding']

# 仓库存放目录
repos_dir = os.getcwd() + '/repos/'


def list_repos(server):
    """
    列出指定用户在Git服务器上拥有的所有的仓库(owner)

    :param server: Git服务器配置
    :return: 仓库列表
    """
    server_type = server['type']
    api = server['api']
    username = server['username']
    token = server['token']
    headers = server['headers']

    # 定义最终返回的所有仓库集合
    # 使用extend添加另一个列表
    all_repos = []
    page = 1
    list_repos_url = ''
    if server_type == 'gitlab':
        # GitLab
        # List user projects: GET /users/:user_id/projects (需要分页: ?page=1)
        # 不存在401的问题: 会返回公开的仓库
        list_repos_url = api + '/users/' + username + '/projects?page='

    elif server_type == 'github':
        # GitHub
        # Get: Get /repos/:owner/:repo (通过Get判断仓库是否已存在)
        # List your repositories: GET /user/repos (需要分页: ?page=1)
        list_repos_url = api + '/user/repos?type=owner&page='
    elif server_type == 'gitee':
        # Gitee
        # 列出授权用户的所有仓库: GET /user/repos
        # https://gitee.com/api/v5/swagger#/getV5UserRepos
        list_repos_url = api + '/user/repos?access_token=' + token \
                         + '&type=personal&sort=full_name&per_page=100&page='

    elif server_type == 'gitea':
        # GET
        # ​/user​/repos
        # List the repos that the authenticated user owns or has access to
        # gitea没有做分页: https://github.com/go-gitea/gitea/issues/7515
        list_repos_url = api + '/user/repos?access_token=' + token

        r = requests.get(list_repos_url, headers=headers)
        repos = json.loads(r.content.decode('utf-8'))

        for repo in repos:
            if repo['owner']['username'] != username:
                repos.remove(repo)
            else:
                print(repo['name'])

        print('总共' + str(len(repos)) + '个仓库')
        return repos

    elif server_type == 'coding':
        # 当前用户的项目列表
        # GET /api/user/projects?type=all&amp;page={page}&amp;pageSize={pageSize}
        # Response totalPage?
        list_repos_url = api + '/api/user/projects?type=all&pageSize=10&page='

        r = requests.get(list_repos_url + str(page), headers=headers)
        content = json.loads(r.content.decode('utf-8'))
        totalPage = content['data']['totalPage']
        repos = content['data']['list']
        if len(repos) == 0:
            return None
        for repo in repos:
            if repo['owner_user_name'] == username:
                all_repos.append(repo)

        while page < totalPage:
            page += 1
            r = requests.get(list_repos_url + str(page), headers=headers)
            content = json.loads(r.content.decode('utf-8'))
            repos = content['data']['list']
            for repo in repos:
                if repo['owner_user_name'] == username:
                    all_repos.append(repo)

        for repo in all_repos:
            print(repo['name'])
        print('总共' + str(len(all_repos)) + '个仓库')
        return all_repos

    # 当没有授权时, 可能只会返回公开项目(至少gitlab会)
    while True:
        r = requests.get(list_repos_url + str(page), headers=headers)
        if r.status_code == 200:
            repos = json.loads(r.content.decode('utf-8'))
            print(r.content.decode('utf-8'))
            if len(repos) == 0:
                break
            all_repos.extend(repos)
            page += 1
        elif r.status_code == 401:
            print('授权令牌无效')
            return None
        else:
            print(r.content.decode('utf-8'))
            return None

    # 打印仓库名
    for repo in all_repos:
        print(repo['name'])
    print('总共' + str(len(all_repos)) + '个仓库')
    return all_repos


def is_existed(server, repo_name):
    """
    检查Git服务器是否存在同名仓库

    :param server: Git服务器配置
    :param repo_name: 仓库名
    :return: 是否存在同名仓库
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
    elif server_type == 'gitea':
        # GET
        # ​/repos​/{owner}​/{repo}
        # Get a repository
        check_url = api + '/repos/' + username + '/' + repo_name + '?access_token=' + token

    r = requests.get(check_url, headers=headers)
    if r.status_code == 200:
        return True
    return False


def clone_repo(server, repo_name):
    """
    从Git服务器拉取仓库

    :param server: Git服务器的配置
    :param repo_name: 仓库名
    :return: 仓库在本地的路径
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
    :return: 是否成功创建仓库
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

    elif server_type == 'gitea':
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
        create_repo_url = api + '/user/repos?access_token=' + token

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
    :return: 是否成功推送仓库
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
    :return: 1表示将终止所有迁移, 2表示单个仓库迁移失败
    """
    repo_name = repo['name']

    if is_existed(dest, repo_name):
        print('您所在目的Git服务已存在' + repo_name + '仓库! 故此仓库无法迁移')
        return 2

    repo_dir = clone_repo(source, repo_name)
    if repo_dir is None:
        print('请确认源Git服务器已经添加SSH Key')
        return 1
    else:
        print('仓库拉取成功: ' + repo_name)

    if not create_repo(dest, repo, source['type']):
        return 1
    else:
        print('仓库创建成功: ' + repo_name)

    if not push_repo(dest, repo_name, repo_dir):
        print('请确认目的Git服务器已经添加SSH Key')
        return 1
    else:
        print('仓库推送成功: ' + repo_name)


def autoconfig(config):
    """
    检查Git服务器的配置(config.py):
    type: Git服务器的类型, 必填
    username: 用户名, 必填
    token: 授权令牌(Access Token), 必填
    self_hosted: 是否自托管(bool), 默认False
    url: 如果是自托管的Git服务器, 需要设置该项, 默认为''
    api: 自动配置
    ssh_prefix: 自动配置
    headers: 自动配置

    :param config: 基本配置信息
    :return: 完整的配置信息
    """
    # 防止出现配置时大小写的问题
    config['type'] = config['type'].lower()
    server_type = config['type']
    username = config['username']
    token = config['token']
    self_hosted = config['self_hosted']
    if server_type == '' or server_type is None:
        print('没有配置type')
        return None
    if username == '' or username is None:
        print('没有配置username')
        return None
    if token == '' or token is None:
        print('没有配置token')
        return None

    if server_type not in support:
        print('暂不支持此类型的Git服务器: ' + server_type)
        return None

    url = None
    if self_hosted:
        url = config['url']
        if url is None or url == '':
            print('自托管的Git服务器需要设置访问地址 url')
            return None

    if server_type == 'github':
        config['ssh_prefix'] = 'git@github.com:'
        config['api'] = 'https://api.github.com'
        config['headers'] = {
            'Authorization': 'token ' + config['token']
        }

    elif server_type == 'gitee':
        config['ssh_prefix'] = 'git@gitee.com:'
        config['api'] = 'https://gitee.com/api/v5'
        config['headers'] = {
            'Content-Type': 'application/json;charset=UTF-8'
        }

    elif server_type == 'gitlab':
        config['headers'] = {
            'PRIVATE-TOKEN': config['token']
        }
        if self_hosted:
            config['ssh_prefix'] = 'git@' + url.split('://')[1] + ':'
            config['api'] = url + '/api/v4'
        else:
            config['ssh_prefix'] = 'git@gitlab.com:'
            config['api'] = 'https://gitlab.com/api/v5'

    elif server_type == 'gitea':
        config['headers'] = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        if self_hosted:
            config['ssh_prefix'] = 'git@' + url.split('://')[1] + ':'
            config['api'] = url + '/api/v1'
        else:
            config['ssh_prefix'] = 'git@gitea.com:'
            config['api'] = 'https://gitea.com/api/v1'

    elif server_type == 'coding':
        config['headers'] = {
            'Authorization': 'token ' + config['token']
        }
        config['ssh_prefix'] = 'git@git.dev.tencent.com:'
        config['api'] = 'https://coding.net'

    return config


if __name__ == "__main__":

    print('检查目的Git服务器配置...')
    dest = autoconfig(config.dest)
    if dest is None:
        sys.exit(0)
    if dest['type'] == 'coding':
        print('不支持迁入Coding')
        sys.exit(0)
    elif dest['type'] == 'bitbucket':
        print('不支持迁入Bitbucket')
        sys.exit(0)

    print('检查源Git服务器配置...')
    source = autoconfig(config.source)
    if source is None:
        sys.exit(0)

    # 创建repo临时目录
    if not os.path.isdir(repos_dir):
        os.mkdir(repos_dir)

    # 列出在源Git服务器上所有的仓库
    repos = list_repos(source)
    # 没有仓库的话直接退出
    if len(repos) == 0:
        sys.exit(0)

    # 输入需要迁移的仓库
    migrate_repos = input('请指定需要迁移的仓库(例如: repo1_name, repo2_name, 默认迁移所有仓库): ').replace(' ', '').split(',')

    success_count = 0
    failed_repos = []
    # 迁移所有仓库
    if len(migrate_repos) == 1 and migrate_repos[0] == '':
        print('开始迁移所有仓库')
        for repo in repos:
            r = migrate(repo=repo, source=source, dest=dest)
            if r == 1:
                print('终止所有迁移')
                sys.exit(0)
            elif r == 2:
                print(repo['name'] + ' 仓库迁移失败')
                failed_repos.append(repo['name'])
            else:
                print('仓库 ' + repo['name'] + ' 迁移成功!')
                success_count += 1
            break

    # 迁移指定仓库
    else:
        print('开始迁移指定仓库')
        # 循环进行仓库迁移
        for migrate_repo in migrate_repos:
            for repo in repos:
                if repo['name'].lower() == migrate_repo.lower():
                    r = migrate(repo=repo, source=source, dest=dest)
                    if r == 1:
                        print('终止所有迁移')
                        sys.exit(0)
                    elif r == 2:
                        print(repo['name'] + ' 仓库迁移失败')
                        failed_repos.append(repo['name'])
                    else:
                        print('仓库 ' + repo['name'] + ' 迁移成功!')
                        success_count += 1
                    break

    print('成功迁移' + str(success_count) + '个仓库')
    # 打印迁移失败的repos
    if len(failed_repos) != 0:
        print('迁移失败的仓库:')
        for failed_repo in failed_repos:
            print(failed_repo)
