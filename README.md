# UnseenServant

A D&D game organisation tool for discord

## Development install

- Clone repository

  - `git clone https://github.com/OperationXen/UnseenServant.git`

- Create and activate python virtual environment (optional)

  - `python -m pip install virtualenv`
  - `python -m virtualenv venv`
  - `./venv/script/activate`

- Install dependencies

  - Ensure C++ build tools are installed: https://visualstudio.microsoft.com/visual-cpp-build-tools
  - `python -m pip install -r requirements.txt`

- Create sqllite database

  - `mkdir database`
  - `python manage.py makemigrations`
  - `python manage.py migrate`

- Create Web interface user (optional)

  - `python manage.py createsuperuser`

- Create Discord application

  - Go to `https://discord.com/developers/applications`
  - Click `New Application`
  - Give the application a name and agree to the terms

- Create discord token

  - Open the bot tab in the application
  - Toggle `Server members intent` under `Privileged Gateway Intents`
  - Uncheck `Public Bot` (if applicable)
  - Click `Reset Token` and copy the bots token
  - Add this to your environment variables as `DISCORD_TOKEN`

- Add testing guild identity to config

  - Right click in Discord app on the server you're using for testing, click "Copy ID" in pop up menu
  - Add this to your environment variables as `DISCORD_GUILDS`

- Add bot to server

  - Click OAuth2 on the application
  - On the OAuth2 URL generator click "bot"
  - Select the following bot permissions
    - Manage roles
    - Manage channels
    - Send messages
    - Read message
    - Manage messages
    - Manage threads
    - Read message history
  - Visit the link to install the bot in to your selected server

- Run API/Admin server in debug mode

  - `python manage.py runserver`

- Start the discord bot

  - `python manage.py startbot`

  - You should see text to the effect of `bot has connected to discord`

If so, congratulations, your bot is up and running. You can access the Django admin page at http://127.0.0.1:8000/admin using the credentials you created.
The bot can be commanded inside the linked discord server while your Django server runs. Try creating a test game in the web interface and running `/games`
