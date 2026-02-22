# 重複コマンドの修正ガイド 🔧

## 問題

スラッシュコマンドが重複して表示される：
- `/chat` が3回表示
- `/clear` が3回表示
- `/dashboard` が3回表示
- など

## 原因

1. **グローバルコマンドとギルドコマンドの重複**
   - `on_ready`でグローバル同期
   - `on_guild_join`でギルド固有の同期
   - 両方が実行されて重複

2. **複数回の同期処理**
   - Botが再起動されるたびに同期
   - 古いコマンドが残っている

## 解決方法

### ステップ1: 重複コマンドをクリア

```bash
cd bot
python clear_duplicate_commands.py
```

このスクリプトは：
1. グローバルコマンドをクリア
2. 全ギルドのコマンドをクリア
3. 自動的に終了

### ステップ2: Botを再起動

```bash
python bot/main.py
```

または、デプロイ環境で再起動：
- Heroku: `heroku restart`
- Koyeb: ダッシュボードから再起動
- Render: ダッシュボードから再起動

### ステップ3: 確認

Discordで `/` を入力して、各コマンドが1つずつ表示されることを確認。

## 修正内容

### bot/main.py

**Before:**
```python
async def on_guild_join(self, guild):
    """Called when bot joins a new guild - sync commands"""
    self.tree.copy_global_to(guild=guild)
    synced = await self.tree.sync(guild=guild)  # ❌ 重複の原因
```

**After:**
```python
async def on_guild_join(self, guild):
    """Called when bot joins a new guild"""
    # グローバルコマンドは自動的に利用可能
    # ギルド固有の同期は不要
```

## コマンド同期の仕組み

### グローバルコマンド
- `await bot.tree.sync()` で全ギルドに配信
- 1回の同期で全ギルドで利用可能
- 反映に最大1時間かかる場合がある

### ギルドコマンド
- `await bot.tree.sync(guild=guild)` で特定ギルドに配信
- 即座に反映される
- テスト用に使用

### 推奨設定
- **本番環境**: グローバルコマンドのみ使用
- **開発環境**: ギルドコマンドで高速テスト

## トラブルシューティング

### コマンドが表示されない

1. **Botの権限を確認**
   - `applications.commands` スコープが必要
   - 招待リンクを再生成

2. **Discordを再起動**
   - キャッシュをクリア
   - Discordアプリを完全に終了して再起動

3. **時間を待つ**
   - グローバルコマンドは最大1時間かかる

### まだ重複している

1. **clear_duplicate_commands.pyを再実行**
2. **Botを完全に停止**
3. **1時間待つ**（Discordのキャッシュ）
4. **Botを再起動**

### 特定のギルドでのみ表示したい

```python
# main.py の on_ready に追加
TEST_GUILD_ID = 123456789  # テストギルドのID

async def on_ready(self):
    # テストギルドのみに同期
    guild = discord.Object(id=TEST_GUILD_ID)
    self.tree.copy_global_to(guild=guild)
    await self.tree.sync(guild=guild)
```

## 予防策

### 1. 同期は1回のみ
```python
# ✅ Good
async def on_ready(self):
    await self.tree.sync()  # グローバルのみ

# ❌ Bad
async def on_ready(self):
    await self.tree.sync()  # グローバル
    for guild in self.guilds:
        await self.tree.sync(guild=guild)  # 重複！
```

### 2. on_guild_joinでは同期しない
```python
# ✅ Good
async def on_guild_join(self, guild):
    logger.info(f'Joined {guild.name}')
    # グローバルコマンドは自動的に利用可能

# ❌ Bad
async def on_guild_join(self, guild):
    await self.tree.sync(guild=guild)  # 不要！
```

### 3. 開発時はギルドコマンドを使用
```python
# 開発用
DEV_GUILD_ID = 123456789

async def on_ready(self):
    if os.getenv('ENVIRONMENT') == 'development':
        guild = discord.Object(id=DEV_GUILD_ID)
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)
    else:
        await self.tree.sync()  # 本番はグローバル
```

## 関連ファイル

- `bot/main.py` - コマンド同期処理（修正済み）
- `bot/clear_duplicate_commands.py` - 重複クリアスクリプト
- `COMMAND_LIST.md` - 全コマンド一覧

---

修正日: 2026-01-24
