# Contributing guidelines

!!! tip
    If you are a first time contributor, please start by reading
    [this fantastic guide](https://opensource.guide/how-to-contribute/).

Any serious contribution to notion-sdk-py is always welcome, regardless of your
experience.

If you want to contribute on the code specifically:

1. Install Git and Python on your system.
2. Fork the repository and clone it.
3. Checkout a new feature branch from `main`:

    ```shell
    git checkout my-feature
    ```

4. Install dependencies inside a virtual environment:

    ```shell
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements/dev.txt
    ```

5. Install [pre-commit](https://pre-commit.com/) hooks:

    ```shell
    pre-commit install
    ```

You should now be ready to hack!

You can run the tests with `pytest` in the main directory. Please make
sure the tests (and pre-commit hooks) pass before opening a pull
request.

Coverage must stay at 100%. Write tests if you add new features.

Thanks for your help!
