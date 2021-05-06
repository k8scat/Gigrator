# -*- coding: utf-8 -*-

"""
@author: hsowan <hsowan.me@gmail.com>
@date: 2020/2/10

"""
import json
import logging
import os
import re
import uuid
from urllib.parse import quote,urlencode
import requests
import settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Git:
    type = ''
    username = ''
    token = ''
    url = ''
    api = ''
    ssh_prefix = ''
    headers = {}

    def __init__(self, config: dict):
        self.type = config['type'].lower()
        if self.type == 'gogs':
            self.type = 'gitea'
        self.username = config['username']
        self.token = config['token']
        self.url = config['url']

        if not self.type:
            raise ValueError('type 必须配置')

        if self.type not in settings.SUPPORT_GITS:
            raise ValueError('暂不支持此类型的Git服务器: ' + self.type)

        if self.type in ['gitlab', 'gitea'] and not self.url:
            raise ValueError('gitlab/gitea/gogs 需要配置url')

        if not self.username:
            raise ValueError('username 必须配置')

        if not self.token:
            raise ValueError('token 必须配置')

        if self.type in ['gitlab', 'gitea']:
            if not re.match(r'^http(s)?://.+$', self.url):
                raise ValueError('url 配置有误')
            if self.url.endswith('/'):
                self.url = self.url[:-1]

    def is_existed(self, repo_name: str) -> bool:
        """
        Check repo existed or not

        :param repo_name:
        :return:
        """
        raise NotImplementedError

    def clone_repo(self, repo_name: str) -> str:
        """
        Clone repo

        :param repo_name:
        :return: the local dir of saved repo
        """

        clone_space = os.path.join(settings.TEMP_DIR, str(uuid.uuid1()))
        os.mkdir(clone_space)

        # 检查本地是否存在repo, 存在则删除
        ssh_address = self.ssh_prefix + self.username + '/' + repo_name + '.git'
        clone_cmd = 'cd ' + clone_space + ' && git clone --bare ' + ssh_address

        return os.path.join(clone_space, repo_name + '.git') if os.system(clone_cmd) == 0 else None

    def create_repo(self, name: str, desc: str, is_private: bool) -> bool:
        """
        Create repo

        :param name:
        :param desc:
        :param is_private:
        :return: create successfully or not
        """
        raise NotImplementedError

    def push_repo(self, repo_name: str, repo_dir: str) -> bool:
        """
        Push repo

        :param repo_name:
        :param repo_dir:
        :return: bool
        """
        ssh_address = self.ssh_prefix + self.username + '/' + repo_name + '.git'
        push_cmd = 'cd ' + repo_dir + ' && git push --mirror ' + ssh_address
        return os.system(push_cmd) == 0

    def list_repos(self) -> list:
        """
        List all repos owned

        :return: a list of repos
        """
        raise NotImplementedError


class Gitlab(Git):

    def __init__(self, config: dict):
        super().__init__(config)
        self.headers = {
            'Private-Token': self.token
        }
        self.ssh_prefix = 'git@' + self.url.split('://')[1] + ':'
        self.api = self.url + settings.GITLAB_API_VERSION

    def is_existed(self, repo_name: str) -> bool:
        # Get single project
        # GET /projects/:id
        path = quote(f'{self.username}/{repo_name}', safe='')
        url = f'{self.api}/projects/{path}'
        r = requests.get(url, headers=self.headers)
        return r.status_code == 200

    def create_repo(self, name: str, desc: str, is_private: bool) -> bool:
        data = {
            'name': name,
            'description': desc,
            'visibility': 'private' if is_private else 'public'
        }
        url = f'{self.api}/projects'
        r = requests.post(url, data=json.dumps(data), headers=self.headers)
        return r.status_code == 201

    def list_repos(self) -> list:
        # GitLab
        # List user projects: GET /users/:user_id/projects (需要分页: ?page=1)
        # 不存在401的问题: 会返回公开的仓库
        url = f'{self.api}/users/{self.username}/projects?page='
        # 当没有授权时, 可能只会返回公开项目(至少gitlab会)
        all_repos = []
        page = 1
        while True:
            r = requests.get(url + str(page), headers=self.headers)
            if r.status_code == 200:
                repos = r.json()
                if len(repos) == 0:
                    break
                for repo in repos:
                    all_repos.append(dict(name=repo['name'],
                                          desc=repo['description'],
                                          is_private=repo['visibility'] != 'public'))
                page += 1
            else:
                raise RuntimeError(r.content)
        return all_repos


