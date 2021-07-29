#
# Author: Johannes Schlatow
# Date: 2021-07-27
#

from rich.console import Console
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.panel import Panel
from rich.tree import Tree as Richtree
from rich import print

class Tree:
    def __init__(self, query="",
                       issues=dict(),
                       pr=dict(),
                       code=dict(),
                       in_readme=dict(),
                       docs=dict(),
                       paths=dict(),
                       readmes=list()):
        self.issues    = issues
        self.pr        = pr
        self.code      = code
        self.in_readme = in_readme
        self.docs      = docs
        self.paths     = paths
        self.readmes   = readmes

        self.tree = Richtree('"%s"' % query)

        self.styles       = { 'link'   : 'dim blue',
                              'issues' : 'green',
                              'pr'     : 'dim green',
                              'code'   : 'bright_red',
                              'docs'   : 'magenta',
                              'readme' : 'yellow',
                              'paths'  : 'blue',
                              'match'  : 'default'}
        self.guide_styles = { 'link'   : 'dim blue',
                              'issues' : 'green',
                              'pr'     : 'dim green',
                              'code'   : 'bright_red',
                              'docs'   : 'magenta',
                              'readme' : 'yellow',
                              'paths'  : 'blue',
                              'match'  : 'dim green'}

    def _add_subtree(self, results, stylename, title, details=None):
        if not results:
            return

        subtree = self.tree.add('[underline]%s[/underline]' % title,
                                style=self.styles[stylename],
                                guide_style=self.guide_styles[stylename])

        for alias, res in results.items():
            if res.total_count():
                subsubtree = subtree.add("%d in %s" % (res.total_count(), alias),
                                         guide_style=self.guide_styles['link'])

                if details:
                    details(alias, subsubtree, res)

    def _with_link(self, alias, subtree, res):
        if hasattr(res, 'query_url'):
            subtree.add("🌍 [link=%s]%s[/link]" % (res.query_url(), res.query_url()),
                        style=self.styles['link'])

    def _with_file_results(self, alias, subtree, res):
        for file in res.items():
            if file.path[-1] == '/':
                subsubtree = subtree.add(":file_folder: %s" % file.path)
                for readme in self.readmes[alias]:
                    if readme.startswith(file.path):
                        subsubtree.add("📄 %s" % readme,
                                       style=self.styles['readme'])

            else:
                subtree.add("📄 %s" % file.path)

    def _with_matches(self, alias, subtree, res):
        if not hasattr(res, 'query_url'):
            # res is LocalResult, list files instead of text matches
            self._with_file_results(alias, subtree, res)
            return

        for i in res.items():
            if hasattr(i, 'path'):
                markdown = False
                subsubtree = subtree.add("📄 [link=%s]%s[/link]" % (i.html_url, i.path),
                                         style=self.styles['match'],
                                         guide_style=self.guide_styles['match'])
            else:
                markdown = True
                subsubtree = subtree.add("[link=%s]#%s %s[/link]" % (i.html_url, i.number, i.title),
                                         style=self.styles['match'],
                                         guide_style=self.guide_styles['match'])

            if 'text_matches' not in i:
                continue

            for match in i.text_matches:
                if match.object_type in {'Issue'}:
                    continue

                if markdown:
                    subsubtree.add(Panel(Markdown(match.fragment),
                                         border_style=self.guide_styles['match']))
                else:
                    subsubtree.add(Panel(Syntax(match.fragment, 'C++', theme='vim', line_numbers=True),
                                         border_style=self.guide_styles['match']))

        self._with_link(alias, subtree, res)

    def print_summary(self, matches=False):
        if matches:
            details = self._with_matches
        else:
            details = self._with_link

        self._add_subtree(self.code,   stylename='code',   title='Code',
                          details=details)
        self._add_subtree(self.docs,   stylename='docs',   title='Documentation',
                          details=details)

        self._add_subtree(self.in_readme, stylename='readme', title='README',
                          details=self._with_file_results)

        self._add_subtree(self.issues, stylename='issues', title='Issues',
                          details=details)
        self._add_subtree(self.pr,     stylename='pr',     title='Pull requests',
                          details=details)

        self._add_subtree(self.paths, stylename='paths',   title='Paths',
                          details=self._with_file_results)

        print(self.tree)


