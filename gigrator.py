import requests
import private as config
import json
import os
import sys
from urllib import parse


class Const:
    GITLAB = 'gitlab'
    GITHUB = 'github'
    GITEE = 'gitee'
    GITEA = 'gitea'


# 支持的Git服务器
support = ['gitlab', 'github', 'gitee', 'gitea']

# GitLab 认证头信息
gitlab_headers = {
    'PRIVATE-TOKEN': config.gitlab_token
}
# GitHub 认证头信息
github_headers = {
    'Authorization': 'token ' + config.github_token
}
# Gitee 头信息
gitee_headers = {
    'Content-Type': 'application/json;charset=UTF-8'
}
# Gitea 头信息
gitea_headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json'
}

# repo临时目录
repo_temp_dir = os.getcwd() + '/repo/'


# 列出在源Git服务器上所有的仓库
# return 1表示将终止整个迁移
def list_repos(server):
    if server == '' or not isinstance(server, str):
        print('请输入正确的Git服务器')
        return

    server = server.lower()

    # 定义最终返回的所有仓库集合
    # 使用extend添加另一个列表
    all_repos = []
    page = 1
    list_repos_url = None
    headers = None

    if server == 'gitlab':
        # GitLab
        # List user projects: GET /users/:user_id/projects (需要分页: ?page=1)
        list_repos_url = config.gitlab_api + '/users/' + config.gitlab_username + '/projects?page='
        headers = gitlab_headers

    if server == 'github':
        # GitHub
        # Get: Get /repos/:owner/:repo (通过Get判断仓库是否已存在)
        # List your repositories: GET /user/repos (需要分页: ?page=1)
        list_repos_url = config.github_api + '/user/repos?type=owner&page='
        headers = github_headers

    if server == 'gitee':
        # Gitee
        # 列出授权用户的所有仓库: GET /user/repos
        # https://gitee.com/api/v5/swagger#/getV5UserRepos
        list_repos_url = config.gitee_api + '/user/repos?access_token=' + config.gitee_token \
                         + '&type=personal&sort=full_name&per_page=100&page='
        headers = gitee_headers

    if server == 'gitea':
        # GET
        # ​/user​/repos
        # List the repos that the authenticated user owns or has access to
        list_repos_url = config.gitea_api + '/user/repos?access_token=' + config.gitea_token
        headers = gitea_headers

        ################################################
        # special gitea
        r = requests.get(list_repos_url, headers=headers)
        repos = json.loads(r.content.decode('utf-8'))

        # gitea似乎没有做分页
        all_repos.extend(repos)
        for repo in all_repos:
            if repo['owner']['username'] != config.gitea_username:
                all_repos.remove(repo)

        for repo in all_repos:
            print(repo['name'])

        print('总共' + str(len(all_repos)) + '个仓库')
        return all_repos
        ################################################

    while True:
        r = requests.get(list_repos_url + str(page), headers=headers)

        if r.status_code == 200:

            repos = json.loads(r.content.decode('utf-8'))

            if len(repos) == 0:
                break

            all_repos.extend(repos)
            for repo in repos:
                print(repo['name'])

            page += 1

        elif r.status_code == 401:
            print('授权令牌无效, 请在config.py文件中配置正确的授权令牌')
            return all_repos
        else:
            print(r)
            return all_repos

    with open('temp.json', 'w') as f:
        f.write(json.dumps(all_repos))

    print('总共' + str(len(all_repos)) + '个仓库')
    return all_repos


# 拼接clone命令
def join_clone_cmd(ssh, username, repo_name):
    if ssh is None or ssh == '' or username is None or username == '' \
            or repo_name is None or repo_name == '' \
            or not isinstance(ssh, str) or not isinstance(username, str) or not isinstance(repo_name, str):
        return None

    clone_cmd = 'cd ' + repo_temp_dir + ' && git clone --bare ' + ssh + username + '/' + repo_name + '.git'
    return clone_cmd


# 拼接push命令
def join_push_cmd(ssh, username, repo_name):
    if ssh == '' or username == '' or repo_name == '' \
            or not isinstance(ssh, str) or not isinstance(username, str) or not isinstance(repo_name, str):
        return None

    push_cmd = 'cd ' + repo_temp_dir + repo_name + '.git && git push --mirror ' \
               + ssh + username + '/' + repo_name + '.git'
    return push_cmd


