# InvisibleServant

A D&D game organisation tool for discord

## Development install

- Clone repository
  - ```git clone https://github.com/OperationXen/InvisibleServant.git```
- Create and activate python virtual environment (optional)
  - ```python -m pip install virtualenv```
  - ```python -m virtualenv venv```
  - ```./venv/script/activate```
  - Install dependencies
  - ```python -m pip install -r requirements.txt```

- Create sqllite database
  - ```python CoreServer/manage.py makemigrations```
  - ```python CoreServer/manage.py migrate```

- Create Web interface user (optional)
  - ```python CoreServer/manage.py createsuperuser```

- Create discord token
  - This is a slightly involved process, but it is relatively well documented here: https://www.writebots.com/discord-bot-token/
  - This token should be added to the CoreServer/config/settings.py file as DISCORD_TOKEN variable
- Add testing guild identity to config
  - Right click in Discord app on the server you're using for testing, click "Copy ID" in pop up menu
  - Add this ID to the file CoreServer/config/settings.py under the DISCORD_GUILDS variable, eg: ```DISCORD_GUILDS = [123123123123123123]```

- Run debug server
  - ```python CoreServer/manage.py runserver```


You should see a few lines of text appear in your console including 

> Starting development server at http://127.0.0.1:8000/,

 after a few seconds you should see another line appear which resembles 

>Unseen Servant has connected to discord

If so, congratulations, your bot is up and running. You can access the Django admin page at http://127.0.0.1:8000/admin using the credentials you created.
The bot can be commanded inside the linked discord server while your Django server runs. Try creating a test game in the web interface and running ```!game``` or ```!games```
