import threading

lock = threading.Lock()

success_count = 0
failed_repos = []


def set_failed_repos(repo_name):
    global failed_repos
    failed_repos.append(repo_name)


def set_success_count():
    global success_count
    success_count += 1


def get_failed_repos():
    return failed_repos


def get_success_count():
    return success_count


class WorkThread(threading.Thread):
    def __init__(self, repo, source, dest, **kwargs):
        self.repo = repo
        self.source = source
        self.dest = dest
        super().__init__(**kwargs)

    def run(self):
        from migrate import migrate
        if migrate(repo=self.repo, source=self.source, dest=self.dest):
            lock.acquire()
            try:
                set_success_count()
            finally:
                lock.release()
        else:
            lock.acquire()
            try:
                set_failed_repos(self.repo['name'])
            finally:
                lock.release()
