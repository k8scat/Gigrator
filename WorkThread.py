import threading

from gigrator import set_failed_repos, set_success_count


class WorkThread(threading.Thread):
    def __init__(self, repo, source, dest, **kwargs):
        self.repo = repo
        self.source = source
        self.dest = dest
        super().__init__(**kwargs)

    def run(self):
        from migrate import migrate
        r = migrate(repo=self.repo, source=self.source, dest=self.dest)
        if r:
            # print(repo['name'] + ' 仓库迁移失败')
            set_failed_repos(self.repo['name'])
        else:
            # print('仓库 ' + repo['name'] + ' 迁移成功!')
            set_success_count()