# 检查Git服务器是否存在同名仓库
def is_existed(git_server, repo_name):
    pass


# 从Git服务器clone仓库
def clone(git_server, repo_name):
    pass


# 向Git服务器推送仓库(包括创建)
def push(git_server, repo):
    pass


# 迁移仓库
# return: 1表示将终止所有迁移, 2表示单个仓库迁移失败
def migrate(repo, source, dest):
    if repo is None or not isinstance(repo, dict) \
            or source == '' or not isinstance(source, str) \
            or dest == '' or not isinstance(dest, str):
        return 1

    # 判断在目的Git服务器上是否已有同名的仓库
    # 有则不做迁移操作, 并进行提示
    check_url = ''
    headers = None
    if dest == Const.GITLAB:
        # Get single project: GET /projects/:id
        # urlencode 需要加上safe='', / 就会转成%2F
        path = parse.quote(config.gitlab_username + '/' + repo['name'], safe='')
        check_url = config.gitlab_api + '/projects/' + path
        headers = gitlab_headers

    elif dest == Const.GITHUB:
        # Get: GET /repos/:owner/:repo
        check_url = config.gitlab_api + '/repos/' + config.github_username + '/' + repo['name']
        headers = github_headers

    elif dest == Const.GITEE:
        # 获取用户的某个仓库: GET /repos/{owner}/{repo}
        # https://gitee.com/api/v5/swagger#/getV5ReposOwnerRepo
        check_url = config.gitee_api + '/repos/' + config.gitee_username + '/' + repo['name'] \
                    + '?access_token=' + config.gitee_token
        headers = gitee_headers

    elif dest == Const.GITEA:
        # GET
        # ​/repos​/{owner}​/{repo}
        # Get a repository
        check_url = config.gitea_api + '/' + config.gitea_username + '/' + repo['name'] \
                    + '?access_token=' + config.gitea_token
        headers = gitea_headers

    r = requests.get(check_url, headers=headers)
    if r.status_code == 200:
        print('您所在目的Git服务已存在' + repo['name'] + '仓库! 故此仓库无法迁移')
        return 2

    # clone from source
    # 检查本地是否存在repo, 存在则删除
    repo_dir = repo_temp_dir + repo['name'] + '.git'
    print(repo_dir)
    if os.path.isdir(repo_dir):
        cmd = 'rm -rf ' + repo_dir
        if os.system(cmd) != 0:
            print('删除目录失败')

    clone_cmd = None
    # 不同的Git服务器获取到的数据格式不一样, 所以在这里设置private
    private = False
    if source == Const.GITLAB:
        clone_cmd = join_clone_cmd(config.gitlab_ssh, config.gitlab_username, repo['name'])
        if repo['visibility'] == 'private':
            private = True

    elif source == Const.GITHUB:
        clone_cmd = join_clone_cmd(config.github_ssh, config.github_username, repo['name'])
        if repo['private']:
            private = True

    elif source == Const.GITEE:
        clone_cmd = join_clone_cmd(config.gitee_ssh, config.gitee_username, repo['name'])
        if repo['private']:
            private = True

    elif source == Const.GITEA:
        clone_cmd = join_clone_cmd(config.gitea_ssh, config.gitea_username, repo['name'])
        if repo['private']:
            private = True

    if clone_cmd is None:
        print('请检查配置是否无误(config.py)')
        return 1

    # 尝试clone, 失败将终止整个程序
    if os.system(clone_cmd) != 0:
        print('请检查配置是否无误(config.py)')
        print('请确定源Git服务器已经添加ssh_key')
        return 1
    else:
        print('拉取 ' + repo['name'] + ' 成功')

    # create repo through API
    create_repo_url = None
    headers = None
    data = None
    ssh = None
    username = None

    # GitLab
    # Create project for user: POST /projects/user/:user_id (status_code: 201)
    if dest == Const.GITLAB:
        description = '' if repo['description'] is None else repo['description']
        visibility = 'private' if private else 'public'
        data = 'name=' + repo['name'] + '&description=' + description + '&visibility=' + visibility
        create_repo_url = config.gitlab_api + '/projects'
        headers = gitlab_headers
        ssh = config.gitlab_ssh
        username = config.gitlab_username

    # GitHub
    # Create project for user: POST /user/repos (status_code: 201)
    elif dest == Const.GITHUB:
        json_data = {
            'name': repo['name'],
            'description': repo['description'],
            'private': private
        }
        data = json.dumps(json_data)
        create_repo_url = config.github_api + '/user/repos'
        headers = github_headers
        ssh = config.github_ssh
        username = config.github_username

    # 创建一个仓库: POST /user/repos
    # https://gitee.com/api/v5/swagger#/postV5UserRepos
    elif dest == Const.GITEE:
        json_data = {
            'access_token': config.gitee_token,
            'name': repo['name'],
            'description': repo['description'],
            'private': private,
            'has_issues': True,
            'has_wiki': True
        }
        data = json.dumps(json_data)
        create_repo_url = config.gitee_api + '/user/repos'
        headers = gitee_headers
        ssh = config.gitee_ssh
        username = config.gitee_username

    elif dest == Const.GITEA:
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
        create_repo_url = config.gitea_api + '/user/repos?access_token=' + config.gitea_token
        headers = gitea_headers
        ssh = config.gitea_ssh
        username = config.gitea_username

    r = requests.post(create_repo_url, headers=headers, data=data)
    if r.status_code != 201:
        # 409 conflict
        # 存在同名仓库, 则对这个仓库不做迁移
        if r.status_code == 409:
            return 2
        print(r.content.decode('utf-8'))
        return 1
    else:
        print('在目的Git服务器上创建 ' + repo['name'] + ' 仓库成功')

    push_cmd = join_push_cmd(ssh, username, repo['name'])
    if push_cmd is None:
        print('请检查配置是否无误(config.py)')
        return 1

    # push to dest
    if os.system(push_cmd) != 0:
        print('仓库' + repo['name'] + 'push失败!')
        print('请检查配置是否无误(config.py)')
        print('请确定目的Git服务器已经添加ssh_key')
        return 1

    return 0


