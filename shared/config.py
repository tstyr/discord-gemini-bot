"""共有設定ファイル"""

# AIモード定義
AI_MODES = {
    "standard": {
        "name": "Standard",
        "description": "バランスの取れた汎用モード",
        "system_prompt": "あなたは親切で知識豊富なアシスタントです。"
    },
    "assistant": {
        "name": "Assistant", 
        "description": "タスク支援に特化したモード",
        "system_prompt": "あなたは効率的なタスク管理と問題解決を支援するアシスタントです。"
    },
    "creative": {
        "name": "Creative",
        "description": "創造的な回答を生成するモード",
        "system_prompt": "あなたは創造的で独創的なアイデアを提案するクリエイティブアシスタントです。"
    },
    "code_expert": {
        "name": "Code Expert",
        "description": "プログラミング支援に特化したモード",
        "system_prompt": "あなたは経験豊富なソフトウェアエンジニアです。コードレビュー、デバッグ、最適化を支援します。"
    }
}

# デフォルト設定
DEFAULT_MODE = "standard"
MAX_TOKENS = 2048