class Github(Git):
    def __init__(self, config: dict):
        super().__init__(config)
        self.headers = {
            'Authorization': 'token ' + self.token
        }
        self.ssh_prefix = settings.GITHUB_SSH_PREFIX
        self.api = settings.GITHUB_API

    def is_existed(self, repo_name: str) -> bool:
        query = '''
        query ($repo_owner: String!, $repo_name: String!) {
          repository(owner: $repo_owner, name: $repo_name) {
            id
          }
        }
        '''
        variables = {
            'repo_owner': self.username,
            'repo_name': repo_name
        }
        post_data = json.dumps({
            'query': query,
            'variables': variables
        })
        r = requests.post(self.api, data=post_data, headers=self.headers)
        if r.status_code == 200:
            data = r.json()
            try:
                return data['data']['repository'].get('id', None) is not None
            except KeyError:
                return False
        else:
            raise RuntimeError(r.content)

    def create_repo(self, name: str, desc: str, is_private: bool) -> bool:
        mutation = '''
        mutation ($name: String!, $desc: String!, $isPrivate: RepositoryVisibility!) {
          createRepository(input: {name: $name, description: $desc, visibility: $isPrivate}) {
            clientMutationId
            repository {
              id
            }
          }
        }
        '''
        variables = {
            'name': name,
            'desc': desc,
            'isPrivate': 'PRIVATE' if is_private else 'PUBLIC'
        }
        post_data = json.dumps({
            'query': mutation,
            'variables': variables
        })
        r = requests.post(self.api, data=post_data, headers=self.headers)
        if r.status_code == 200:
            data = r.json()
            return 'errors' not in data.keys()
        else:
            raise RuntimeError(r.content)

    def list_repos(self) -> list:
        query = '''
        query ($first: Int!, $after: String) {
          viewer {
            repositories(first: $first, after: $after, ownerAffiliations: [OWNER]) {
              edges {
                node {
                  name
                  isPrivate
                  description
                }
                cursor
              }
              pageInfo {
                hasNextPage
              }
            }
          }
        }
        '''
        variables = {
            'first': 100
        }
        post_data = json.dumps({
            'query': query,
            'variables': variables
        })
        r = requests.post(self.api, data=post_data, headers=self.headers)
        if r.status_code == 200:
            data = r.json()
            all_repos = []
            try:
                def parse_data():
                    repos = data['data']['viewer']['repositories']['edges']
                    for repo in repos:
                        repo = repo['node']
                        all_repos.append(dict(name=repo['name'],
                                              desc=repo['description'],
                                              is_private=repo['isPrivate']))
                parse_data()
                has_next_page = data['data']['viewer']['repositories']['pageInfo']['hasNextPage']
                while has_next_page:
                    variables['after'] = data['data']['viewer']['repositories']['edges'][-1]['cursor']
                    post_data = json.dumps({
                        'query': query,
                        'variables': variables
                    })
                    r = requests.post(self.api, data=post_data, headers=self.headers)
                    if r.status_code == 200:
                        data = r.json()
                        parse_data()
                        has_next_page = data['data']['viewer']['repositories']['pageInfo']['hasNextPage']
                    else:
                        raise RuntimeError(r.content)
            except KeyError:
                logger.error(data)
            finally:
                return all_repos
        else:
            raise RuntimeError(r.content)


class Gitee(Git):
    def __init__(self, config: dict):
        super().__init__(config)
        self.headers = {
            'Content-Type': 'application/json;charset=UTF-8'
        }
        self.ssh_prefix = settings.GITEE_SSH_PREFIX
        self.api = settings.GITEE_API

    def is_existed(self, repo_name: str) -> bool:
        # 获取用户的某个仓库: GET /repos/{owner}/{repo}
        # https://gitee.com/api/v5/swagger#/getV5ReposOwnerRepo
        url = f'{self.api}/repos/{self.username}/{repo_name}?access_token={self.token}'
        r = requests.get(url, headers=self.headers)
        return r.status_code == 200

    def create_repo(self, name: str, desc: str, is_private: bool) -> bool:
        data = {
            'access_token': self.token,
            'name': name,
            'description': desc,
            'private': is_private
        }
        url = f'{self.api}/user/repos'
        r = requests.post(url, json=data, headers=self.headers)
        return r.status_code == 201

    def list_repos(self) -> list:
        # Gitee
        # 列出授权用户的所有仓库: GET /user/repos
        # https://gitee.com/api/v5/swagger#/getV5UserRepos
        list_repos_url = self.api + '/user/repos?access_token=' + self.token \
                         + '&type=personal&sort=full_name&per_page=100&page='
        page = 1
        all_repos = []
        while True:
            r = requests.get(list_repos_url + str(page), headers=self.headers)
            if r.status_code == 200:
                repos = r.json()
                if len(repos) == 0:
                    break
                for repo in repos:
                    all_repos.append(dict(name=repo['name'],
                                          desc=repo['description'],
                                          is_private=repo['private']))
                page += 1
            elif r.status_code == 401:
                raise ValueError('token 无效')
            else:
                raise RuntimeError(r.content.decode('utf-8'))
        return all_repos


