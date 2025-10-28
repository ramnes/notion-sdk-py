"""Generate random data and populate a Notion database."""

import os
import sys
import random
from datetime import datetime, timedelta
from typing import Any, Dict, List

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


def make_fake_properties_data(properties: Dict[str, Any]) -> Dict[str, Any]:
    """Generate fake data matching the database property schema."""
    fake_data = {}

    for prop_name, prop_info in properties.items():
        prop_type = prop_info.get("type")

        if prop_type in [
            "formula",
            "rollup",
            "created_time",
            "created_by",
            "last_edited_time",
            "last_edited_by",
        ]:
            continue
        if prop_type == "title":
            fake_data[prop_name] = {
                "title": [{"text": {"content": fake.catch_phrase()}}]
            }

        elif prop_type == "rich_text":
            fake_data[prop_name] = {
                "rich_text": [{"text": {"content": fake.paragraph(nb_sentences=2)}}]
            }

        elif prop_type == "number":
            fake_data[prop_name] = {"number": random.randint(0, 1000)}

        elif prop_type == "select" and prop_info.get("select", {}).get("options"):
            options = prop_info["select"]["options"]
            if options:
                selected = random.choice(options)
                fake_data[prop_name] = {"select": {"name": selected["name"]}}

        elif prop_type == "multi_select" and prop_info.get("multi_select", {}).get(
            "options"
        ):
            options = prop_info["multi_select"]["options"]
            if options:
                num_selections = random.randint(1, min(3, len(options)))
                selected = random.sample(options, num_selections)
                fake_data[prop_name] = {
                    "multi_select": [{"name": opt["name"]} for opt in selected]
                }

        elif prop_type == "date":
            start_date = datetime.now()
            random_days = random.randint(0, 30)
            random_date = start_date + timedelta(days=random_days)
            fake_data[prop_name] = {"date": {"start": random_date.strftime("%Y-%m-%d")}}

        elif prop_type == "checkbox":
            fake_data[prop_name] = {"checkbox": random.choice([True, False])}

        elif prop_type == "url":
            fake_data[prop_name] = {"url": fake.url()}

        elif prop_type == "email":
            fake_data[prop_name] = {"email": fake.email()}

        elif prop_type == "phone_number":
            fake_data[prop_name] = {"phone_number": fake.phone_number()}

        elif prop_type == "people":
            pass  # Requires actual Notion user IDs

        elif prop_type == "files":
            fake_data[prop_name] = {
                "files": [
                    {
                        "type": "external",
                        "name": "Sample file",
                        "external": {"url": fake.url()},
                    }
                ]
            }

    return fake_data


def extract_property_value_to_string(prop_value: Any, prop_type: str) -> str:
    """Convert Notion property values to readable strings for display."""
    if prop_value is None:
        return "N/A"

    if prop_type == "title":
        texts = prop_value.get("title", [])
        return "".join(text.get("text", {}).get("content", "") for text in texts)

    elif prop_type == "rich_text":
        texts = prop_value.get("rich_text", [])
        return "".join(text.get("text", {}).get("content", "") for text in texts)

    elif prop_type == "number":
        return str(prop_value.get("number", "N/A"))

    elif prop_type == "select":
        select = prop_value.get("select")
        return select.get("name", "N/A") if select else "N/A"

    elif prop_type == "multi_select":
        options = prop_value.get("multi_select", [])
        return ", ".join(opt.get("name", "") for opt in options) if options else "N/A"

    elif prop_type == "date":
        date_obj = prop_value.get("date")
        if date_obj:
            start = date_obj.get("start", "N/A")
            end = date_obj.get("end")
            return f"{start} - {end}" if end else start
        return "N/A"

    elif prop_type == "checkbox":
        return "✓" if prop_value.get("checkbox") else "✗"

    elif prop_type == "url":
        return prop_value.get("url", "N/A")

    elif prop_type == "email":
        return prop_value.get("email", "N/A")

    elif prop_type == "phone_number":
        return prop_value.get("phone_number", "N/A")

    elif prop_type == "formula":
        formula = prop_value.get("formula", {})
        formula_type = formula.get("type")
        if formula_type:
            return str(formula.get(formula_type, "N/A"))
        return "N/A"

    elif prop_type == "rollup":
        rollup = prop_value.get("rollup", {})
        rollup_type = rollup.get("type")
        if rollup_type == "array":
            return str(len(rollup.get("array", [])))
        elif rollup_type:
            return str(rollup.get(rollup_type, "N/A"))
        return "N/A"

    elif prop_type == "people":
        people = prop_value.get("people", [])
        return (
            ", ".join(person.get("name", "") for person in people) if people else "N/A"
        )

    elif prop_type == "files":
        files = prop_value.get("files", [])
        return (
            ", ".join(file.get("name", "Unnamed") for file in files) if files else "N/A"
        )

    elif prop_type == "created_time":
        return prop_value.get("created_time", "N/A")

    elif prop_type == "last_edited_time":
        return prop_value.get("last_edited_time", "N/A")

    elif prop_type == "created_by":
        user = prop_value.get("created_by", {})
        return user.get("name", user.get("id", "N/A"))

    elif prop_type == "last_edited_by":
        user = prop_value.get("last_edited_by", {})
        return user.get("name", user.get("id", "N/A"))

    else:
        return str(prop_value)


