"""リアルタイム歌詞配信システム"""
import discord
from discord.ext import commands, tasks
from discord import app_commands
import wavelink
import aiohttp
import re
import logging
from typing import Optional, List, Dict, Tuple
import asyncio
import os

logger = logging.getLogger(__name__)

# 歌詞API
LRCLIB_API = "https://lrclib.net/api/get"
GENIUS_API = "https://api.genius.com"

OFFSET = 0.5  # 0.5秒早めに送信


class LyricsLine:
    """歌詞の1行を表すクラス"""
    def __init__(self, timestamp: float, text: str):
        self.timestamp = timestamp  # 秒数
        self.text = text
        self.sent = False


class LyricsStreamer(commands.Cog):
    """歌詞のリアルタイム配信を管理"""
    
    def __init__(self, bot):
        self.bot = bot
        self.lyrics_enabled: Dict[int, bool] = {}  # guild_id -> enabled
        self.lyrics_channels: Dict[int, int] = {}  # guild_id -> channel_id
        self.lyrics_webhooks: Dict[int, discord.Webhook] = {}  # guild_id -> webhook
        self.current_lyrics: Dict[int, List[LyricsLine]] = {}  # guild_id -> lyrics
        self.current_track_info: Dict[int, Dict] = {}  # guild_id -> track info
        self.lyrics_index: Dict[int, int] = {}  # guild_id -> current index
        
        # レコード数管理
        self.update_counter = 0
        self.cleanup_interval = 100  # 100回の更新ごとにクリーンアップ
    
    async def cog_load(self):
        """Cog読み込み時に歌詞配信ループを開始"""
        if not self.lyrics_stream_loop.is_running():
            self.lyrics_stream_loop.start()
        logger.info("✅ Lyrics streamer loaded")
    
    async def cog_unload(self):
        """Cog削除時にループを停止"""
        if self.lyrics_stream_loop.is_running():
            self.lyrics_stream_loop.cancel()
        logger.info("✅ Lyrics streamer unloaded")
    
    @tasks.loop(seconds=0.1)
    async def lyrics_stream_loop(self):
        """0.1秒ごとに歌詞を送信"""
        try:
            for guild_id, enabled in list(self.lyrics_enabled.items()):
                if not enabled:
                    continue
                
                # ギルドのVCを取得
                guild = self.bot.get_guild(guild_id)
                if not guild or not guild.voice_client:
                    continue
                
                vc = guild.voice_client
                if not vc.playing or vc.paused:
                    continue
                
                # 現在の再生位置を取得（ミリ秒→秒）
                position = vc.position / 1000.0
                
                # 歌詞があるか確認
                if guild_id not in self.current_lyrics:
                    continue
                
                lyrics = self.current_lyrics[guild_id]
                current_index = self.lyrics_index.get(guild_id, 0)
                
                # 次の歌詞行を探す
                while current_index < len(lyrics):
                    line = lyrics[current_index]
                    
                    # OFFSETを適用して少し早めに送信
                    if position >= (line.timestamp - OFFSET) and not line.sent:
                        await self._send_lyrics_line(guild_id, line)
                        line.sent = True
                        self.lyrics_index[guild_id] = current_index + 1
                        break
                    elif position < (line.timestamp - OFFSET):
                        # まだ時間じゃない
                        break
                    
                    current_index += 1
                
        except Exception as e:
            logger.error(f"❌ Lyrics stream loop error: {e}")
    
    @lyrics_stream_loop.before_loop
    async def before_lyrics_stream(self):
        """ループ開始前にBotの準備を待つ"""
        await self.bot.wait_until_ready()
    
    async def _send_lyrics_line(self, guild_id: int, line: LyricsLine):
        """Webhookで歌詞を送信"""
        try:
            webhook = self.lyrics_webhooks.get(guild_id)
            if not webhook:
                return
            
            track_info = self.current_track_info.get(guild_id, {})
            
            # Webhookで送信（曲名とジャケット画像を使用）
            await webhook.send(
                content=line.text,
                username=track_info.get('title', 'Music Bot')[:80],  # 80文字制限
                avatar_url=track_info.get('artwork'),
                wait=False
            )
            
            logger.debug(f"🎤 Sent lyrics: {line.text[:30]}...")
            
            # Supabaseに記録（レコード数管理付き）
            await self._log_lyrics_to_supabase(guild_id, line.text, line.timestamp)
            
        except Exception as e:
            logger.error(f"❌ Failed to send lyrics line: {e}")
    
    async def _log_lyrics_to_supabase(self, guild_id: int, text: str, timestamp: float):
        """歌詞をSupabaseに記録（レコード数管理付き）"""
        try:
            if not self.bot.supabase_client or not self.bot.supabase_client.client:
                return
            
            # 歌詞ログを保存
            data = {
                'guild_id': str(guild_id),
                'lyrics_text': text,
                'timestamp_sec': float(timestamp),
                'track_title': self.current_track_info.get(guild_id, {}).get('title', 'Unknown')
            }
            
            self.bot.supabase_client.client.table('lyrics_logs').insert(data).execute()
            
            # カウンターを増やす
            self.update_counter += 1
            
            # 一定回数ごとにクリーンアップ
            if self.update_counter >= self.cleanup_interval:
                await self._cleanup_old_records()
                self.update_counter = 0
            
        except Exception as e:
            # テーブルが存在しない場合は警告のみ（エラーを無視）
            if 'does not exist' in str(e) or 'PGRST204' in str(e):
                logger.warning(f"⚠️ lyrics_logs table does not exist. Please run add_lyrics_table.sql in Supabase.")
            else:
                logger.error(f"❌ Failed to log lyrics to Supabase: {e}")
    
    async def _cleanup_old_records(self):
        """古いレコードを削除して10万件以下に保つ"""
        try:
            if not self.bot.supabase_client or not self.bot.supabase_client.client:
                return
            
            # レコード数を取得
            count_result = self.bot.supabase_client.client.table('lyrics_logs')\
                .select('id', count='exact')\
                .execute()
            
            total_count = count_result.count if hasattr(count_result, 'count') else len(count_result.data)
            
            if total_count > 100000:
                # 削除する件数
                delete_count = total_count - 100000
                
                logger.info(f"🗑️ Cleaning up {delete_count} old lyrics records...")
                
                # 古い順にIDを取得
                old_records = self.bot.supabase_client.client.table('lyrics_logs')\
                    .select('id')\
                    .order('created_at', desc=False)\
                    .limit(delete_count)\
                    .execute()
                
                if old_records.data:
                    # IDのリストを作成
                    ids_to_delete = [record['id'] for record in old_records.data]
                    
                    # バッチ削除（1000件ずつ）
                    batch_size = 1000
                    for i in range(0, len(ids_to_delete), batch_size):
                        batch = ids_to_delete[i:i + batch_size]
                        self.bot.supabase_client.client.table('lyrics_logs')\
                            .delete()\
                            .in_('id', batch)\
                            .execute()
                    
                    logger.info(f"✅ Deleted {len(ids_to_delete)} old lyrics records")
            
        except Exception as e:
            # テーブルが存在しない場合は警告のみ
            if 'does not exist' in str(e) or 'PGRST204' in str(e):
                logger.warning(f"⚠️ lyrics_logs table does not exist. Skipping cleanup.")
            else:
                logger.error(f"❌ Failed to cleanup old records: {e}")
                import traceback
                traceback.print_exc()
    
    async def fetch_lyrics(self, track_title: str, artist: str, duration: int) -> Optional[List[LyricsLine]]:
        """複数のAPIから歌詞を取得（LRCLIB → Genius フォールバック）"""
        
        # 1. LRCLIB API（最優先、タイムスタンプ付き）
        lyrics = await self._fetch_from_lrclib(track_title, artist, duration)
        if lyrics:
            logger.info(f"✅ Lyrics found on LRCLIB: {len(lyrics)} lines")
            return lyrics
        
        # 2. Genius API（フォールバック、タイムスタンプ推定）
        lyrics = await self._fetch_from_genius(track_title, artist, duration)
        if lyrics:
            logger.info(f"✅ Lyrics found on Genius: {len(lyrics)} lines (estimated timestamps)")
            return lyrics
        
        logger.warning(f"❌ No lyrics found for: {track_title} by {artist}")
        return None
    
    async def _fetch_from_lrclib(self, track_title: str, artist: str, duration: int) -> Optional[List[LyricsLine]]:
        """LRCLIB APIから歌詞を取得"""
        try:
            params = {
                'track_name': track_title,
                'artist_name': artist,
                'duration': duration // 1000  # ミリ秒→秒
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(LRCLIB_API, params=params, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status != 200:
                        logger.debug(f"LRCLIB returned {response.status}")
                        return None
                    
                    data = await response.json()
                    synced_lyrics = data.get('syncedLyrics')
                    
                    if not synced_lyrics:
                        logger.debug("No synced lyrics on LRCLIB")
                        return None
                    
                    return self._parse_lrc(synced_lyrics)
            
        except asyncio.TimeoutError:
            logger.warning("⚠️ LRCLIB timeout")
            return None
        except Exception as e:
            logger.debug(f"LRCLIB error: {e}")
            return None
    
    async def _fetch_from_genius(self, track_title: str, artist: str, duration: int) -> Optional[List[LyricsLine]]:
        """Genius APIから歌詞を取得（lyricsgenius使用）"""
        try:
            # Genius APIキーが必要（環境変数から取得）
            api_key = os.getenv('GENIUS_API_KEY')
            if not api_key:
                logger.debug("Genius API key not configured")
                return None
            
            # lyricsgenius ライブラリを使用
            try:
                import lyricsgenius
            except ImportError:
                logger.warning("lyricsgenius not installed. Run: pip install lyricsgenius")
                return None
            
            # Geniusクライアントを作成
            genius = lyricsgenius.Genius(
                api_key,
                verbose=False,
                remove_section_headers=True,
                skip_non_songs=True,
                timeout=5
            )
            
            # 曲を検索
            song = genius.search_song(track_title, artist)
            
            if not song or not song.lyrics:
                logger.debug(f"No lyrics found on Genius for: {track_title}")
                return None
            
            # タイムスタンプなしの歌詞を推定タイムスタンプ付きに変換
            return self._estimate_timestamps(song.lyrics, duration)
        
        except Exception as e:
            logger.debug(f"Genius error: {e}")
            return None
    
    def _estimate_timestamps(self, lyrics_text: str, duration: int = 180000) -> List[LyricsLine]:
        """タイムスタンプなしの歌詞に推定タイムスタンプを付与"""
        lines = [line.strip() for line in lyrics_text.split('\n') if line.strip()]
        
        if not lines:
            return []
        
        # 曲の長さを行数で割って、均等に配置
        duration_sec = duration / 1000.0
        interval = duration_sec / len(lines)
        
        lyrics = []
        for i, line in enumerate(lines):
            timestamp = i * interval
            lyrics.append(LyricsLine(timestamp, line))
        
        return lyrics
    
    def _parse_lrc(self, lrc_text: str) -> List[LyricsLine]:
        """LRC形式の歌詞をパース"""
        lyrics = []
        
        # [mm:ss.xx] text の形式
        pattern = re.compile(r'\[(\d+):(\d+)\.(\d+)\](.+)')
        
        for line in lrc_text.split('\n'):
            match = pattern.match(line.strip())
            if match:
                minutes = int(match.group(1))
                seconds = int(match.group(2))
                centiseconds = int(match.group(3))
                text = match.group(4).strip()
                
                # 秒数に変換
                timestamp = minutes * 60 + seconds + centiseconds / 100.0
                
                lyrics.append(LyricsLine(timestamp, text))
        
        # タイムスタンプ順にソート
        lyrics.sort(key=lambda x: x.timestamp)
        
        return lyrics
    
    async def start_lyrics_for_track(self, guild_id: int, track: wavelink.Playable):
        """曲の歌詞配信を開始"""
        try:
            if guild_id not in self.lyrics_enabled or not self.lyrics_enabled[guild_id]:
                return
            
            # トラック情報を保存
            self.current_track_info[guild_id] = {
                'title': track.title,
                'artist': getattr(track, 'author', 'Unknown'),
                'artwork': getattr(track, 'artwork', None),
                'duration': track.length
            }
            
            # 歌詞チャンネルを取得
            guild = self.bot.get_guild(guild_id)
            if not guild:
                return
            
            lyrics_channel_id = self.lyrics_channels.get(guild_id)
            if not lyrics_channel_id:
                return
            
            lyrics_channel = guild.get_channel(lyrics_channel_id)
            if not lyrics_channel:
                return
            
            # 歌詞を取得中メッセージ
            try:
                searching_msg = await lyrics_channel.send(f"🔍 歌詞を検索中: **{track.title}**")
            except:
                searching_msg = None
            
            # 歌詞を取得
            logger.info(f"🎤 Fetching lyrics for: {track.title}")
            lyrics = await self.fetch_lyrics(
                track.title,
                getattr(track, 'author', 'Unknown'),
                track.length
            )
            
            # 検索中メッセージを削除
            if searching_msg:
                try:
                    await searching_msg.delete()
                except:
                    pass
            
            if lyrics:
                self.current_lyrics[guild_id] = lyrics
                self.lyrics_index[guild_id] = 0
                
                # 成功メッセージ
                embed = discord.Embed(
                    title="✅ 歌詞を取得しました",
                    description=f"**{track.title}**\n{len(lyrics)}行の歌詞を配信します",
                    color=0x00ff88
                )
                if getattr(track, 'artwork', None):
                    embed.set_thumbnail(url=track.artwork)
                
                try:
                    await lyrics_channel.send(embed=embed, delete_after=5)
                except:
                    pass
                
                logger.info(f"✅ Lyrics loaded: {len(lyrics)} lines")
            else:
                # 歌詞が見つからない
                self.current_lyrics.pop(guild_id, None)
                self.lyrics_index.pop(guild_id, None)
                
                embed = discord.Embed(
                    title="❌ 歌詞が見つかりませんでした",
                    description=f"**{track.title}**\nこの曲の歌詞は利用できません",
                    color=0xff4444
                )
                
                try:
                    await lyrics_channel.send(embed=embed, delete_after=10)
                except:
                    pass
                
                logger.info("ℹ️ No lyrics available for this track")
            
        except Exception as e:
            logger.error(f"❌ Failed to start lyrics: {e}")
            import traceback
            traceback.print_exc()
    
    async def stop_lyrics_for_guild(self, guild_id: int):
        """ギルドの歌詞配信を停止"""
        self.current_lyrics.pop(guild_id, None)
        self.lyrics_index.pop(guild_id, None)
        self.current_track_info.pop(guild_id, None)
    
    async def get_or_create_lyrics_channel(self, guild: discord.Guild) -> Optional[discord.TextChannel]:
        """歌詞チャンネルを取得または作成"""
        try:
            # 既存のチャンネルを確認
            if guild.id in self.lyrics_channels:
                channel = guild.get_channel(self.lyrics_channels[guild.id])
                if channel:
                    return channel
            
            # 既存の lyrics-stream チャンネルを探す
            channel = discord.utils.get(guild.text_channels, name='lyrics-stream')
            if channel:
                self.lyrics_channels[guild.id] = channel.id
                return channel
            
            # 新規作成
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(
                    send_messages=False,
                    read_messages=True
                ),
                guild.me: discord.PermissionOverwrite(
                    send_messages=True,
                    manage_webhooks=True
                )
            }
            
            channel = await guild.create_text_channel(
                name='lyrics-stream',
                topic='🎤 リアルタイム歌詞配信',
                overwrites=overwrites,
                reason='Lyrics streaming channel'
            )
            
            self.lyrics_channels[guild.id] = channel.id
            logger.info(f"✅ Created lyrics channel in {guild.name}")
            
            return channel
            
        except Exception as e:
            logger.error(f"❌ Failed to create lyrics channel: {e}")
            return None
    
    async def get_or_create_webhook(self, guild: discord.Guild, channel: discord.TextChannel) -> Optional[discord.Webhook]:
        """Webhookを取得または作成"""
        try:
            # 既存のWebhookを確認
            if guild.id in self.lyrics_webhooks:
                webhook = self.lyrics_webhooks[guild.id]
                try:
                    # Webhookがまだ有効か確認
                    await webhook.fetch()
                    return webhook
                except:
                    # 無効なWebhookは削除
                    self.lyrics_webhooks.pop(guild.id, None)
            
            # チャンネルのWebhookを取得
            webhooks = await channel.webhooks()
            webhook = discord.utils.get(webhooks, name='Lyrics Bot')
            
            if not webhook:
                # 新規作成
                webhook = await channel.create_webhook(
                    name='Lyrics Bot',
                    reason='Lyrics streaming webhook'
                )
            
            self.lyrics_webhooks[guild.id] = webhook
            logger.info(f"✅ Webhook ready for {guild.name}")
            
            return webhook
            
        except Exception as e:
            logger.error(f"❌ Failed to create webhook: {e}")
            return None
    
    @app_commands.command(name="lyrics_mode", description="歌詞配信のON/OFF")
    @app_commands.describe(mode="ON または OFF")
    @app_commands.choices(mode=[
        app_commands.Choice(name="ON", value="on"),
        app_commands.Choice(name="OFF", value="off"),
    ])
    async def lyrics_mode(self, interaction: discord.Interaction, mode: str):
        """歌詞配信モードの切り替え"""
        await interaction.response.defer()
        
        try:
            if mode == "on":
                # チャンネルを作成または取得
                channel = await self.get_or_create_lyrics_channel(interaction.guild)
                if not channel:
                    await interaction.followup.send("❌ 歌詞チャンネルの作成に失敗しました。", ephemeral=True)
                    return
                
                # Webhookを作成または取得
                webhook = await self.get_or_create_webhook(interaction.guild, channel)
                if not webhook:
                    await interaction.followup.send("❌ Webhookの作成に失敗しました。", ephemeral=True)
                    return
                
                # 有効化
                self.lyrics_enabled[interaction.guild.id] = True
                
                embed = discord.Embed(
                    title="✅ 歌詞配信を有効化しました",
                    description=f"歌詞は {channel.mention} にリアルタイムで配信されます。",
                    color=0x00ff88
                )
                embed.add_field(name="精度", value="0.1秒間隔", inline=True)
                embed.add_field(name="オフセット", value=f"{OFFSET}秒早め", inline=True)
                
                await interaction.followup.send(embed=embed)
                
            else:  # off
                self.lyrics_enabled[interaction.guild.id] = False
                await self.stop_lyrics_for_guild(interaction.guild.id)
                
                embed = discord.Embed(
                    title="⏹️ 歌詞配信を無効化しました",
                    color=0xff4444
                )
                
                await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"❌ Error in lyrics_mode command: {e}")
            await interaction.followup.send("❌ エラーが発生しました。", ephemeral=True)


async def setup(bot):
    await bot.add_cog(LyricsStreamer(bot))
