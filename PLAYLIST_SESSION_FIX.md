# プレイリスト・セッション再開修正プロンプト

## 問題点

1. **プレイリスト選択時に再生できない**
2. **登録したプレイリストの曲が消える**
3. **セッション再開が機能しない**

## 原因分析

### 1. プレイリスト選択の問題

#### 考えられる原因
- プレイリストIDとトラックの紐付けが正しくない
- データベースへの保存時にエラーが発生
- トラック情報の取得に失敗

#### 確認ポイント
```python
# playlist_manager.pyで確認
- save_playlist()でトラックが正しく保存されているか
- load_playlist()でトラックが正しく取得できているか
- トラックのURI/URLが正しく保存されているか
```

### 2. プレイリスト曲が消える問題

#### 考えられる原因
- データベーススキーマの問題（CASCADE削除）
- トランザクションのロールバック
- 重複キー制約違反

#### 確認ポイント
```sql
-- Supabaseで確認
SELECT * FROM playlists WHERE guild_id = 'YOUR_GUILD_ID';
SELECT * FROM playlist_tracks WHERE playlist_id = 'YOUR_PLAYLIST_ID';

-- 外部キー制約を確認
SELECT
    tc.constraint_name,
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name,
    rc.delete_rule
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
JOIN information_schema.referential_constraints AS rc
    ON rc.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_name = 'playlist_tracks';
```

### 3. セッション再開の問題

#### 考えられる原因
- `active_sessions`テーブルにデータがない
- トラック検索に失敗
- ボイスチャンネル接続に失敗

#### 確認ポイント
```python
# main.pyの_resume_music_sessions()で確認
- active_sessionsにデータが存在するか
- guild_idが正しいか
- トラック検索が成功しているか
- ボイスチャンネルに接続できているか
```

## 修正方法

### 1. プレイリスト保存の修正

#### `playlist_manager.py`

```python
async def save_playlist(self, guild_id: int, name: str, tracks: list):
    """プレイリストを保存（トランザクション対応）"""
    try:
        if not self.bot.supabase_client or not self.bot.supabase_client.client:
            return False
        
        # 1. プレイリストを作成
        playlist_data = {
            'guild_id': str(guild_id),
            'name': name,
            'track_count': len(tracks)
        }
        
        result = self.bot.supabase_client.client.table('playlists')\
            .insert(playlist_data)\
            .execute()
        
        if not result.data:
            logger.error("Failed to create playlist")
            return False
        
        playlist_id = result.data[0]['id']
        logger.info(f"Created playlist: {playlist_id}")
        
        # 2. トラックを保存（バッチ処理）
        track_data = []
        for i, track in enumerate(tracks):
            track_data.append({
                'playlist_id': playlist_id,
                'track_title': track.title,
                'track_url': track.uri if hasattr(track, 'uri') else '',
                'track_author': getattr(track, 'author', 'Unknown'),
                'track_duration': track.length if hasattr(track, 'length') else 0,
                'position': i
            })
        
        # バッチサイズ100で分割して保存
        batch_size = 100
        for i in range(0, len(track_data), batch_size):
            batch = track_data[i:i + batch_size]
            self.bot.supabase_client.client.table('playlist_tracks')\
                .insert(batch)\
                .execute()
            logger.info(f"Saved tracks {i} to {i + len(batch)}")
        
        logger.info(f"✅ Saved playlist '{name}' with {len(tracks)} tracks")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to save playlist: {e}")
        import traceback
        traceback.print_exc()
        return False
```

#### `playlist_manager.py` - ロード修正

