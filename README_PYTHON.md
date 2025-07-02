# Discord Tickets Bot - Python Version

This repository now contains both the original JavaScript version and a new Python implementation of the Discord Tickets Bot.

## 🐍 Python Version (NEW!)

The Python version is a complete rewrite using modern Python frameworks:

- **Discord Library**: py-cord (pycord) + ezcord
- **Database**: SQLAlchemy with async support  
- **API Server**: FastAPI
- **Configuration**: Pydantic settings
- **Logging**: Structured logging with Rich

### Quick Start (Python)

1. **Requirements**: Python 3.9+ required

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configuration**:
   ```bash
   cp .env.example .env
   # Edit .env with your bot token and settings
   ```

4. **Run the Bot**:
   ```bash
   python main.py
   ```

### Python Project Structure

```
├── main.py                 # Main entry point
├── requirements.txt        # Python dependencies
├── pyproject.toml         # Project configuration
├── config/
│   ├── env.py             # Environment variables
│   └── settings.py        # Bot configuration
├── bot/
│   ├── client.py          # Main bot client
│   ├── commands/          # Slash commands
│   ├── interactions/      # Buttons, menus, modals
│   ├── tickets/           # Ticket management
│   └── events/            # Event handlers
├── api/
│   ├── server.py          # FastAPI server
│   └── routes/            # API routes
├── database/
│   ├── models.py          # SQLAlchemy models
│   └── migrations/        # Database migrations
├── utils/
│   ├── logger.py          # Logging system
│   ├── embed.py           # Discord embeds
│   ├── users.py           # User utilities
│   └── i18n.py            # Internationalization
└── locales/               # Translation files
```

### Features Implemented

✅ **Core Functionality**:
- Bot client with py-cord and ezcord
- SQLAlchemy database models (converted from Prisma)
- Structured logging with Rich console output
- Environment configuration with Pydantic
- Basic FastAPI server for web dashboard

✅ **Commands**:
- `/tickets` - List user's tickets
- `/new` - Create a new ticket with category selection
- `/close` - Close a ticket with reason

✅ **Interactions**:
- Ticket claim/close buttons
- Category selection menus
- Proper permission checking

✅ **Ticket Management**:
- Create tickets with categories
- Claim/unclaim tickets
- Close tickets with archiving support
- Permission-based access control

### Still To Do

- [ ] Complete ticket archiving system
- [ ] Full web dashboard API
- [ ] All interaction handlers (edit, transfer, etc.)
- [ ] Question/answer system for tickets
- [ ] Complete i18n integration
- [ ] Statistics and reporting
- [ ] Advanced features (auto-close, etc.)

## 📝 JavaScript Version (Original)

The original JavaScript version continues to work as before. See the main README sections below for JavaScript setup instructions.

---

# Discord Tickets

[![Discord](https://img.shields.io/discord/451745464480432129?style=flat-square&logo=discord&logoColor=white&color=5865F2)](https://go.eartharoid.me/discord)
[![Version](https://img.shields.io/github/package-json/v/discord-tickets/bot?style=flat-square&logo=azurepipelines&logoColor=white&color=blue)](https://github.com/discord-tickets/bot/)
[![Downloads](https://img.shields.io/github/downloads/discord-tickets/bot/total?style=flat-square&logo=github&logoColor=white&color=success)](https://github.com/discord-tickets/bot/releases/)

Discord Tickets is a Discord bot for creating and managing support tickets. 

**[Go to the docs](https://discordtickets.app)**

## Features

Discord Tickets is feature-rich and much more advanced than many of the other ticket bots available.
You can also upgrade to [**Discord Tickets Pro**](https://lnk.earth/dtp) for additional features and priority support.

For a full list of features, see the [**documentation**](https://discordtickets.app).

## Support & Documentation

Before asking for help in the support server, please check the [**documentation**](https://discordtickets.app) to see if your question is answered there.

If you need help, you can ask in the support server at [**lnk.earth/discord**](https://lnk.earth/discord) where you can receive community support.

If you are a [**Discord Tickets Pro**](https://lnk.earth/dtp) customer, you can receive faster and better support by creating a ticket on the [**helpdesk**](https://lnk.earth/dtp-support).

## Installation & setup

### Quick start

**You must have [Node.js v18](https://nodejs.org/) or later installed.**

1. Download the bot
2. Extract or unzip the archive and move the files to a new directory
3. Open a terminal or command prompt and navigate to the directory
4. Install the dependencies: `npm install`
5. Rename `.env.example` to `.env` and add your bot token and other options
6. Use `npx prisma db push` to create the database
7. (Optional) Add a process manager like PM2 (`npm i -g pm2`)
8. Start the bot: `npm start` (or `pm2 start --name tickets .`)

For detailed setup instructions, see the [**documentation**](https://discordtickets.app).

### Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/T6vbiD?referralCode=eartharoid)

### Replit (not recommended)

[![Run on Repl.it](https://repl.it/badge/github/discord-tickets/bot)](https://repl.it/github/discord-tickets/bot)

Please read the [**documentation**](https://discordtickets.app/installation/#replitcom) before deploying to Replit.

## License & Contributing

Discord Tickets is licensed under the [**GNU General Public License v3.0**](https://github.com/discord-tickets/bot/blob/main/LICENSE). 

Contributions are welcome! Please read the [**contributing guidelines**](https://github.com/discord-tickets/bot/.github/CONTRIBUTING.md) before submitting a pull request.

## Sponsors

Thanks to our sponsors!

[![Sponsors](https://sponsors.eartharoid.me/discord-tickets.svg)](https://github.com/sponsors/eartharoid)