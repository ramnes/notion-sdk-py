# Find the official Notion API client @ https://github.com/ramnes/notion-sdk-py
# pip install notion-client
import os
import random
import json
from datetime import datetime
from typing import Any, Dict, Optional, Tuple
from urllib.parse import unquote

from notion_client import Client
from faker import Faker

fake = Faker()

try:
    from dotenv import load_dotenv

    load_dotenv()
except ModuleNotFoundError:
    print("Could not load .env because python-dotenv not found.")

NOTION_TOKEN = os.getenv("NOTION_TOKEN", "")

if not NOTION_TOKEN:
    print("NOTION_TOKEN not found.")
    NOTION_TOKEN = input("Enter your integration token: ").strip()

notion = Client(auth=NOTION_TOKEN)

start_time = datetime.utcnow().replace(second=0, microsecond=0, tzinfo=None)


def user_to_string(user: Dict[str, Any]) -> str:
    user_id = user.get("id", "")
    name = user.get("name") or "Unknown Name"
    return f"{user_id}: {name}"


# Given the properties of a database, generate an object full of
# random data that can be used to generate new rows in our Notion database.
def make_fake_properties_data(properties: Dict[str, Any]) -> Dict[str, Any]:
    property_values = {}

    for name, property in properties.items():
        prop_type = property.get("type")

        if prop_type == "date":
            property_values[name] = {
                "type": "date",
                "date": {"start": fake.date_time_this_year().isoformat()},
            }
        elif prop_type == "multi_select" and property.get("multi_select", {}).get(
            "options"
        ):
            options = property["multi_select"]["options"]
            if options:
                num_selections = random.randint(1, min(3, len(options)))
                selected = random.sample(options, num_selections)
                property_values[name] = {
                    "type": "multi_select",
                    "multi_select": [{"name": opt["name"]} for opt in selected],
                }
        elif prop_type == "select" and property.get("select", {}).get("options"):
            options = property["select"]["options"]
            if options:
                selected = random.choice(options)
                property_values[name] = {
                    "type": "select",
                    "select": {"name": selected["name"]},
                }
        elif prop_type == "email":
            property_values[name] = {"type": "email", "email": fake.email()}
        elif prop_type == "checkbox":
            property_values[name] = {"type": "checkbox", "checkbox": fake.boolean()}
        elif prop_type == "url":
            property_values[name] = {"type": "url", "url": fake.url()}
        elif prop_type == "number":
            property_values[name] = {"type": "number", "number": fake.random_int()}
        elif prop_type == "title":
            property_values[name] = {
                "type": "title",
                "title": [
                    {"type": "text", "text": {"content": " ".join(fake.words(3))}}
                ],
            }
        elif prop_type == "rich_text":
            property_values[name] = {
                "type": "rich_text",
                "rich_text": [{"type": "text", "text": {"content": fake.first_name()}}],
            }
        elif prop_type == "phone_number":
            property_values[name] = {
                "type": "phone_number",
                "phone_number": fake.phone_number(),
            }
        else:
            print("unimplemented property type: ", prop_type)

    return property_values


def extract_property_item_value_to_string(property: Dict[str, Any]) -> str:
    prop_type = property.get("type")

    if prop_type == "checkbox":
        return str(property.get("checkbox", ""))
    elif prop_type == "created_by":
        return user_to_string(property.get("created_by", {}))
    elif prop_type == "created_time":
        ct = property.get("created_time")
        return (
            datetime.fromisoformat(ct.replace("Z", "+00:00")).isoformat() if ct else ""
        )
    elif prop_type == "date":
        date_obj = property.get("date")
        return (
            datetime.fromisoformat(date_obj["start"].replace("Z", "+00:00")).isoformat()
            if date_obj
            else ""
        )
    elif prop_type == "email":
        return property.get("email") or ""
    elif prop_type == "url":
        return property.get("url") or ""
    elif prop_type == "number":
        num = property.get("number")
        return str(num) if isinstance(num, (int, float)) else ""
    elif prop_type == "phone_number":
        return property.get("phone_number") or ""
    elif prop_type == "select":
        select = property.get("select")
        if not select:
            return ""
        return f"{select.get('id', '')} {select.get('name', '')}"
    elif prop_type == "multi_select":
        multi_select = property.get("multi_select", [])
        if not multi_select:
            return ""
        return ", ".join(
            f"{opt.get('id', '')} {opt.get('name', '')}" for opt in multi_select
        )
    elif prop_type == "people":
        return user_to_string(property.get("people", {}))
    elif prop_type == "last_edited_by":
        return user_to_string(property.get("last_edited_by", {}))
    elif prop_type == "last_edited_time":
        let = property.get("last_edited_time")
        return (
            datetime.fromisoformat(let.replace("Z", "+00:00")).isoformat()
            if let
            else ""
        )
    elif prop_type == "title":
        return property.get("title", {}).get("plain_text", "")
    elif prop_type == "rich_text":
        return property.get("rich_text", {}).get("plain_text", "")
    elif prop_type == "files":
        files = property.get("files", [])
        return ", ".join(file.get("name", "") for file in files)
    elif prop_type == "formula":
        formula = property.get("formula", {})
        formula_type = formula.get("type")
        if formula_type == "string":
            return formula.get("string") or "???"
        elif formula_type == "number":
            num = formula.get("number")
            return str(num) if num is not None else "???"
        elif formula_type == "boolean":
            bool_val = formula.get("boolean")
            return str(bool_val) if bool_val is not None else "???"
        elif formula_type == "date":
            date_obj = formula.get("date")
            return (
                datetime.fromisoformat(
                    date_obj["start"].replace("Z", "+00:00")
                ).isoformat()
                if date_obj and date_obj.get("start")
                else "???"
            )
        return "???"
    elif prop_type == "rollup":
        rollup = property.get("rollup", {})
        rollup_type = rollup.get("type")
        if rollup_type == "number":
            num = rollup.get("number")
            return str(num) if num is not None else "???"
        elif rollup_type == "date":
            date_obj = rollup.get("date")
            return (
                datetime.fromisoformat(
                    date_obj["start"].replace("Z", "+00:00")
                ).isoformat()
                if date_obj and date_obj.get("start")
                else "???"
            )
        elif rollup_type == "array":
            return json.dumps(rollup.get("array", []))
        elif rollup_type in ("incomplete", "unsupported"):
            return rollup_type
        return "???"
    elif prop_type == "relation":
        relation = property.get("relation")
        if relation:
            return relation.get("id", "???")
        return "???"
    elif prop_type == "status":
        return property.get("status", {}).get("name", "")
    elif prop_type == "button":
        return property.get("button", {}).get("name", "")
    elif prop_type == "unique_id":
        unique_id = property.get("unique_id", {})
        prefix = unique_id.get("prefix") or ""
        number = unique_id.get("number") or ""
        return f"{prefix}{number}"
    elif prop_type == "verification":
        return property.get("verification", {}).get("state", "")

    return ""