```python
async def load_playlist(self, playlist_id: str):
    """プレイリストをロード"""
    try:
        if not self.bot.supabase_client or not self.bot.supabase_client.client:
            return []
        
        # トラックを取得（position順）
        result = self.bot.supabase_client.client.table('playlist_tracks')\
            .select('*')\
            .eq('playlist_id', playlist_id)\
            .order('position', desc=False)\
            .execute()
        
        if not result.data:
            logger.warning(f"No tracks found for playlist {playlist_id}")
            return []
        
        logger.info(f"Found {len(result.data)} tracks for playlist {playlist_id}")
        
        # トラックを検索
        import wavelink
        tracks = []
        
        for track_data in result.data:
            try:
                # URLがある場合は直接検索
                if track_data.get('track_url'):
                    search_result = await wavelink.Playable.search(track_data['track_url'])
                else:
                    # タイトルで検索
                    search_query = f"{track_data['track_author']} - {track_data['track_title']}"
                    search_result = await wavelink.Playable.search(f"ytsearch:{search_query}")
                
                if search_result:
                    if isinstance(search_result, list):
                        tracks.append(search_result[0])
                    else:
                        tracks.append(search_result)
                    logger.debug(f"Found track: {track_data['track_title']}")
                else:
                    logger.warning(f"Track not found: {track_data['track_title']}")
                    
            except Exception as e:
                logger.error(f"Error loading track {track_data['track_title']}: {e}")
                continue
        
        logger.info(f"✅ Loaded {len(tracks)} tracks from playlist")
        return tracks
        
    except Exception as e:
        logger.error(f"❌ Failed to load playlist: {e}")
        import traceback
        traceback.print_exc()
        return []
```

### 2. セッション再開の修正

#### `main.py` - `_resume_music_sessions()`

```python
async def _resume_music_sessions(self):
    """Resume music sessions from Supabase after restart"""
    try:
        if not self.supabase_client or not self.supabase_client.client:
            logger.info("Supabase not available, skipping session resume")
            return
        
        # Get active sessions from Supabase
        result = self.supabase_client.client.table('active_sessions')\
            .select('*')\
            .eq('is_playing', True)\
            .execute()
        
        if not result.data:
            logger.info("No active sessions to resume")
            return
        
        logger.info(f"Found {len(result.data)} active sessions to resume")
        
        music_cog = self.get_cog('MusicPlayer')
        if not music_cog:
            logger.warning("Music player cog not loaded, cannot resume sessions")
            return
        
        for session in result.data:
            try:
                guild_id = int(session['guild_id'])
                guild = self.get_guild(guild_id)
                
                if not guild:
                    logger.warning(f"Guild {guild_id} not found")
                    # Clear session
                    await self.supabase_client.update_active_session(guild_id, None)
                    continue
                
                # Find voice channel with members
                voice_channel = None
                for vc in guild.voice_channels:
                    # Botを除いたメンバー数をチェック
                    human_members = [m for m in vc.members if not m.bot]
                    if len(human_members) > 0:
                        voice_channel = vc
                        logger.info(f"Found voice channel: {vc.name} with {len(human_members)} members")
                        break
                
                if not voice_channel:
                    logger.info(f"No voice channel with members in {guild.name}")
                    # Clear session
                    await self.supabase_client.update_active_session(guild_id, None)
                    continue
                
                # Get track info
                track_title = session.get('track_title')
                if not track_title:
                    logger.warning("No track title in session")
                    continue
                
                logger.info(f"Resuming session in {guild.name}: {track_title}")
                
                # Search for the track
                import wavelink
                
                # より正確な検索のため、アーティスト名も使用
                search_query = track_title
                tracks = await wavelink.Playable.search(f"ytsearch:{search_query}")
                
                if not tracks or len(tracks) == 0:
                    logger.warning(f"Could not find track: {track_title}")
                    # Clear session
                    await self.supabase_client.update_active_session(guild_id, None)
                    continue
                
                track = tracks[0]
                logger.info(f"Found track: {track.title}")
                
                # Connect to voice channel
                try:
                    if guild.voice_client:
                        # 既に接続している場合は切断
                        await guild.voice_client.disconnect()
                    
                    vc = await voice_channel.connect(cls=wavelink.Player)
                    logger.info(f"Connected to voice channel: {voice_channel.name}")
                except Exception as vc_err:
                    logger.error(f"Failed to connect to voice channel: {vc_err}")
                    continue
                
                # Play the track
                try:
                    await vc.play(track)
                    logger.info(f"Started playing: {track.title}")
                    
                    # Seek to position if available
                    position_ms = session.get('position_ms', 0)
                    if position_ms > 0 and position_ms < track.length:
                        await asyncio.sleep(0.5)  # Wait for playback to start
                        await vc.seek(position_ms)
                        logger.info(f"Seeked to position: {position_ms}ms")
                    
                    # Update queue
                    queue = music_cog.get_queue(guild_id)
                    queue.current = track
                    
                    logger.info(f"✅ Resumed session in {guild.name}")
                    
                    # Send notification
                    text_channel = guild.system_channel or guild.text_channels[0] if guild.text_channels else None
                    if text_channel:
                        try:
                            embed = discord.Embed(
                                title="🔄 Session Resumed",
                                description=f"**{track.title}**",
                                color=0x00ff88
                            )
                            if hasattr(track, 'artwork') and track.artwork:
                                embed.set_thumbnail(url=track.artwork)
                            await text_channel.send(embed=embed)
                        except:
                            pass
                    
                except Exception as play_err:
                    logger.error(f"Failed to play track: {play_err}")
                    import traceback
                    traceback.print_exc()
                    continue
                
            except Exception as e:
                logger.error(f"Error resuming session: {e}")
                import traceback
                traceback.print_exc()
        
    except Exception as e:
        logger.error(f"Error in _resume_music_sessions: {e}")
        import traceback
        traceback.print_exc()
```

