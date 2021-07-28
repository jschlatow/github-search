This repository contains a utility for searching multiple GitHub repositories
using the GitHub API.

Highlights:

* search multiple git repositories at once
* supports multiple output formats
* special handling for README files
* configurable

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
