import asyncio
import os
import logging
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn
import json
import time
from datetime import datetime, timedelta
import socketio

logger = logging.getLogger(__name__)

class ChannelRequest(BaseModel):
    guild_id: int
    channel_id: int
    enable: bool

class ModeRequest(BaseModel):
    guild_id: int
    mode: str

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.network_stats = {
            'rx_bytes': 0,
            'tx_bytes': 0,
            'rx_packets': 0,
            'tx_packets': 0,
            'connected_users': 0,
            'last_update': time.time()
        }

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        if self.active_connections:
            disconnected = []
            for connection in self.active_connections:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    disconnected.append(connection)
            
            # Remove disconnected connections
            for conn in disconnected:
                self.disconnect(conn)

    def update_network_stats(self, rx_bytes: int, tx_bytes: int):
        self.network_stats['rx_bytes'] += rx_bytes
        self.network_stats['tx_bytes'] += tx_bytes
        self.network_stats['rx_packets'] += 1
        self.network_stats['tx_packets'] += 1
        self.network_stats['last_update'] = time.time()

class APIServer:
    def __init__(self, bot):
        self.bot = bot
        self.app = FastAPI(title="Discord Bot API", version="1.0.0")
        self.connection_manager = ConnectionManager()
        
        # Skip Socket.IO for now to avoid conflicts
        # self.sio = socketio.AsyncServer(
        #     async_mode='asgi',
        #     cors_allowed_origins=["http://localhost:3000", "http://127.0.0.1:3000"]
        # )
        # self.sio_app = socketio.ASGIApp(self.sio, self.app)
        
        self.setup_routes()
        self.setup_middleware()
    
    def setup_middleware(self):
        """Setup CORS middleware"""
        import os
        dashboard_url = os.getenv('DASHBOARD_URL', 'http://localhost:3000')
        
        allowed_origins = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            dashboard_url
        ]
        
        # Add any vercel preview URLs
        if 'vercel.app' in dashboard_url:
            allowed_origins.append("https://*.vercel.app")
        
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Allow all for WebSocket compatibility
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def setup_routes(self):
        """Setup API routes"""
        
        @self.app.get("/api/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "bot_ready": self.bot.is_ready(),
                "guilds": len(self.bot.guilds),
                "websocket_connections": len(self.connection_manager.active_connections)
            }
        
        @self.app.get("/api/stats")
        async def get_stats(guild_id: Optional[int] = None):
            """Get usage statistics"""
            try:
                stats = await self.bot.database.get_usage_stats(guild_id)
                return {
                    "success": True,
                    "data": stats
                }
            except Exception as e:
                logger.error(f'Error getting stats: {e}')
                raise HTTPException(status_code=500, detail="Failed to get statistics")
        
        @self.app.get("/api/cost/usage")
        async def get_cost_usage():
            """Get current cost and quota usage"""
            try:
                from utils.cost_optimizer import cost_optimizer
                usage_stats = cost_optimizer.get_usage_stats()
                
                return {
                    "success": True,
                    "data": {
                        **usage_stats,
                        "is_warning_threshold": cost_optimizer.is_quota_warning_threshold(),
                        "is_quota_exceeded": cost_optimizer.is_quota_exceeded(),
                        "last_reset": cost_optimizer.api_usage['last_reset'].isoformat()
                    }
                }
            except Exception as e:
                logger.error(f'Error getting cost usage: {e}')
                raise HTTPException(status_code=500, detail="Failed to get cost usage")
        
        @self.app.get("/api/cost/simple-responses")
        async def get_simple_responses():
            """Get available simple response patterns"""
            try:
                from utils.cost_optimizer import cost_optimizer
                return {
                    "success": True,
                    "data": {
                        "patterns": list(cost_optimizer.simple_responses.keys()),
                        "total_patterns": len(cost_optimizer.simple_responses)
                    }
                }
            except Exception as e:
                logger.error(f'Error getting simple responses: {e}')
                raise HTTPException(status_code=500, detail="Failed to get simple responses")
        
        @self.app.get("/api/chat-logs")
        async def get_chat_logs(guild_id: Optional[int] = None, limit: int = 50):
            """Get chat logs"""
            try:
                logs = await self.bot.database.get_chat_logs(guild_id, limit)
                return {
                    "success": True,
                    "data": logs
                }
            except Exception as e:
                logger.error(f'Error getting chat logs: {e}')
                raise HTTPException(status_code=500, detail="Failed to get chat logs")
        
        @self.app.get("/api/users")
        async def get_users():
            """Get all users who have chatted with the bot"""
            try:
                users = await self.bot.database.get_chat_users()
                # Enrich with Discord data
                enriched_users = []
                for user_data in users:
                    user_id = int(user_data['user_id'])
                    discord_user = self.bot.get_user(user_id)
                    
                    enriched_users.append({
                        'user_id': str(user_id),
                        'username': discord_user.display_name if discord_user else user_data.get('username', f'User#{str(user_id)[-4:]}'),
                        'avatar': str(discord_user.avatar.url) if discord_user and discord_user.avatar else None,
                        'message_count': user_data.get('message_count', 0),
                        'total_tokens': user_data.get('total_tokens', 0),
                        'last_message': user_data.get('last_message', None)
                    })
                
                return {
                    "success": True,
                    "data": enriched_users
                }
            except Exception as e:
                logger.error(f'Error getting users: {e}')
                raise HTTPException(status_code=500, detail="Failed to get users")
        
        @self.app.get("/api/users/{user_id}/chat-history")
        async def get_user_chat_history(user_id: int, limit: int = 100):
            """Get chat history for a specific user"""
            try:
                logs = await self.bot.database.get_user_chat_history(user_id, limit)
                
                # Get Discord user info
                discord_user = self.bot.get_user(user_id)
                user_info = {
                    'user_id': str(user_id),
                    'username': discord_user.display_name if discord_user else f'User#{str(user_id)[-4:]}',
                    'avatar': str(discord_user.avatar.url) if discord_user and discord_user.avatar else None
                }
                
                return {
                    "success": True,
                    "data": {
                        "user": user_info,
                        "messages": logs
                    }
                }
            except Exception as e:
                logger.error(f'Error getting user chat history: {e}')
                raise HTTPException(status_code=500, detail="Failed to get user chat history")
        
        @self.app.get("/api/guilds")
        async def get_guilds():
            """Get bot guilds"""
            try:
                guilds = []
                for guild in self.bot.guilds:
                    guilds.append({
                        "id": guild.id,
                        "name": guild.name,
                        "member_count": guild.member_count,
                        "icon": str(guild.icon) if guild.icon else None
                    })
                
                return {
                    "success": True,
                    "data": guilds
                }
            except Exception as e:
                logger.error(f'Error getting guilds: {e}')
                raise HTTPException(status_code=500, detail="Failed to get guilds")
        
        @self.app.get("/api/guilds/{guild_id}/channels")
        async def get_guild_channels(guild_id: int):
            """Get guild channels"""
            try:
                guild = self.bot.get_guild(guild_id)
                if not guild:
                    raise HTTPException(status_code=404, detail="Guild not found")
                
                channels = []
                chat_channels = await self.bot.database.get_chat_channels(guild_id)
                
                for channel in guild.text_channels:
                    channels.append({
                        "id": channel.id,
                        "name": channel.name,
                        "category": channel.category.name if channel.category else None,
                        "ai_enabled": channel.id in chat_channels
                    })
                
                return {
                    "success": True,
                    "data": channels
                }
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f'Error getting guild channels: {e}')
                raise HTTPException(status_code=500, detail="Failed to get channels")
        
        @self.app.post("/api/channels/toggle")
        async def toggle_channel(request: ChannelRequest):
            """Toggle AI auto-response for a channel"""
            try:
                if request.enable:
                    success = await self.bot.database.add_chat_channel(
                        request.guild_id, 
                        request.channel_id
                    )
                else:
                    success = await self.bot.database.remove_chat_channel(
                        request.guild_id, 
                        request.channel_id
                    )
                
                if success:
                    # Broadcast update to connected clients
                    await self.connection_manager.broadcast({
                        "type": "channel_update",
                        "guild_id": request.guild_id,
                        "channel_id": request.channel_id,
                        "enabled": request.enable
                    })
                    
                    return {
                        "success": True,
                        "message": f"Channel {'enabled' if request.enable else 'disabled'} successfully"
                    }
                else:
                    raise HTTPException(status_code=400, detail="Failed to update channel")
                    
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f'Error toggling channel: {e}')
                raise HTTPException(status_code=500, detail="Failed to toggle channel")
        
        @self.app.get("/api/guilds/{guild_id}/mode")
        async def get_ai_mode(guild_id: int):
            """Get AI mode for guild"""
            try:
                mode = await self.bot.database.get_ai_mode(guild_id)
                modes = await self.bot.gemini_client.get_available_modes()
                
                return {
                    "success": True,
                    "data": {
                        "current_mode": mode,
                        "available_modes": modes
                    }
                }
            except Exception as e:
                logger.error(f'Error getting AI mode: {e}')
                raise HTTPException(status_code=500, detail="Failed to get AI mode")
        
        @self.app.post("/api/mode")
        async def set_ai_mode(request: ModeRequest):
            """Set AI mode for guild"""
            try:
                available_modes = await self.bot.gemini_client.get_available_modes()
                if request.mode not in available_modes:
                    raise HTTPException(status_code=400, detail="Invalid AI mode")
                
                success = await self.bot.database.set_ai_mode(request.guild_id, request.mode)
                
                if success:
                    # Broadcast update to connected clients
                    await self.connection_manager.broadcast({
                        "type": "mode_update",
                        "guild_id": request.guild_id,
                        "mode": request.mode
                    })
                    
                    return {
                        "success": True,
                        "message": f"AI mode set to {request.mode}"
                    }
                else:
                    raise HTTPException(status_code=400, detail="Failed to set AI mode")
                    
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f'Error setting AI mode: {e}')
                raise HTTPException(status_code=500, detail="Failed to set AI mode")
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for real-time updates"""
            await self.connection_manager.connect(websocket)
            try:
                while True:
                    # Send periodic network stats
                    network_data = {
                        "type": "network_stats",
                        "data": {
                            "timestamp": datetime.now().isoformat(),
                            "rx_bytes": self.connection_manager.network_stats['rx_bytes'],
                            "tx_bytes": self.connection_manager.network_stats['tx_bytes'],
                            "rx_packets": self.connection_manager.network_stats['rx_packets'],
                            "tx_packets": self.connection_manager.network_stats['tx_packets'],
                            "latency": 20 + (time.time() % 30),  # Mock latency
                            "connected_users": len(self.bot.guilds) * 5  # Mock connected users
                        }
                    }
                    await websocket.send_text(json.dumps(network_data))
                    await asyncio.sleep(1)  # Send updates every second
                    
            except WebSocketDisconnect:
                self.connection_manager.disconnect(websocket)
        
        @self.app.get("/api/network/stream")
        async def network_stream():
            """Server-Sent Events endpoint for network monitoring"""
            async def generate():
                while True:
                    data = {
                        "timestamp": datetime.now().isoformat(),
                        "rx_bytes": self.connection_manager.network_stats['rx_bytes'],
                        "tx_bytes": self.connection_manager.network_stats['tx_bytes'],
                        "latency": 20 + (time.time() % 30),
                        "connected_users": len(self.bot.guilds) * 5
                    }
                    yield f"data: {json.dumps(data)}\n\n"
                    await asyncio.sleep(1)
            
            return StreamingResponse(
                generate(),
                media_type="text/plain",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "*"
                }
            )
    
    async def broadcast_message_event(self, message_data: dict):
        """Broadcast new message event to connected clients"""
        await self.connection_manager.broadcast({
            "type": "new_message",
            "data": message_data
        })
        
        # Update network stats
        message_size = len(json.dumps(message_data))
        self.connection_manager.update_network_stats(message_size, message_size)
    
    async def start(self):
        """Start the API server"""
        try:
            host = os.getenv('API_HOST', '0.0.0.0')
            port = int(os.getenv('API_PORT', 8000))
            
            logger.info(f"Starting API server on {host}:{port}")
            
            # Create server config
            config = uvicorn.Config(
                self.app,  # Use FastAPI app directly for now
                host=host,
                port=port,
                log_level="info"
            )
            server = uvicorn.Server(config)
            
            # Start server
            await server.serve()
            
        except Exception as e:
            logger.error(f'Error starting API server: {e}')
        
        @self.app.get("/api/guilds/{guild_id}/ai-channels")
        async def get_ai_channels(guild_id: int):
            """Get AI channels (public and private) for guild"""
            try:
                guild = self.bot.get_guild(guild_id)
                if not guild:
                    raise HTTPException(status_code=404, detail="Guild not found")
                
                public_channels = await self.bot.database.get_public_channels(guild_id)
                private_channels = await self.bot.database.get_private_channels(guild_id)
                
                # Enrich with Discord data
                public_data = []
                for channel_data in public_channels:
                    channel = guild.get_channel(channel_data['channel_id'])
                    creator = guild.get_member(channel_data['creator_id'])
                    
                    public_data.append({
                        **channel_data,
                        'name': channel.name if channel else 'deleted-channel',
                        'exists': channel is not None,
                        'creator_name': creator.display_name if creator else 'Unknown User',
                        'creator_avatar': str(creator.avatar) if creator and creator.avatar else None
                    })
                
                private_data = []
                for channel_data in private_channels:
                    channel = guild.get_channel(channel_data['channel_id'])
                    owner = guild.get_member(channel_data['owner_id'])
                    
                    private_data.append({
                        **channel_data,
                        'name': channel.name if channel else 'deleted-channel',
                        'exists': channel is not None,
                        'owner_name': owner.display_name if owner else 'Unknown User',
                        'owner_avatar': str(owner.avatar) if owner and owner.avatar else None
                    })
                
                return {
                    "success": True,
                    "data": {
                        "public_channels": public_data,
                        "private_channels": private_data
                    }
                }
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f'Error getting AI channels: {e}')
                raise HTTPException(status_code=500, detail="Failed to get AI channels")
        
        @self.app.delete("/api/channels/{channel_id}")
        async def delete_channel(channel_id: int, guild_id: int):
            """Delete AI channel"""
            try:
                guild = self.bot.get_guild(guild_id)
                if not guild:
                    raise HTTPException(status_code=404, detail="Guild not found")
                
                channel = guild.get_channel(channel_id)
                if not channel:
                    raise HTTPException(status_code=404, detail="Channel not found")
                
                # Remove from database
                await self.bot.database.remove_chat_channel(guild_id, channel_id)
                await self.bot.database.remove_public_channel(guild_id, channel_id)
                await self.bot.database.remove_private_channel(guild_id, channel_id)
                
                # Delete Discord channel
                await channel.delete(reason="AI channel deleted via dashboard")
                
                # Broadcast update
                await self.connection_manager.broadcast({
                    "type": "channel_deleted",
                    "guild_id": guild_id,
                    "channel_id": channel_id
                })
                
                return {
                    "success": True,
                    "message": "Channel deleted successfully"
                }
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f'Error deleting channel: {e}')
                raise HTTPException(status_code=500, detail="Failed to delete channel")
        
        @self.app.get("/api/guilds/{guild_id}/channel-activity")
        async def get_channel_activity(guild_id: int):
            """Get channel activity for heatmap"""
            try:
                activity_data = await self.bot.database.get_channel_activity(guild_id)
                
                guild = self.bot.get_guild(guild_id)
                if guild:
                    # Enrich with channel names
                    for activity in activity_data:
                        channel = guild.get_channel(activity['channel_id'])
                        activity['channel_name'] = channel.name if channel else 'deleted-channel'
                        activity['exists'] = channel is not None
                
                return {
                    "success": True,
                    "data": activity_data
                }
            except Exception as e:
                logger.error(f'Error getting channel activity: {e}')
                raise HTTPException(status_code=500, detail="Failed to get channel activity")
        
        @self.app.get("/api/guilds/{guild_id}/music/status")
        async def get_music_status(guild_id: int):
            """Get current music status"""
            try:
                guild = self.bot.get_guild(guild_id)
                if not guild:
                    raise HTTPException(status_code=404, detail="Guild not found")
                
                vc = guild.voice_client
                if not vc:
                    return {
                        "success": True,
                        "data": {
                            "playing": False,
                            "connected": False
                        }
                    }
                
                # Get music cog and queue
                music_cog = self.bot.get_cog('MusicPlayer')
                queue = music_cog.get_queue(guild_id) if music_cog else None
                
                current_track = None
                if vc.playing and queue and queue.current:
                    current_track = {
                        "title": queue.current.title,
                        "author": getattr(queue.current, 'author', 'Unknown'),
                        "length": queue.current.length,
                        "position": vc.position,
                        "artwork": getattr(queue.current, 'artwork', None),
                        "uri": queue.current.uri
                    }
                
                queue_tracks = []
                if queue and queue.queue:
                    for track in queue.queue[:10]:  # Limit to 10 tracks
                        queue_tracks.append({
                            "title": track.title,
                            "author": getattr(track, 'author', 'Unknown'),
                            "length": track.length,
                            "artwork": getattr(track, 'artwork', None)
                        })
                
                return {
                    "success": True,
                    "data": {
                        "playing": vc.playing,
                        "connected": True,
                        "paused": vc.paused,
                        "volume": vc.volume,
                        "current_track": current_track,
                        "queue": queue_tracks,
                        "loop_mode": queue.loop_mode if queue else "off"
                    }
                }
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f'Error getting music status: {e}')
                raise HTTPException(status_code=500, detail="Failed to get music status")
        
        @self.app.post("/api/guilds/{guild_id}/music/control")
        async def control_music(guild_id: int, action: str):
            """Control music playback"""
            try:
                guild = self.bot.get_guild(guild_id)
                if not guild:
                    raise HTTPException(status_code=404, detail="Guild not found")
                
                vc = guild.voice_client
                if not vc:
                    raise HTTPException(status_code=400, detail="Not connected to voice channel")
                
                music_cog = self.bot.get_cog('MusicPlayer')
                if not music_cog:
                    raise HTTPException(status_code=500, detail="Music cog not loaded")
                
                if action == "pause":
                    await vc.pause(True)
                elif action == "resume":
                    await vc.pause(False)
                elif action == "skip":
                    await vc.stop()
                elif action == "stop":
                    queue = music_cog.get_queue(guild_id)
                    queue.clear()
                    await vc.disconnect()
                else:
                    raise HTTPException(status_code=400, detail="Invalid action")
                
                # Broadcast control event
                await self.connection_manager.broadcast({
                    "type": "music_control",
                    "guild_id": guild_id,
                    "action": action
                })
                
                return {
                    "success": True,
                    "message": f"Music {action} successful"
                }
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f'Error controlling music: {e}')
                raise HTTPException(status_code=500, detail="Failed to control music")
    
    async def broadcast_music_event(self, event_data: dict):
        """Broadcast music event to connected clients"""
        await self.connection_manager.broadcast({
            "type": "music_event",
            "data": event_data
        })
        
        @self.app.post("/api/guilds/{guild_id}/music/playback-mode")
        async def set_playback_mode(guild_id: int, mode: str):
            """Set playback mode (discord/web)"""
            try:
                # Store playback mode preference
                # This could be stored in database for persistence
                await self.connection_manager.broadcast({
                    "type": "playback_mode_changed",
                    "guild_id": guild_id,
                    "mode": mode
                })
                
                return {
                    "success": True,
                    "message": f"Playback mode set to {mode}"
                }
                
            except Exception as e:
                logger.error(f'Error setting playback mode: {e}')
                raise HTTPException(status_code=500, detail="Failed to set playback mode")
        
        @self.app.get("/api/stream/{track_uri}")
        async def get_stream_url(track_uri: str):
            """Get high-quality stream URL for web playback"""
            try:
                import yt_dlp
                import urllib.parse
                
                # Decode URI
                decoded_uri = urllib.parse.unquote(track_uri)
                
                ydl_opts = {
                    'format': 'bestaudio[ext=m4a]/bestaudio/best',
                    'noplaylist': True,
                    'quiet': True,
                    'no_warnings': True,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(decoded_uri, download=False)
                    
                    if info and 'url' in info:
                        return {
                            "success": True,
                            "data": {
                                "stream_url": info['url'],
                                "format": info.get('ext', 'unknown'),
                                "quality": info.get('abr', 'unknown'),
                                "duration": info.get('duration', 0)
                            }
                        }
                
                raise HTTPException(status_code=404, detail="Stream URL not found")
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f'Error getting stream URL: {e}')
                raise HTTPException(status_code=500, detail="Failed to get stream URL")
        
        @self.app.get("/api/ai/eq-settings/{genre}")
        async def get_ai_eq_settings(genre: str):
            """Get AI-recommended EQ settings for genre"""
            try:
                # Use Gemini to get optimal EQ settings
                music_cog = self.bot.get_cog('MusicPlayer')
                if not music_cog:
                    raise HTTPException(status_code=500, detail="Music cog not available")
                
                prompt = f"""
                音楽ジャンル: "{genre}"
                
                このジャンルに最適なイコライザー設定を提案してください。
                以下の周波数帯域での調整値を-12dB〜+12dBの範囲で指定してください:
                
                - bass (低音域: 60-250Hz)
                - mid (中音域: 500-2kHz) 
                - treble (高音域: 4-16kHz)
                - presence (超高音域: 8-20kHz)
                
                JSON形式で出力してください:
                {{"bass": 0, "mid": 0, "treble": 0, "presence": 0}}
                """
                
                response = await self.bot.gemini_client.generate_response(
                    prompt,
                    mode='music_dj'
                )
                
                if response:
                    import json
                    try:
                        eq_settings = json.loads(response.strip())
                        return {
                            "success": True,
                            "data": eq_settings
                        }
                    except json.JSONDecodeError:
                        # Fallback to default settings
                        pass
                
                # Default EQ settings by genre
                default_settings = {
                    'rock': {'bass': 2, 'mid': 1, 'treble': 3, 'presence': 2},
                    'jazz': {'bass': -1, 'mid': 2, 'treble': 1, 'presence': 3},
                    'classical': {'bass': 0, 'mid': 0, 'treble': 2, 'presence': 4},
                    'electronic': {'bass': 4, 'mid': -1, 'treble': 2, 'presence': 1},
                    'pop': {'bass': 1, 'mid': 2, 'treble': 2, 'presence': 1},
                    'hip-hop': {'bass': 5, 'mid': 1, 'treble': 0, 'presence': -1}
                }
                
                genre_lower = genre.lower()
                for key, settings in default_settings.items():
                    if key in genre_lower:
                        return {
                            "success": True,
                            "data": settings
                        }
                
                # Default neutral settings
                return {
                    "success": True,
                    "data": {'bass': 0, 'mid': 0, 'treble': 0, 'presence': 0}
                }
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f'Error getting AI EQ settings: {e}')
                raise HTTPException(status_code=500, detail="Failed to get EQ settings")
        
        @self.app.get("/api/guilds/{guild_id}/analytics")
        async def get_guild_analytics(guild_id: int, period: str = "week"):
            """サーバーの分析データを取得"""
            try:
                data = await self.bot.database.get_analytics_data(guild_id, period)
                summary = await self.bot.database.get_guild_summary(guild_id)
                
                return {
                    "success": True,
                    "data": {
                        "period": period,
                        "stats": data,
                        "summary": summary
                    }
                }
            except Exception as e:
                logger.error(f'Error getting analytics: {e}')
                raise HTTPException(status_code=500, detail="Failed to get analytics")