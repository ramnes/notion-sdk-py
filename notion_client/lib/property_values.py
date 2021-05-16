from property import *


def page_property_from_dict(d: Dict[str, object]) -> DatabaseProperty:
    property_type = d['type']
    property_type_to_class = {
        "title": TitleDatabaseProperty,
        "rich_text": RichTextDatabaseProperty,
        "number": NumberDatabaseProperty,
        "select": SelectDatabaseProperty,
        "multi_select": MultiselectDatabaseProperty,
        "date": DateDatabaseProperty,
        "people": PeopleDatabaseProperty,
        "file": FileDatabaseProperty,
        "checkbox": CheckboxDatabaseProperty,
        "url": UrlDatabaseProperty,
        "email": EmailDatabaseProperty,
        "phone_number": PhoneNumberDatabaseProperty,
        "formula": FormulaDatabaseProperty,
        "relation": RelationDatabaseProperty,
        "rollup": RollupDatabaseProperty,
        "created_time": CreatedTimeDatabaseProperty,
        "created_by": CreatedByDatabaseProperty,
        "last_edited_time": LastEditedTimeDatabaseProperty,
        "last_edited_by": LastEditedByDatabaseProperty
    }
    return property_type_to_class[property_type].from_dict(d)
