"""Generate virtual files for mkdocs."""

import mkdocs_gen_files


def docs_stub(module_name):
    return f"::: notion_client.{module_name}\
        \n\trendering:\n\t\tshow_root_heading: true\n\t\tshow_source: false"


virtual_files = {
    "index.md": "--8<-- 'README.md'",
    "license.md": "```text\n--8<-- 'LICENSE'\n```",
    "reference/api_endpoints.md": docs_stub("api_endpoints"),
    "reference/client.md": docs_stub("client"),
    "reference/errors.md": docs_stub("errors"),
    "reference/helpers.md": docs_stub("helpers"),
    "contributing/contributing.md": "--8<-- '.github/CONTRIBUTING.md'",
}

for file_name, content in virtual_files.items():
    with mkdocs_gen_files.open(file_name, "w") as file:
        print(content, file=file)
