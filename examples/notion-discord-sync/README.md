# Sample Integration: Discord to Notion

## About the Integration 
This is a Discord bot that ports book recommendations from Discord to Notion. Here is a simple diagram to illustrate what the bot does!
![Could not Load Diagram](https://github.com/FruitVodka/notion-discord-sync/blob/main/examples/notion-discord-sync/flow-diagram.png)

## Try it Yourself
To test this Discord bot, you will need to set up a few things

### Notion Reading List Database Template
You can duplicate [this](https://www.notion.so/e2b278fd05574df694833e6790e02340?v=34c458559056411d8cbd3bc3a7f406d6) template for running this example. You need to create a Notion integration as explained in the Notion API documentation [here](https://developers.notion.com/docs).
After doing this, you will obtain a **Notion Internal Integration Token** and a **database ID**. Note these down somewhere secure to use later.

### Discord Bot
Follow the instructions [here](https://realpython.com/how-to-make-a-discord-bot-python/) to create a Discord Bot and add it to your server. Make sure to give the bot permissions to view the channel(s) where book recommendations will be coming in! At the end of this, you will obtain a **Discord Bot Token**. Note this down too.

### Google Books API
Create a GCP project and get your **Google Books API credentials** by following [these](https://developers.google.com/books/docs/v1/using) instructions.

### Running the Bot
1. Clone this repository locally: `git clone https://github.com/ramnes/notion-sdk-py.git`
2. Switch into this project: `cd notion-sdk-py/examples/notion-discord-sync`
3. Add the credentials from the previous sections to the `.env` file against the appropriate variables
4. Install the requirements in `requirements.txt`
5. Run `bot.py` - it contains the code that powers this Discord bot

## Resources
If you want to use your own database instead of following the above-mentioned template, you might find [this](https://developers.notion.com/reference/page#page-property-value) description of the page object in Notion useful.
For any feedback or suggestions, raise a discussion or issue!
