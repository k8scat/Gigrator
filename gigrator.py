import requests
import config
import json
import os
import sys
from urllib import parse

class _const:
    GITLAB = 'gitlab'
    GITHUB = 'github'

# 支持的Git服务器
support = ['gitlab', 'github']

# GitLab 认证头信息
gitlab_headers = {
    'PRIVATE-TOKEN': config.gitlab_token
}
# GitHub 认证头信息
github_headers = {
    'Authorization': 'token ' + config.github_token
}

# repo临时目录
repo_dir = os.getcwd() + '/repo/'

# 列出用户所在源Git服务器上所有的仓库
def list_repos(server=None):
    if server is None or server == '':
        return
    
    # 定义最终返回的所有仓库集合
    # 使用extend添加另一个列表
    all_repos = []
    page = 1
    
    server = server.lower()
    
    if server == 'gitlab':
        # GitLab
        # List user projects: GET /users/:user_id/projects (需要分页: ?page=1)
        while True:
            r = requests.get(config.gitlab_api + '/users/' + config.gitlab_username + '/projects?page=' + str(page), headers=gitlab_headers)
            
            repos = json.loads(r.content.decode('utf-8'))
            
            if len(repos) == 0:
                break
            
            all_repos.extend(repos)
            for repo in repos:
                print(repo['name'])
                
            page += 1
            
    
    if server == 'github':
        # GitHub
        # Get: Get /repos/:owner/:repo (通过Get判断仓库是否已存在)
        # List user repositories: Get /users/:username/repos (需要分页: ?page=1)
        while True:
            r = requests.get(config.github_api + '/users/' + config.github_username + '/repos?page=' + str(page), headers=github_headers)
            
            repos = json.loads(r.content.decode('utf-8'))
            
            if len(repos) == 0:
                break
            
            all_repos.extend(repos)
            for repo in repos:
                print(repo['name'])
            
            page += 1
    
    print('总共' + str(len(all_repos)) + '个仓库')
    return all_repos

# 迁移仓库
def migrate(repo=None, source=None, dest=None):
    if repo is None or source is None or dest is None:
        return
    
    # 判断用户在目的Git服务器上是否已有同名的仓库
    # 有则不做迁移操作, 并进行提示
    if dest == _const.GITLAB:
        # check
        # Get single project: GET /projects/:id
        path = parse.quote(config.gitlab_username + '/' + repo['name'])
        r = requests.get(config.gitlab_api + '/projects/' + path)
        if r.status_code == 200:
            print('您所在目的Git服务已存在' + repo['name'] + '仓库!')
            return
    elif dest == _const.GITHUB:
        # check
        # Get: GET /repos/:owner/:repo
        r = requests.get(config.gitlab_api + '/repos/' + config.github_username + '/' + repo['name'])
        if r.status_code == 200:
            print('您所在目的Git服务已存在' + repo['name'] + '仓库!')
            return
        
    # clone from source
    if source == _const.GITLAB:
        if not os.path.isdir(repo_dir):
            os.mkdir(repo_dir)
        cmd = 'cd ' + repo_dir + ' && git clone --bare ' + config.gitlab_ssh + config.gitlab_username + '/' + repo['name'] + '.git'
        if os.system(cmd) != 0:
            print('仓库' + repo['name'] + 'clone失败!')
            return 1
    elif source == _const.GITHUB:
        if not os.path.isdir(repo_dir):
            os.mkdir(repo_dir)
        cmd = 'cd ' + repo_dir + ' && git clone --bare ' + config.github_ssh + config.github_username + '/' + repo['name'] + '.git'
        if os.system(cmd) != 0:
            print('仓库' + repo['name'] + 'clone失败!')
            return 1
        
    # create through API
    # 判断用户在目的Git服务器上是否已有同名的仓库
    # 有则不做迁移操作, 并进行提示
    if dest == _const.GITLAB:
        # Create project for user: POST /projects/user/:user_id (status_code: 201)
        # data = {
        #     'name': repo['name'],
        #     'description': '' if repo['description'] is None else repo['description'],
        #     'visibility': 'private' if repo['private'] else 'public'
        # }
        description = '' if repo['description'] is None else repo['description']
        visibility = 'private' if repo['private'] else 'public'
        data = 'name=' + repo['name'] + '&description=' + description + '&visibility=' + visibility
        print(json.dumps(data))
        r = requests.post(config.gitlab_api + '/projects', headers=gitlab_headers, data=data)
        if r.status_code != 201:
            print(r.content.decode('utf-8'))
            cmd = 'rm -rf ' + repo_dir + repo['name'] + '.git'
            os.system(cmd)
            return 1
        
        # push to dest
        cmd = 'cd ' + repo_dir + repo['name'] + '.git && git push --mirror ' + config.gitlab_ssh + config.gitlab_username + '/' + repo['name'] + '.git'
        r = os.system(cmd)
        cmd = 'rm -rf ' + repo_dir + repo['name'] + '.git'
        os.system(cmd)
        if r != 0:
            print('仓库' + repo['name'] + '迁移失败!')
            return 1
    elif dest == _const.GITHUB:
        # Create project for user: POST /user/repos (status_code: 201)
        data = {
            'name': repo['name'],
            'description': repo['description'],
            'private': True if repo['visibility'] == 'private' else False
        }
        r = requests.post(config.github_api + '/user/repos', headers=github_headers, data=json.dumps(data))
        if r.status_code != 201:
            print(r.content.decode('utf-8'))
            cmd = 'rm -rf ' + repo_dir + repo['name'] + '.git'
            os.system(cmd)
            return 1
        
        # push to dest
        cmd = 'cd ' + repo_dir + repo['name'] + '.git && git push --mirror ' + config.github_ssh + config.github_username + '/' + repo['name'] + '.git'
        r = os.system(cmd)
        cmd = 'rm -rf ' + repo_dir + repo['name'] + '.git'
        os.system(cmd)
        if r != 0:
            print('仓库' + repo['name'] + '迁移失败!')
            return 1

if __name__ == "__main__":
    
    # 创建repo临时目录
    if not os.path.isdir(repo_dir):
        os.mkdir(repo_dir)   

    print('使用前请先配置config文件')
    print('目前仅支持GitLab与GitHub之间的仓库迁移')
    # 用户输入源Git服务器
    while True:
        source = input('源Git服务器(GitLab|GitHub): ').lower().replace(' ', '')
        if source != '' and source in support:
            break
        print('输入有误, 请重新输入!')

    # 用户输入目的Git服务器
    while True:
        dest = input('目标Git服务器(GitLab|GitHub): ').lower().replace(' ', '')
        if dest != '' and dest in support:
            break
        print('输入有误, 请重新输入!')

    repos = list_repos(source)

    # 用户输入需要迁移的仓库
    migrate_repos = input('请输入需要迁移的仓库(例如: repo_name1, repo2_name): ').replace(' ', '').split(',')

    # 循环进行仓库迁移
    for migrate_repo in migrate_repos:
        for repo in repos:
            if repo['name'].lower() == migrate_repo.lower():
                if migrate(repo=repo, source=source, dest=dest) == 1:
                    sys.exit(0)
                print('仓库' + migrate_repo + '迁移成功!')
                break
                
        
        