### 3. データベーススキーマ確認

#### Supabase SQL Editorで実行

```sql
-- playlist_tracksの外部キー制約を確認
SELECT
    tc.constraint_name,
    rc.delete_rule
FROM information_schema.table_constraints AS tc
JOIN information_schema.referential_constraints AS rc
    ON rc.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_name = 'playlist_tracks';

-- もしCASCADE削除になっている場合は修正
ALTER TABLE playlist_tracks
DROP CONSTRAINT IF EXISTS playlist_tracks_playlist_id_fkey;

ALTER TABLE playlist_tracks
ADD CONSTRAINT playlist_tracks_playlist_id_fkey
FOREIGN KEY (playlist_id)
REFERENCES playlists(id)
ON DELETE CASCADE;  -- プレイリスト削除時にトラックも削除
```

## テスト手順

### 1. プレイリスト保存テスト

```
1. /playlist_create name:test
2. 曲を5曲追加
3. /playlist_save
4. Supabaseでデータ確認:
   SELECT * FROM playlists WHERE name = 'test';
   SELECT * FROM playlist_tracks WHERE playlist_id = '...';
```

### 2. プレイリストロードテスト

```
1. /playlist_load name:test
2. 曲が正しく再生されるか確認
3. キューに全曲追加されているか確認
```

### 3. セッション再開テスト

```
1. 曲を再生中にBotを再起動
2. ボイスチャンネルにメンバーがいることを確認
3. Bot起動後、自動的に再生が再開されるか確認
4. 再生位置が正しいか確認
```

## ログ確認

```bash
# Koyebログで確認
- "Created playlist: ..." が表示されるか
- "Saved tracks X to Y" が表示されるか
- "Found X tracks for playlist" が表示されるか
- "Resuming session in ..." が表示されるか
- "✅ Resumed session in ..." が表示されるか
```

## トラブルシューティング

### プレイリストが保存されない
- Supabase接続を確認
- RLSポリシーを確認
- ログでエラーメッセージを確認

### トラックが見つからない
- track_urlが正しく保存されているか確認
- Lavalinkサーバーが起動しているか確認
- YouTube APIの制限に達していないか確認

### セッション再開が動作しない
- active_sessionsテーブルにデータがあるか確認
- is_playing = true になっているか確認
- ボイスチャンネルにメンバーがいるか確認
