import json
import os
import sys
import requests
# import private as config  # dev
import config  # prod
from settings import support, repos_dir


def list_repos(server):
    """
    列出指定用户在Git服务器上拥有的所有的仓库(owner)

    :param server: Git服务器配置
    :return: list
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

    elif server_type == 'gitea' or server_type == 'gogs':
        # GET
        # ​/user​/repos
        # List the repos that the authenticated user owns or has access to
        # gitea没有做分页: https://github.com/go-gitea/gitea/issues/7515
        list_repos_url = api + '/user/repos'

        r = requests.get(list_repos_url, headers=headers)
        if r.status_code == 200:
            repos = json.loads(r.content.decode('utf-8'))
            for repo in repos:
                if repo['owner']['username'] == username:
                    all_repos.append(repo)
        return all_repos

    elif server_type == 'coding':
        # 当前用户的项目列表
        # GET /api/user/projects?type=all&amp;page={page}&amp;pageSize={pageSize}
        # Response totalPage?
        list_repos_url = api + '/api/user/projects?type=all&pageSize=10&page='

        r = requests.get(list_repos_url + str(page), headers=headers)
        if r.status_code == 200:
            content = json.loads(r.content.decode('utf-8'))
            totalPage = content['data']['totalPage']
            repos = content['data']['list']
            for repo in repos:
                if repo['owner_user_name'] == username:
                    all_repos.append(repo)

            while page < totalPage:
                page += 1
                r = requests.get(list_repos_url + str(page), headers=headers)
                if r.status_code == 200:
                    content = json.loads(r.content.decode('utf-8'))
                    repos = content['data']['list']
                    for repo in repos:
                        if repo['owner_user_name'] == username:
                            all_repos.append(repo)

        return all_repos

    # 当没有授权时, 可能只会返回公开项目(至少gitlab会)
    while True:
        r = requests.get(list_repos_url + str(page), headers=headers)
        if r.status_code == 200:
            repos = json.loads(r.content.decode('utf-8'))
            if len(repos) == 0:
                break
            all_repos.extend(repos)
            page += 1
        elif r.status_code == 401:
            print('授权令牌无效')
            break
        else:
            print(r.content.decode('utf-8'))
            break

    return all_repos


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
    :return: dict
    """
    # 防止出现配置时大小写的问题
    config['type'] = config['type'].lower()
    server_type = config['type']
    username = config['username']
    token = config['token']
    url = config['url']

    if server_type == 'gitlab' or server_type == 'gitea' or server_type == 'gogs':
        if url == '' or url is None:
            print('gitlab, gitea 和 gogs 需要设置url')
            return None

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
        config['ssh_prefix'] = 'git@' + url.split('://')[1] + ':'
        config['api'] = url + '/api/v4'

    elif server_type == 'gitea' or server_type == 'gogs':
        config['headers'] = {
            'Content-Type': 'application/json',
            'Authorization': 'token ' + config['token']
        }
        config['ssh_prefix'] = 'git@' + url.split('://')[1] + ':'
        config['api'] = url + '/api/v1'

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

    print('检查源Git服务器配置...')
    source = autoconfig(config.source)
    if source is None:
        sys.exit(0)

    # 创建repos临时目录
    if not os.path.isdir(repos_dir):
        os.mkdir(repos_dir)

    # 每次迁移前删除repos临时目录中所有的文件
    cmd = 'rm -rf ' + repos_dir + '*'
    os.system(cmd)

    # 列出在源Git服务器上所有的仓库
    repos = list_repos(source)
    # 没有仓库的话直接退出
    if len(repos) == 0:
        sys.exit(0)

    # 打印仓库名
    for repo in repos:
        print(repo['name'])
    print('总共' + str(len(repos)) + '个仓库')

    # 输入需要迁移的仓库
    migrate_repos = input('请指定需要迁移的仓库(例如: repo1_name, repo2_name, 默认迁移所有仓库): ').replace(' ', '').split(',')

    threads = []
    from WorkThread import WorkThread, get_failed_repos, get_success_count
    # 迁移所有仓库
    if len(migrate_repos) == 1 and migrate_repos[0] == '':
        for repo in repos:
            threads.append(WorkThread(repo=repo, source=source, dest=dest))
    # 迁移指定仓库
    else:
        for migrate_repo in migrate_repos:
            for repo in repos:
                if repo['name'].lower() == migrate_repo.lower():
                    threads.append(WorkThread(repo=repo, source=source, dest=dest))

    print('开始迁移仓库')
    for t in threads:
        t.start()

    for t in threads:
        t.join()

    success_count = get_success_count()
    print('成功迁移' + str(success_count) + '个仓库')
    # 打印迁移失败的repos
    failed_repos = get_failed_repos()
    if len(failed_repos) != 0:
        print('迁移失败的仓库:')
        for failed_repo in failed_repos:
            print(failed_repo)

        print('请检查目的Git服务器是否存在同名仓库或者仓库是否为空仓库')
