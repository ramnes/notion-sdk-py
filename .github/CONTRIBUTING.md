# Contributing Guidelines

If you are a first time contributor, start by reading [this fantastic guide](https://opensource.guide/how-to-contribute/).

1. Read the docs
      - [notion-sdk-py](https://github.com/ramnes/notion-sdk-py)
      - [Notion API Reference](https://developers.notion.com/reference/intro)
      - [httpx](https://www.python-httpx.org/)

2. System Requirements
      - [git](https://git-scm.com/)
      - [python](https://www.python.org/)
      - [pip](https://pip.pypa.io/en/stable/quickstart/)

3. Fork the repository and clone it.
Checkout a new feature branch from `main`.
This [guide](https://docs.github.com/en/github/getting-started-with-github/quickstart/fork-a-repo)
will be really helpful if you are a newbie.

4. Install dependencies inside a virtual environment.

    ```shell
    python -m venv .venv && source .venv/bin/activate
    pip install -r requirements/dev.txt
    ```

5. Install [pre-commit](https://pre-commit.com/) hooks.

    ```shell
    pre-commit install
    ```

6. Follow the code style enforced by tools such as black, isort, flake, mypy.
For markdown files, markdownlint must be followed.

7. Tests must pass. If you are adding features write tests.