class Text:
    def __init__(self, query="",
                       issues=dict(),
                       pr=dict(),
                       code=dict(),
                       in_readme=dict(),
                       docs=dict(),
                       paths=dict(),
                       readmes=list()):
        self.query     = query
        self.issues    = issues
        self.pr        = pr
        self.code      = code
        self.in_readme = in_readme
        self.docs      = docs
        self.paths     = paths
        self.readmes   = readmes

        self.console = Console()

    def _readme_in_subpath(self, path, alias):
        res = list()
        if path[-1] != '/':
            path = path + '/'
        for readme in self.readmes[alias]:
            if readme.startswith(path):
                res.append(readme)

        return res

    def print_summary_issues(self):
        if not self.issues:
            return

        for alias, res in self.issues.items():
            if res.total_count():
                self.console.print("Found %d [bold]issues[/bold] in [green]%s[/green]" % (res.total_count(), alias))
                if hasattr(res, 'query_url'):
                    self.console.print("  view: [underline blue]%s[/underline blue]" % res.query_url())

        self.console.print()

    def print_summary_pr(self):
        if not self.pr:
            return

        for alias, res in self.pr.items():
            if res.total_count():
                self.console.print("Found %d [bold]pull requests[/bold] in [green]%s[/green]" % (res.total_count(), alias))
                if hasattr(res, 'query_url'):
                    self.console.print("  view: [underline blue]%s[/underline blue]" % res.query_url())

        self.console.print()

    def print_summary_code(self):
        if not self.code:
            return
        
        for alias, res in self.code.items():
            if res.total_count():
                self.console.print("Found %d [bold]code[/bold] matches in [green]%s[/green]" % (res.total_count(), alias))
                if hasattr(res, 'query_url'):
                    self.console.print("  view: [underline blue]%s[/underline blue]" % res.query_url())

        self.console.print()

    def print_summary_in_readme(self):
        if not self.in_readme:
            return

        for alias, res in self.in_readme.items():
            if res.total_count():
                self.console.print("Found %d [bold]README[/bold] matches in [green]%s[/green]" % (res.total_count(), alias))
                for readme in res.items():
                    self.console.print("  in [magenta]%s[/magenta]" % readme.path)
                    self.console.print("    view: [underline blue]%s[/underline blue]" % readme.html_url)

        self.console.print()

    def print_summary_docs(self):
        if not self.docs:
            return

        for alias, res in self.docs.items():
            if res.total_count():
                self.console.print("Found %d [bold]documentation[/bold] matches in [green]%s[/green]" % (res.total_count(), alias))
                if hasattr(res, 'query_url'):
                    self.console.print("  view: [underline blue]%s[/underline blue]" % res.query_url())

        self.console.print()

    def print_summary_paths(self):
        if not self.paths:
            return

        for alias, res in self.paths.items():
            if res.total_count():
                self.console.print("Found %d [bold]path[/bold] matches in [green]%s[/green]" % (res.total_count(), alias))
                for path in res.items():
                    self.console.print("  [magenta]%s[/magenta]" % path.path)
                    for readme in self._readme_in_subpath(path.path, alias):
                        self.console.print("    has [bold]README[/bold] in [underline]%s[/underline]" % readme)

        self.console.print()

    def print_summary(self):

        self.console.print("[bold]Searching for '%s':[/bold]\n" % self.query)

        self.print_summary_issues()
        self.print_summary_pr()
        self.print_summary_code()
        self.print_summary_in_readme()
        self.print_summary_docs()
        self.print_summary_paths()
