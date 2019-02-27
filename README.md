# CircleTUI

* Get your things square with CircleCI! *

---

This is a small tool which allows you to browse build logs from CircleCI from
your terminal.

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
