# CircleTUI

_Get your things square with CircleCI!_

[![CircleCI](https://circleci.com/gh/wurbanski/circle-tui.svg?style=svg)](https://circleci.com/gh/wurbanski/circle-tui)

## Description

This is a small tool which allows you to browse build logs from CircleCI from
your terminal.
It uses your CircleCI CLI config (`~/.circleci/cli.yml`) to get information
about you, such as your token.

Yes, it's expected that you have a [working CircleCI CLI configured](https://circleci.com/docs/2.0/local-cli/). Sorry! But you should have anyway
:).

**NOTE:** You can add additional field to specify your default project, e.g.
`project: github/wurbanski/circle-tui`.

## Run with docker

If you don't want to give a lot of thought into running this, use docker!
`docker run -it -v ~/.circleci/cli.yml:/app/cli.yml wurbanski/circle-tui:latest --config /app/cli.yml`

## Installation

circle-tui requires python 3 and was tested on python 3.6 and 3.7. You might require development tools and python 3 development headers on your machine.

Steps:
1. Create virtualenv with python 3 using your preferred method, e.g. `mkvirtualenv -p $(which python 3) circle-tui`
2. Activate virtualenv and install requried packages: `pip install -r requirements.txt`
3. Run app: `python circle-tui.py`

## Usage

```
usage: circle-tui.py [-h] [--config CONFIG] [--project PROJECT]
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