def extract_value_to_string(property: Dict[str, Any]) -> str:
    if property.get("object") == "property_item":
        return extract_property_item_value_to_string(property)
    elif property.get("object") == "list":
        results = property.get("results", [])
        return ", ".join(
            extract_property_item_value_to_string(result) for result in results
        )
    return ""


def exercise_writing(data_source_id: str, properties: Dict[str, Any]):
    print("\n\n********* Exercising Writing *********\n\n")

    rows_to_write = 10

    for i in range(rows_to_write):
        properties_data = make_fake_properties_data(properties)

        notion.pages.create(
            parent={"data_source_id": data_source_id}, properties=properties_data
        )

    print(f"Wrote {rows_to_write} rows after {start_time}")


def exercise_reading(data_source_id: str, _properties: Dict[str, Any]):
    print("\n\n********* Exercising Reading *********\n\n")

    query_response = notion.data_sources.query(data_source_id=data_source_id)

    num_old_rows = 0
    for page in query_response.get("results", []):
        if "url" not in page:
            continue

        created_time = datetime.fromisoformat(
            page["created_time"].replace("Z", "+00:00")
        )
        start_dt = start_time.replace(tzinfo=created_time.tzinfo)
        if start_dt > created_time:
            num_old_rows += 1
            return

        print(f"New page: {page['id']}")

        for name, property in page["properties"].items():
            property_response = notion.pages.properties.retrieve(
                page_id=page["id"], property_id=property["id"]
            )
            print(
                f" - {name} {property['id']} - {extract_value_to_string(property_response)}"
            )

    print(f"Skipped printing {num_old_rows} rows that were written before {start_time}")


def find_random_select_column_name_and_value(
    properties: Dict[str, Any],
) -> Tuple[str, Optional[str]]:
    options = []
    for name, property in properties.items():
        if property.get("type") == "select" and property.get("select", {}).get(
            "options"
        ):
            select_options = property["select"]["options"]
            if select_options:
                options.append(
                    {
                        "name": name,
                        "value": random.choice(select_options)["name"],
                    }
                )

    if options:
        selected = random.choice(options)
        return selected["name"], selected["value"]

    return "", None


def exercise_filters(data_source_id: str, properties: Dict[str, Any]):
    print("\n\n********* Exercising Filters *********\n\n")

    select_column_name, select_column_value = find_random_select_column_name_and_value(
        properties
    )

    if not select_column_name or not select_column_value:
        raise ValueError("need a select column to run this part of the example")

    print(f"Looking for {select_column_name}={select_column_value}")

    query_filter_select_filter_type_based = {
        "property": select_column_name,
        "select": {"equals": select_column_value},
    }

    matching_select_results = notion.data_sources.query(
        data_source_id=data_source_id, filter=query_filter_select_filter_type_based
    )

    print(
        f"had {len(matching_select_results.get('results', []))} matching rows for {select_column_name}={select_column_value}"
    )

    text_column = None
    for property in properties.values():
        if property.get("type") == "rich_text":
            text_column = property
            break

    if not text_column:
        raise ValueError(
            "Need a rich_text column for this part of the test, could not find one"
        )

    text_column_id = unquote(text_column["id"])
    letter_to_find = fake.word()[:1]

    print(
        f'\n\nLooking for text column with id "{text_column_id}" contains letter "{letter_to_find}"'
    )

    text_filter = {
        "property": text_column_id,
        "rich_text": {"contains": letter_to_find},
    }

    matching_text_results = notion.data_sources.query(
        data_source_id=data_source_id, filter=text_filter
    )

    print(
        f'Had {len(matching_text_results.get("results", []))} matching rows in column with ID "{text_column_id}" containing letter "{letter_to_find}"'
    )


def main():
    search_results = notion.search(
        filter={"property": "object", "value": "data_source"}
    )

    if not search_results.get("results"):
        raise ValueError("This bot doesn't have access to any databases!")

    data_source = search_results["results"][0]

    if not data_source or data_source.get("object") != "data_source":
        raise ValueError("This bot doesn't have access to any databases!")

    exercise_writing(data_source["id"], data_source.get("properties", {}))
    exercise_reading(data_source["id"], data_source.get("properties", {}))
    exercise_filters(data_source["id"], data_source.get("properties", {}))


if __name__ == "__main__":
    main()
