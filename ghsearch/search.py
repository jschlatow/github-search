#
# Author: Johannes Schlatow
# Date: 2021-07-27
#

from ghapi.all import GhApi, pages
from requests.utils import requote_uri
import subprocess

class LocalPath:
    def __init__(self, rel_path, base_path):
        self.path = rel_path
        self.html_url = 'file://' + base_path + '/' + rel_path

    def __hash__(self):
        return hash(self.path)

    def __eq__(self, rhs):
        return self.path == rhs.path


class GitSearch:
    def __init__(self, path):
        self.path = path

    def _run_git(self, args):
        result = subprocess.run(args, cwd=self.path, capture_output=True,
                                                     text=True,
                                                     check=True)
        return result.stdout

    def find_in_readme(self, query):
        res = list()
        args = ['/usr/bin/git', 'grep', '-l', query, '--', '*README']
        stdout = self._run_git(args)
        for p in iter(stdout.splitlines()):
            res.append(LocalPath(p, self.path))

        return res

    def find_paths(self, query):
        res = set()
        args1 = ['/usr/bin/git', 'ls-tree', '--name-only', 'master', '-r']
        args2 = ['grep', '-i', query]

        git = subprocess.Popen(args1, cwd=self.path, stdout=subprocess.PIPE)
        stdout = subprocess.run(args2, stdin=git.stdout, capture_output=True, text=True).stdout
        git.wait()

        for p in iter(stdout.splitlines()):
            pos = p.lower().find(query.lower())
            if pos == -1:
                pos = len(p)

            end = p.find('/', pos)
            if end == -1:
                end = len(p)

            res.add(LocalPath(p[0:end], self.path))

        return list(res)

class Manager:
    def __init__(self, repos, token=None):
        self.repos = list()
        self.token = token
        self.api   = GhApi(token=token)

        for repo in repos:
            if not repo['enabled']: continue

            repo['repo'] = '%s/%s' % (repo['owner'], repo['name'])
            if 'alias' not in repo:
                repo['alias'] = repo['repo']

            flags = ['issues',
                     'pullrequests',
                     'readme',
                     'paths',
                     'code']
            for f in flags:
                if f not in repo:
                    repo[f] = True

            self.repos.append(repo)

    def _query_single(self, f, query, repo, per_page=10):
        return Result(repo,
                      query,
                      f(q='%s repo:%s' % (query, repo), per_page=per_page))

    def _query_all(self, f, query, repo):
        res = f(q='%s repo:%s' % (query, repo), per_page=100)

        if res.total_count > 100:
            res = pages(f, self.api.last_page(),
                        q='%s repo:%s' % (query, repo))


        return Result(repo, query, res)

    def find_issues(self, s):
        res = dict()
        for r in self.repos:
            if not r['issues']: continue

            query = '%s type:issue' % s
            repo  = r['repo']

            res[r['alias']] = \
                self._query_single(self.api.search.issues_and_pull_requests,
                                   query,
                                   repo)

        return res

    def find_pull_requests(self, s):
        res = dict()
        for r in self.repos:
            if not r['pullrequests']: continue

            query = '%s type:pr' % s
            repo  = r['repo']

            res[r['alias']] = \
                self._query_single(self.api.search.issues_and_pull_requests,
                                   query,
                                   repo)

        return res

    def find_code(self, s):
        res = dict()

        for r in self.repos:
            if not r['code']: continue

            query = s
            repo  = r['repo']

            if 'doc-folder' in r:
                query += ' -path:%s' % r['doc-folder']

            res[r['alias']] = \
                self._query_single(self.api.search.code,
                                   query,
                                   repo)

        return res

    def find_docs(self, s):
        res = dict()

        for r in self.repos:
            if 'doc-folder' not in r: continue

            query = s + ' path:%s' % r['doc-folder']
            repo = r['repo']

            res[r['alias']] = \
                self._query_single(self.api.search.code,
                                   query,
                                   repo)

        return res

    def find_paths(self, s):
        res = dict()

        for r in self.repos:
            if not r['paths']: continue

            if 'local-path' in r:
                res[r['alias']] = LocalResult(r['alias'],
                                              GitSearch(r['local-path']).find_paths(s))
            else:
                query = s + ' in:path'
                repo = r['repo']
                res[r['alias']] = \
                    self._query_all(self.api.search.code,
                                    query,
                                    repo)

        return res

    def find_in_readme(self, s):
        res = dict()

        for r in self.repos:
            if not r['readme']: continue

            if 'local-path' in r:
                res[r['alias']] = LocalResult(r['alias'],
                                              GitSearch(r['local-path']).find_in_readme(s))
            else:
                query = s + ' filename:README'
                repo  = r['repo']

                res[r['alias']] = \
                    self._query_all(self.api.search.code,
                                    query,
                                    repo)

        return res

    def find_readme(self):
        res = dict()

        for r in self.repos:
            if not r['paths']: continue

            if 'local-path' in r:
                tmp = LocalResult(r['alias'],
                                  GitSearch(r['local-path']).find_paths('README'))
            else:
                query = 'filename:README'
                repo = r['repo']
                tmp = self._query_all(self.api.search.code,
                                      query,
                                      repo)

            res[r['alias']] = dict()
            for readme in tmp.items():
                res[r['alias']][readme.path] = readme

        return res

    def remaining_quota(self):
        limit_rem = self.api.limit_rem
        limit     = 10
        if self.token:
            limit = 30

        return (limit_rem, limit)


class LocalResult:
    def __init__(self, repo, results):
        self.repo    = repo
        self.results = results

    def total_count(self):
        return len(self.results)

    def items(self):
        return self.results


class Result:
    def __init__(self, repo, query, results):
        self.repo    = repo
        self.query   = query
        self.results = results

    def total_count(self):
        if hasattr(self.results, 'total_count'):
            return self.results.total_count
        else:
            return len(self.results)

    def query_url(self):
        uri = 'https://github.com/%s/search?q=%s' % (self.repo, self.query)
        return requote_uri(uri)

    def items(self):
        return self.results['items']

    def __getattr__(self, attr):
        return self.results.getattr(attr)