class Gitea(Git):
    def __init__(self, config: dict):
        super().__init__(config)
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'token {self.token}'
        }
        self.ssh_prefix = f'git@{self.url.split("://")[1]}:'
        self.api = self.url + settings.GITEA_API_VERSION

    def is_existed(self, repo_name: str) -> bool:
        # GET
        # ​/repos​/{owner}​/{repo}
        # Get a repository
        url = f'{self.api}/repos/{self.username}/{repo_name}'
        r = requests.get(url, headers=self.headers)
        return r.status_code == 200

    def create_repo(self, name: str, desc: str, is_private: bool) -> bool:
        data = {
            'auto_init': False,
            'description': desc,
            'name': name,
            'private': is_private
        }
        url = f'{self.api}/user/repos'
        r = requests.post(url, headers=self.headers, data=json.dumps(data))
        return r.status_code == 201

    def list_repos(self) -> list:
        # GET
        # ​/user​/repos
        # List the repos that the authenticated user owns or has access to
        # 没有做分页: https://github.com/go-gitea/gitea/issues/7515
        list_repos_url = self.api + '/user/repos'
        all_repos = []
        r = requests.get(list_repos_url, headers=self.headers)
        if r.status_code == 200:
            repos = r.json()
            for repo in repos:
                if repo['owner']['username'] == self.username:
                    all_repos.append(dict(name=repo['name'],
                                          desc=repo['description'],
                                          is_private=repo['private']))
        return all_repos


class Coding(Git):
    def __init__(self, config: dict):
        super().__init__(config)
        self.headers = {
            'Authorization': 'token ' + self.token
        }
        self.ssh_prefix = settings.CODING_SSH_PREFIX
        self.api = f'https://{self.username}.coding.net'

    def is_existed(self, repo_name: str) -> bool:
        # GET /api/user/{username}/project/{project_name}
        url = f'{self.api}/api/user/{self.username}/project/{repo_name}'
        r = requests.get(url, headers=self.headers)
        if r.status_code == 200:
            data = r.json()
            return data['code'] == 0 and data['data']['name'] == repo_name
        else:
            return False

    def create_repo(self, name: str, desc: str, is_private: bool) -> bool:
        raise PermissionError('Coding 不支持通过API创建仓库')

    def list_repos(self) -> list:
        # 当前用户的项目列表
        # https://open.coding.net/api-reference/%E9%A1%B9%E7%9B%AE.html#%E5%BD%93%E5%89%8D%E7%94%A8%E6%88%B7%E7%9A%84%E9%A1%B9%E7%9B%AE%E5%88%97%E8%A1%A8
        # GET /api/user/projects?type=all&amp;page={page}&amp;pageSize={pageSize}
        # Response包含totalPage
        url = f'{self.api}/api/user/projects?type=all&pageSize=10&page='
        page = 1
        all_repos = []
        r = requests.get(url + str(page), headers=self.headers)
        if r.status_code == 200:
            data = r.json()
            if data['code'] == 0:
                total_page = data['data']['totalPage']
                repos = data['data']['list']
                for repo in repos:
                    if str.lower(repo['owner_user_name']) == str.lower(self.username):
                        all_repos.append(dict(name=repo['name'],
                                              desc=repo['description'],
                                              is_private=not repo['is_public']))
            else:
                raise RuntimeError(data)

            while page < total_page:
                page += 1
                r = requests.get(url + str(page), headers=self.headers)
                if r.status_code == 200:
                    if data['code'] == 0:
                        data = r.json()
                        repos = data['data']['list']
                        for repo in repos:
                            if str.lower(repo['owner_user_name']) == str.lower(self.username):
                                all_repos.append(dict(name=repo['name'],
                                                      desc=repo['description'],
                                                      is_private=not repo['is_public']))
                    else:
                        raise RuntimeError(data)

        return all_repos


