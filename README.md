This repository contains a utility for searching multiple GitHub repositories
using the GitHub API.

Highlights:

* search multiple git repositories at once (issues, pull requests, paths, code)
* supports multiple output formats
* special handling for README files
* configurable

Limitations:

* GitHub search results shouldn't be trusted to be complete.
* GitHub ignores most special characters in your search query [see](https://docs.github.com/en/github/searching-for-information-on-github/searching-on-github/searching-code#considerations-for-code-search)

# Prerequisites

* Python 3
* Third-party modules
	* [rich](https://rich.readthedocs.io/)
	* [ghapi](https://ghapi.fast.ai/)
	* [requests](https://pypi.org/project/requests/)

# Configuration

The ghs utility must be provided with a YAML configuration file that
specifies the respositories to be searched.
By default, ghs looks for a `config.yaml` file in the working directory.
Alternatively, you can provide the location of you configuration file via the
`--config /path/to/config.yaml` command line option.

## token

The GitHub API enforces a rate limit of 10 search requests per minute for
unauthenticated users.
In order to raise the rate limite to 30 requests per minute, you can
[create a personal API token](https://github.com/settings/tokens) and add it to
your configuration file.

```yaml
token: foobar...
```

## repositories

A repository is specified by the mandatory fields `owner` and `name`, which
you find in the repository's URL (i.e. `https://github.com/{owner}/{name}`).

Optional attributes can be used to switch off certain search categories or to
disable the repository entirely.

For more details, please have a look at the [examples](examples/).

**Mandatory attributes**

* owner
* name

**Optional attributes**

* alias: repository alias (default: owner/name)
* enabled (default: yes)
* issues (default: yes)
* pullrequests (default: yes)
* paths (default: yes)
* readme (default: yes)
* doc-folder: folder containing documentation (for docs search)
* local-path: local path to git repo (for exact path search and reducing API requests)

## Usage examples

By default, ghs prints a summary of search results.
The summary contains the total number of matches and a weblink to the full
search query.

E.g., you can search the genode repositories for the term 'vfs' as follows:
```
ghs --config examples/genode.yaml vfs
```

You can switch on the output of the first 10 text matches in every repository
via the `--matches` switch.
Furthermore, you can restrict the search categories by using the `--where` option.

E.g., you can list the first 10 open issues and pull requests that match
'nic_router' as follows:

```
ghs --config examples/genode.yaml nic_router is:open --where issues pullrequest --matches
```

Note, when using a bunch of repositories the, you may easily exhaust the limit
of 10 (resp. 30) queries per minute.
If you have a local check out of some repositories, you can circumvent this
by providing the optional `local-path` attribute.
When set, ghs will use `git grep` and `git ls-tree` to search README files and
path names.
