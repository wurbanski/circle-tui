# CircleTUI

_Get your things square with CircleCI!_

---

This is a small tool which allows you to browse build logs from CircleCI from
your terminal.
It uses your CircleCI CLI config (`~/.circleci/cli.yml`) to get information
about you, such as your token.

**NOTE:** You can add additional field to specify your default project, e.g.
`project: github/wurbanski/circle-tui`.

## Run with docker

If you don't want to give a lot of thought into running this, use docker!
`docker run -it -v ~/.circleci/cli.yml:/app/cli.yml wurbanski/circle-tui:latest --config /app/cli.yml`

```
usage: main.py [-h] [--config CONFIG] [--project PROJECT]
               [--build_num BUILD_NUM] [--step STEP] [--non_interactive]

TUI/Log viewer for CircleCI

optional arguments:
  -h, --help            show this help message and exit
  --config CONFIG       Location of config file
  --project PROJECT     Project name in format: <vcs>/<username>/<reponame>
  --build_num BUILD_NUM
                        Build number
  --step STEP           Steps
  --non_interactive     Use non-interactive mode - just print the logs,
                        requires all other parameters
```
