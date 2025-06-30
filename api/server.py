"""FastAPI server for Discord Tickets web dashboard."""

import os
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends, Cookie
from fastapi.security import HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
from pydantic import BaseModel

from config.env import get_settings
from utils.logger import get_bot_logger


class TicketsAPI:
    """Discord Tickets FastAPI server."""
    
    def __init__(self, bot):
        """Initialize the API server."""
        self.bot = bot
        self.settings = get_settings()
        self.log = get_bot_logger().api
        
        # Create FastAPI app
        self.app = FastAPI(
            title="Discord Tickets API",
            description="Discord Tickets Bot Web Dashboard API",
            version="4.1.0",
            docs_url="/docs" if os.getenv("DEBUG") else None,
            redoc_url="/redoc" if os.getenv("DEBUG") else None,
        )
        
        # Setup middleware
        self.setup_middleware()
        
        # Setup routes
        self.setup_routes()
    
    def setup_middleware(self) -> None:
        """Setup FastAPI middleware."""
        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"] if os.getenv("DEBUG") else [self.settings.http_external],
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE"],
            allow_headers=["*"],
        )
    
    def setup_routes(self) -> None:
        """Setup API routes."""
        
        @self.app.get("/")
        async def root():
            """Root endpoint."""
            return {
                "name": "Discord Tickets API",
                "version": "4.1.0",
                "status": "running"
            }
        
        @self.app.get("/health")
        async def health():
            """Health check endpoint."""
            return {
                "status": "healthy",
                "bot_connected": self.bot.is_ready() if self.bot else False,
                "guilds": len(self.bot.guilds) if self.bot and self.bot.is_ready() else 0
            }
        
        @self.app.get("/api/user")
        async def get_user_info(token: Optional[str] = Cookie(None)):
            """Get current user information."""
            if not token:
                raise HTTPException(status_code=401, detail="Not authenticated")
            
            # TODO: Implement JWT token verification and user fetching
            return {"message": "User endpoint - not implemented yet"}
        
        @self.app.get("/api/guilds")
        async def get_user_guilds(token: Optional[str] = Cookie(None)):
            """Get user's guilds."""
            if not token:
                raise HTTPException(status_code=401, detail="Not authenticated")
            
            # TODO: Implement guild fetching for authenticated user
            return {"message": "Guilds endpoint - not implemented yet"}
        
        @self.app.get("/api/guilds/{guild_id}/tickets")
        async def get_guild_tickets(guild_id: str, token: Optional[str] = Cookie(None)):
            """Get tickets for a guild."""
            if not token:
                raise HTTPException(status_code=401, detail="Not authenticated")
            
            # TODO: Implement ticket fetching for guild
            return {"message": f"Tickets for guild {guild_id} - not implemented yet"}
        
        @self.app.get("/api/guilds/{guild_id}/categories")
        async def get_guild_categories(guild_id: str, token: Optional[str] = Cookie(None)):
            """Get ticket categories for a guild."""
            if not token:
                raise HTTPException(status_code=401, detail="Not authenticated")
            
            # TODO: Implement category fetching for guild
            return {"message": f"Categories for guild {guild_id} - not implemented yet"}
    
    async def start(self) -> None:
        """Start the API server."""
        self.log.info(f"Starting API server on {self.settings.http_host}:{self.settings.http_port}")
        
        config = uvicorn.Config(
            self.app,
            host=self.settings.http_host,
            port=self.settings.http_port,
            log_level="info",
            access_log=True,
        )
        
        server = uvicorn.Server(config)
        await server.serve()


# Request/Response models
class UserResponse(BaseModel):
    """User information response model."""
    id: str
    username: str
    display_name: str
    avatar: Optional[str] = None


class GuildResponse(BaseModel):
    """Guild information response model."""
    id: str
    name: str
    icon: Optional[str] = None
    permissions: int


class TicketResponse(BaseModel):
    """Ticket information response model."""
    id: str
    number: int
    category: str
    created_by: str
    created_at: str
    open: bool
    topic: Optional[str] = None