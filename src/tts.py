"""edge-tts を使用して音声ファイル（.mp3）を生成するモジュール。
"""

import asyncio
import edge_tts

# 利用可能な自然な日本語音声の例:
# "ja-JP-NanamiNeural" (明るい女性声)
# "ja-JP-KeitaNeural" (落ち着いた男性声)
DEFAULT_VOICE = "ja-JP-NanamiNeural"

async def _synthesize_async(text: str, output_path: str, voice: str = DEFAULT_VOICE):
    """テキストからmp3音声を非同期で合成して保存する。"""
    communicate = edge_tts.Communicate(text=text, voice=voice, rate="+5%")
    await communicate.save(output_path)

def text_to_speech(text: str, output_path: str, voice: str = DEFAULT_VOICE):
    """テキストを音声ファイル（.mp3）に変換する同期ラッパー関数。"""
    asyncio.run(_synthesize_async(text, output_path, voice))
