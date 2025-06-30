# Discord Tickets Bot - Python Migration

This is a Python migration of the popular Discord Tickets bot, using py-cord and modern Python technologies.

## Features

- 🎫 Comprehensive ticket management system
- 🔧 Configurable categories with permissions
- 💬 Slash commands (/new, /close, /claim, /release, /tickets)
- 🖱️ Interactive buttons and modals
- 📊 Feedback and rating system
- 🗄️ Ticket archiving and transcripts
- 🌐 Web dashboard for configuration
- 🌍 Multi-language support (i18n)
- ⚡ Fast SQLAlchemy database with async support
- 🛡️ Advanced permission system

## Technology Stack

- **Discord Library**: py-cord (discord.py fork) with ezcord
- **Database**: SQLAlchemy with async support (SQLite/PostgreSQL)
- **Web Framework**: FastAPI
- **Configuration**: Pydantic Settings
- **Internationalization**: PyYAML-based i18n system
- **Encryption**: Cryptography library for sensitive data

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your bot token and settings
   ```

3. **Run the bot:**
   ```bash
   python src/main.py
   ```

## Configuration

### Environment Variables

- `BOT_TOKEN`: Your Discord bot token
- `DATABASE_URL`: Database connection URL (defaults to SQLite)
- `HTTP_HOST`/`HTTP_PORT`: Web server configuration
- `LOG_LEVEL`: Logging verbosity (DEBUG, INFO, WARNING, ERROR)

### Web Dashboard

Access the configuration dashboard at `http://localhost:8080` to:
- Configure ticket categories
- Set up staff roles and permissions
- Manage working hours
- View statistics

## Commands

### Slash Commands

- `/new [references]` - Create a new support ticket
- `/close [reason]` - Close the current ticket  
- `/claim` - Claim a ticket for exclusive handling
- `/release` - Release a claimed ticket
- `/tickets` - View your tickets
- `/setup` - Initial server setup (admin only)
- `/stats` - View ticket statistics (staff only)

### Admin Commands

- `/setup` - Configure the ticket system
- `/settings` - Get dashboard link
- `/stats` - View server statistics

## Architecture

```
src/
├── main.py                 # Bot entry point
├── config/                 # Configuration management
│   ├── settings.py         # Pydantic settings
│   └── database.py         # SQLAlchemy setup
├── models/                 # Database models
│   ├── ticket.py          # Ticket model
│   ├── category.py        # Category model  
│   ├── guild.py           # Guild model
│   └── user.py            # User model
├── cogs/                  # Discord cogs
│   ├── tickets.py         # Main ticket functionality
│   ├── admin.py           # Admin commands
│   └── events.py          # Event handlers
├── commands/              # Command implementations
│   ├── new.py             # /new command
│   ├── close.py           # /close command
│   └── claim.py           # /claim command
├── views/                 # UI components
│   ├── ticket_buttons.py  # Button interactions
│   ├── category_select.py # Category selection
│   └── ticket_modals.py   # Modal forms
├── utils/                 # Utilities
│   ├── logger.py          # Logging setup
│   ├── permissions.py     # Permission checks
│   ├── crypto.py          # Encryption
│   └── i18n.py            # Internationalization
└── web/                   # Web dashboard
    └── server.py          # FastAPI server
```

## Migration from JavaScript Version

This Python version maintains feature parity with the original JavaScript Discord Tickets bot while providing:

- **Better Performance**: Async/await throughout with SQLAlchemy
- **Type Safety**: Full type hints with Pydantic
- **Modern Stack**: FastAPI, SQLAlchemy 2.0, py-cord
- **Maintainability**: Clean architecture with separation of concerns

## Development

### Database Migrations

The bot automatically creates database tables on startup. For production deployments, consider using Alembic for database migrations.

### Adding Features

1. Create new models in `src/models/`
2. Add commands in `src/commands/`
3. Create UI components in `src/views/`
4. Update i18n files in `src/i18n/`

## License

This project is licensed under the GNU General Public License v3.0 - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For support, please join our Discord server or open an issue on GitHub.