# 在做迁移操作前，检查源Git服务器和目的Git服务器的配置
def check_config(source, dest):
    pass


if __name__ == "__main__":

    # 创建repo临时目录
    if not os.path.isdir(repo_temp_dir):
        if os.mkdir(repo_temp_dir) != 0:
            print('创建repo临时目录失败')
            sys.exit(0)

    print('目前支持的Git服务器: GitLab | GitHub | Gitee | Gitea')
    # 输入源Git服务器
    while True:
        source = input('源Git服务器: ').lower().replace(' ', '')
        if source != '' and source in support:
            break
        print('输入有误, 请重新输入!')

    # 输入目的Git服务器
    while True:
        dest = input('目标Git服务器: ').lower().replace(' ', '')
        if dest != '' and dest in support:
            break
        print('输入有误, 请重新输入!')

    # 列出在源Git服务器上所有的仓库
    repos = list_repos(source)
    # 没有仓库的话直接退出
    if len(repos) == 0:
        sys.exit(0)

    # 输入需要迁移的仓库
    migrate_repos = input('请指定需要迁移的仓库(例如: repo1_name, repo2_name, 默认迁移所有仓库): ').replace(' ', '').split(',')

    count = 0
    failed_repos = []
    # 迁移所有仓库
    if len(migrate_repos) == 1 and migrate_repos[0] == '':
        print('开始迁移所有仓库')
        for repo in repos:
            r = migrate(repo=repo, source=source, dest=dest)
            if r == 0:
                print('仓库 ' + repo['name'] + ' 迁移成功!')
                count += 1
            elif r == 1:
                sys.exit(0)
            elif r == 2:
                print(repo['name'] + ' 仓库迁移失败')
                failed_repos.append(repo['name'])
            break

    else:
        print('开始迁移指定仓库')
        # 循环进行仓库迁移
        for migrate_repo in migrate_repos:
            for repo in repos:
                if repo['name'].lower() == migrate_repo.lower():
                    r = migrate(repo=repo, source=source, dest=dest)
                    if r == 0:
                        print('仓库 ' + repo['name'] + ' 迁移成功!')
                        count += 1
                    elif r == 1:
                        sys.exit(0)
                    elif r == 2:
                        print(repo['name'] + ' 仓库迁移失败')
                        failed_repos.append(repo['name'])
                    break

        print('成功迁移' + str(count) + '个仓库')
        # 打印迁移失败的repos
        if len(failed_repos) != 0:
            print('迁移失败的仓库:')
            for failed_repo in failed_repos:
                print(failed_repo)
