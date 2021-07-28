#
# Author: Johannes Schlatow
# Date: 2021-07-27
#

from rich.console import Console

class Text:
    def __init__(self, issues=dict(),
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
                self.console.print("  view: [underline blue]%s[/underline blue]" % res.query_url())

        self.console.print()

    def print_summary_pr(self):
        if not self.pr:
            return

        for alias, res in self.pr.items():
            if res.total_count():
                self.console.print("Found %d [bold]pull requests[/bold] in [green]%s[/green]" % (res.total_count(), alias))
                self.console.print("  view: [underline blue]%s[/underline blue]" % res.query_url())

        self.console.print()

    def print_summary_code(self):
        if not self.code:
            return
        
        for alias, res in self.code.items():
            if res.total_count():
                self.console.print("Found %d [bold]code[/bold] matches in [green]%s[/green]" % (res.total_count(), alias))
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

        self.print_summary_issues()
        self.print_summary_pr()
        self.print_summary_code()
        self.print_summary_in_readme()
        self.print_summary_docs()
        self.print_summary_paths()
