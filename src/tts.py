"""Edge-TTS を使用して、複数話者のポッドキャスト音声を並行合成し、1本のmp3に結合するモジュール。
"""

import os
import sys
import asyncio
import tempfile
import subprocess
from typing import List, Dict, Any, Optional
import edge_tts
from config_loader import load_config

def get_voice_map(config: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
    """設定から話者名と音声ボイスの対応マップを構築する。"""
    if config is None:
        config = load_config()

    speakers = config.get("speakers", {})
    host1 = speakers.get("host1", {})
    host2 = speakers.get("host2", {})

    vmap = {}
    if "name" in host1 and "voice" in host1:
        vmap[host1["name"]] = host1["voice"]
    if "name" in host2 and "voice" in host2:
        vmap[host2["name"]] = host2["voice"]

    # フォールバック
    if not vmap:
        vmap = {
            "Keita": "ja-JP-KeitaNeural",
            "Nanami": "ja-JP-NanamiNeural"
        }
    return vmap

async def _synthesize_line(speaker: str, text: str, output_chunk_path: str, sem: asyncio.Semaphore, voice_map: Dict[str, str]):
    """単一のセリフを並行制御しながら音声合成して一時ファイルに保存する。"""
    default_voice = list(voice_map.values())[0] if voice_map else "ja-JP-NanamiNeural"
    voice = voice_map.get(speaker, default_voice)

    async with sem:
        try:
            communicate = edge_tts.Communicate(text=text, voice=voice, rate="+5%")
            await communicate.save(output_chunk_path)
        except Exception as e:
            print(f"セリフ合成失敗 [{speaker}]: {text[:30]}... ({e})")
            await asyncio.sleep(1)
            communicate = edge_tts.Communicate(text=text, voice=voice)
            await communicate.save(output_chunk_path)

async def synthesize_podcast_async(dialogue_lines: List[Dict[str, str]], output_path: str, config: Optional[Dict[str, Any]] = None):
    """全対話セリフを非同期並行で合成し、1つのmp3ファイルに結合する。"""
    if not dialogue_lines:
        raise ValueError("対話台本が空です。")

    voice_map = get_voice_map(config)

    with tempfile.TemporaryDirectory() as temp_dir:
        tasks = []
        chunk_files = []
        sem = asyncio.Semaphore(8)

        print(f"全 {len(dialogue_lines)} 行のセリフを並行合成中 (話者: {', '.join(voice_map.keys())})...")

        for idx, line in enumerate(dialogue_lines):
            speaker = line.get("speaker", "Nanami")
            text = line.get("text", "")
            chunk_path = os.path.join(temp_dir, f"chunk_{idx:04d}.mp3")
            chunk_files.append(chunk_path)
            tasks.append(_synthesize_line(speaker, text, chunk_path, sem, voice_map))

        await asyncio.gather(*tasks)
        print("-> すべてのセリフの音声合成が完了しました。")

        print("音声を1本のポッドキャストに結合中...")
        valid_chunks = [f for f in chunk_files if os.path.exists(f) and os.path.getsize(f) > 0]
        if not valid_chunks:
            raise RuntimeError("有効な音声チャンクが生成されませんでした。")

        # 1. ffmpeg による高品質結合を試行
        concat_list_file = os.path.join(temp_dir, "concat_list.txt")
        with open(concat_list_file, "w", encoding="utf-8") as f:
            for c in valid_chunks:
                f.write(f"file '{c}'\n")

        ffmpeg_cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", concat_list_file, "-c", "copy", output_path
        ]

        ffmpeg_success = False
        try:
            res = subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if res.returncode == 0:
                ffmpeg_success = True
                print(f"-> ffmpeg による結合成功: {output_path}")
        except FileNotFoundError:
            print("ffmpeg が見つかりません。バイナリ結合にフォールバックします。")

        # 2. ffmpeg がない場合のバイナリ結合フォールバック
        if not ffmpeg_success:
            with open(output_path, "wb") as out_f:
                for chunk_file in valid_chunks:
                    with open(chunk_file, "rb") as in_f:
                        out_f.write(in_f.read())
            print(f"-> バイナリ連結による結合成功: {output_path}")

def synthesize_podcast(dialogue_lines: List[Dict[str, str]], output_path: str, config: Optional[Dict[str, Any]] = None):
    """同期実行用のエントリーラッパー関数。"""
    asyncio.run(synthesize_podcast_async(dialogue_lines, output_path, config))