#腾讯工蜂
class GF(Git):
    def __init__(self, config: dict):
        super().__init__(config)
        self.headers = {
            'PRIVATE-TOKEN': self.token
        }
        self.ssh_prefix = settings.GF_SSH_PREFIX
        self.api = settings.GF_API

    def is_existed(self, repo_name: str) -> bool:
        # repo_name如果包含命名空间需要URL编码
        repo_name_encoded = urlencode(repo_name)
        url = f'{self.api}/api/v3/projects/{repo_name_encoded}/repository/tree'
        r = requests.get(url, headers=self.headers)
        if r.status_code == 200:
            return True
        else:
            return False

    #repo_name = name_with_namespace
    def create_repo(self, repo_name: str, desc: str, is_private: bool) -> bool:
        url = self.api + "/projects"
        repo_full_name_list = repo_name.split("/")
        if len(repo_full_name_list) == 1:
            repo_name_namespace = "null"
            repo_name_short = repo_name
        else:
            repo_name_namespace = repo_full_name_list[0]
            repo_name_short = repo_full_name_list[1]
        if is_private:
            visibility_level = 0
        else:
            visibility_level = 10
        data = {
            "name": repo_name_short,
            "namespace_id": repo_name_namespace,
            "description": desc,
            "visibility_level": visibility_level
        }
        r = requests.post(url, headers=self.headers, data=json.dumps(data))
        return r.status_code == 200


    def list_repos(self) -> list:
        list_groups_url = self.api + '/groups'
        all_groups = []
        all_repos = []
        r = requests.get(list_groups_url, headers=self.headers)
        if r.status_code == 200:
            repos = r.json()
            for repo in repos:
                all_groups.append(repo["id"])
        for group in all_groups:
            group_detail_url = list_groups_url + "/" + str(group)
            r = requests.get(group_detail_url, headers=self.headers)
            if r.status_code == 200:
                group_detail = r.json()
                for repo in group_detail["projects"]:
                    all_repos.append(
                        dict(name=repo["name_with_namespace"],
                             desc=repo['description'],
                             is_private=not repo['public'])
                    )
        return all_repos


if __name__ == "__main__":
    if not os.path.isdir(settings.TEMP_DIR):
        os.mkdir(settings.TEMP_DIR)

    source_type = settings.SOURCE_GIT.get('type', '')
    dest_type = settings.DEST_GIT.get('type', '')
    if source_type == 'gitlab':
        source_git = Gitlab(settings.SOURCE_GIT)
    elif source_type == 'github':
        source_git = Github(settings.SOURCE_GIT)
    elif source_type == 'coding':
        source_git = Coding(settings.SOURCE_GIT)
    elif source_type in ['gitea', 'gogs']:
        source_git = Gitea(settings.SOURCE_GIT)
    elif source_type == 'gitee':
        source_git = Gitee(settings.SOURCE_GIT)
    elif source_type == "gf":
        source_git = GF(settings.SOURCE_GIT)
    else:
        raise ValueError(f'暂不支持此类Git服务器: {source_type}')

    if dest_type == 'gitlab':
        dest_git = Gitlab(settings.DEST_GIT)
    elif dest_type == 'github':
        dest_git = Github(settings.DEST_GIT)
    elif dest_type == 'coding':
        raise ValueError(f'暂不支持迁移至 Coding')
    elif dest_type in ['gitea', 'gogs']:
        dest_git = Gitea(settings.DEST_GIT)
    elif dest_type == 'gitee':
        dest_git = Gitee(settings.DEST_GIT)
    elif dest_type == "gf":
        dest_type = GF(settings.DEST_GIT)
    else:
        raise ValueError(f'暂不支持此类Git服务器: {source_type}')

    all_repos = source_git.list_repos()
    for i, repo in enumerate(all_repos):
        print(f'{str(i)}. {repo["name"]}')
    repo_ids = [int(i) for i in input('请输入需要迁移的仓库序号, 以英文逗号分割: ').replace(' ', '').split(',')]
    for repo_id in repo_ids:
        migrate_repo = all_repos[repo_id]
        try:
            repo_dir = source_git.clone_repo(migrate_repo['name'])
            if repo_dir:
                has_create = dest_git.create_repo(**migrate_repo)
                if has_create:
                    dest_git.push_repo(migrate_repo['name'], repo_dir)
        except Exception as e:
            logger.error(e)