def exercise_writing(database_id: str, properties: Dict[str, Any]) -> List[str]:
    """Create 10 pages with random data in the database."""
    print("\nCreating test data...")
    created_pages = []

    for i in range(10):
        fake_data = make_fake_properties_data(properties)
        response = notion.pages.create(
            parent={"database_id": database_id}, properties=fake_data
        )
        created_pages.append(response["id"])
        print(f"  Created {i+1}/10")

    print(f"Done. Created {len(created_pages)} pages.")
    return created_pages


def exercise_reading(database_id: str, start_time: str):
    """Query and display pages created after the given timestamp."""
    print("\nQuerying created pages...")

    response = notion.data_sources.query(
        data_source_id=database_id,
        filter={"timestamp": "created_time", "created_time": {"after": start_time}},
        sorts=[{"timestamp": "created_time", "direction": "descending"}],
    )

    results = response.get("results", [])
    print(f"Found {len(results)} pages\n")

    for i, page in enumerate(results[:3], 1):
        print(f"[{i}] {page['id'][:8]}...")
        for prop_name, prop_value in page["properties"].items():
            prop_type = prop_value["type"]
            value_str = extract_property_value_to_string(prop_value, prop_type)
            if len(value_str) > 50:
                value_str = value_str[:47] + "..."
            print(f"    {prop_name}: {value_str}")


def exercise_filters(database_id: str, properties: Dict[str, Any]):
    """Demonstrate filtering by select and text properties."""
    print("\nTesting filters...")

    select_property = None
    select_options = []

    for prop_name, prop_info in properties.items():
        if prop_info["type"] == "select" and prop_info.get("select", {}).get("options"):
            select_property = prop_name
            select_options = prop_info["select"]["options"]
            break

    if select_property and select_options:
        random_option = random.choice(select_options)
        print(f"  Filter: {select_property}={random_option['name']}")

        response = notion.data_sources.query(
            data_source_id=database_id,
            filter={
                "property": select_property,
                "select": {"equals": random_option["name"]},
            },
        )

        results = response.get("results", [])
        print(f"  Results: {len(results)}")

    text_property = None
    for prop_name, prop_info in properties.items():
        if prop_info["type"] in ["title", "rich_text"]:
            text_property = prop_name
            break

    if text_property:
        search_text = "the"
        print(f"  Filter: {text_property} contains '{search_text}'")

        filter_config = {
            "property": text_property,
        }

        if properties[text_property]["type"] == "title":
            filter_config["title"] = {"contains": search_text}
        else:
            filter_config["rich_text"] = {"contains": search_text}

        response = notion.data_sources.query(
            data_source_id=database_id, filter=filter_config
        )

        results = response.get("results", [])
        print(f"  Results: {len(results)}")


def main():
    print("notion-sdk-py: generate_random_data")
    print("-" * 40)

    start_time = datetime.utcnow().isoformat() + "Z"

    print("Looking for database...")

    try:
        search_response = notion.search()
        all_results = search_response.get("results", [])
        databases = [r for r in all_results if r.get("object") == "data_source"]

        if not databases:
            print("ERROR: No databases found. Share a database with your integration.")
            sys.exit(1)

        database = databases[0]
        data_source_id = database["id"]

        database_title = (
            "".join(
                text.get("text", {}).get("content", "")
                for text in database.get("title", [])
            )
            if isinstance(database.get("title"), list)
            else "Untitled"
        )

        print(f"Using: {database_title}")

        db_response = notion.data_sources.retrieve(data_source_id=data_source_id)

        parent = db_response.get("parent", {})
        if parent.get("type") == "database_id":
            database_id = parent.get("database_id")
        else:
            database_id = data_source_id

        properties = db_response.get("properties", {})
        print(f"Schema: {len(properties)} properties")

        exercise_writing(database_id, properties)
        exercise_reading(data_source_id, start_time)
        exercise_filters(data_source_id, properties)

        print("\nComplete.")

    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
