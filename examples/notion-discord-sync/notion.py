from notion_client import Client

notion = Client(auth=os.getenv('NOTION_TOKEN'))

list_users_response = notion.users.list()
pprint(list_users_response.json())


dbId = '526652e30e534606a263a07702d4482c'
my_page = notion.databases.query(
    **{
        "database_id": dbId
    }
)
pprint(my_page.json())