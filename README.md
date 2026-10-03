# HackYeah 2026

[![CI](https://github.com/nekeal/hackyeah2026/actions/workflows/backend.yml/badge.svg)](https://github.com/nekeal/hackyeah2026/actions)

This is project developed as part of hackyeah 2026

# Prerequisites

## Native way with virtualenv
- [Python3.14+](https://www.python.org/downloads/)
- [uv](https://github.com/astral-sh/uv)

## Docker way
- [Docker](https://docs.docker.com/engine/install/)  
- [Docker Compose](https://docs.docker.com/compose/install/)

## Local Development

## Native way with virtualenv

First create postgresql database:

```sql
create user hackyeah2026 with createdb;
alter user hackyeah2026 password 'hackyeah2026';
create database hackyeah2026 owner hackyeah2026;
```
Now you can setup virtualenv and django:
```bash
pip install uv
make bootstrap
```

## Docker way

Start the dev server for local development:
```bash
docker compose up
```

Run a command inside the docker container:

```bash
docker compose run --rm web [command]
```


## Pre-commit hooks

To install pre-commit hooks run:

```bash
pre-commit install
```

# Ideas:

- mark places where you can rent a wheelchair (for tourists) 
- mark places like museums where you can borrow a wheelchair
