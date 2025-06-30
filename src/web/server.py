"""
FastAPI web server for the tickets dashboard.
"""

import logging
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.guild import Guild
from models.category import Category
from models.ticket import Ticket

logger = logging.getLogger(__name__)


def create_app(database, settings):
    """Create FastAPI application."""
    
    app = FastAPI(
        title="Discord Tickets Dashboard",
        description="Web dashboard for managing Discord Tickets",
        version="4.0.41-python"
    )
    
    # Store database and settings in app state
    app.state.database = database
    app.state.settings = settings
    
    # Dependency for database session
    async def get_db() -> AsyncSession:
        async with database.get_session() as session:
            yield session
    
    @app.get("/", response_class=HTMLResponse)
    async def root():
        """Root endpoint."""
        return """
        <html>
            <head>
                <title>Discord Tickets Dashboard</title>
                <style>
                    body { font-family: Arial, sans-serif; padding: 40px; }
                    .container { max-width: 800px; margin: 0 auto; }
                    .header { text-align: center; margin-bottom: 40px; }
                    .card { background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎫 Discord Tickets Dashboard</h1>
                        <p>Manage your Discord ticket system</p>
                    </div>
                    
                    <div class="card">
                        <h2>🚀 Welcome</h2>
                        <p>This is the web dashboard for Discord Tickets bot. Here you can configure your ticket categories, manage settings, and view statistics.</p>
                    </div>
                    
                    <div class="card">
                        <h2>📋 Features</h2>
                        <ul>
                            <li>Configure ticket categories</li>
                            <li>Manage staff roles and permissions</li>
                            <li>Set up working hours</li>
                            <li>View ticket statistics</li>
                            <li>Export ticket transcripts</li>
                        </ul>
                    </div>
                    
                    <div class="card">
                        <h2>🔗 Quick Links</h2>
                        <ul>
                            <li><a href="/status">Server Status</a></li>
                            <li><a href="/docs">API Documentation</a></li>
                        </ul>
                    </div>
                </div>
            </body>
        </html>
        """
    
    @app.get("/status")
    async def status():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "service": "discord-tickets",
            "version": settings.version
        }
    
    @app.get("/settings/{guild_id}")
    async def guild_settings(guild_id: str, db: AsyncSession = Depends(get_db)):
        """Get guild settings (placeholder)."""
        # Get guild from database
        result = await db.execute(
            select(Guild).where(Guild.id == guild_id)
        )
        guild = result.scalar_one_or_none()
        
        if not guild:
            raise HTTPException(status_code=404, detail="Guild not found")
        
        # For now, return basic info
        return {
            "guild_id": guild.id,
            "locale": guild.locale,
            "primary_colour": guild.primary_colour,
            "message": "Full settings interface coming soon!"
        }
    
    @app.get("/api/guilds/{guild_id}/stats")
    async def guild_stats(guild_id: str, db: AsyncSession = Depends(get_db)):
        """Get guild ticket statistics."""
        # Check if guild exists
        guild_result = await db.execute(
            select(Guild).where(Guild.id == guild_id)
        )
        guild = guild_result.scalar_one_or_none()
        
        if not guild:
            raise HTTPException(status_code=404, detail="Guild not found")
        
        # Get ticket counts
        from sqlalchemy import func
        
        total_result = await db.execute(
            select(func.count(Ticket.id)).where(Ticket.guild_id == guild_id)
        )
        total_tickets = total_result.scalar()
        
        open_result = await db.execute(
            select(func.count(Ticket.id)).where(
                Ticket.guild_id == guild_id,
                Ticket.open == True
            )
        )
        open_tickets = open_result.scalar()
        
        # Get category count
        category_result = await db.execute(
            select(func.count(Category.id)).where(Category.guild_id == guild_id)
        )
        categories = category_result.scalar()
        
        return {
            "guild_id": guild_id,
            "total_tickets": total_tickets,
            "open_tickets": open_tickets,
            "closed_tickets": total_tickets - open_tickets,
            "categories": categories
        }
    
    return app


async def start_web_server(app, settings):
    """Start the web server."""
    import uvicorn
    
    config = uvicorn.Config(
        app,
        host=settings.http_host,
        port=settings.http_port,
        log_level="info"
    )
    
    server = uvicorn.Server(config)
    logger.info(f"Starting web server on {settings.http_host}:{settings.http_port}")
    await server.serve()