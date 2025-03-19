from setuptools import setup


def get_description():
    with open("README.md") as file:
        return file.read()


setup(
    name="notion-client",
    version="2.3.0",
    url="https://github.com/ramnes/notion-sdk-py",
    author="Guillaume Gelin",
    author_email="contact@ramnes.eu",
    description="Python client for the official Notion API",
    long_description=get_description(),
    long_description_content_type="text/markdown",
    packages=["notion_client"],
    python_requires=">=3.7, <4",
    install_requires=[
        "httpx >= 0.23.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
    ],
    package_data={"notion_client": ["py.typed"]},
)
