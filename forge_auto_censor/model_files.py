"""Persistent ONNX files; Hugging Face is used only to obtain missing weights."""
from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path
from threading import Lock

MODEL_REPO = "deepghs/anime_censor_detection"
MODEL_LEVELS = {"s": "标准模型（精度优先）", "n": "轻量模型（速度优先）"}
MODEL_DIR = Path(__file__).resolve().parents[1] / "models"
_PREPARE_LOCK = Lock()


def model_name(level):
    if level not in MODEL_LEVELS:
        raise ValueError("二次元检测模型无效，请选择标准模型或轻量模型")
    return f"censor_detect_v1.0_{level}"


def _cache_roots():
    from huggingface_hub import constants

    roots = [Path(constants.HF_HUB_CACHE), Path.home() / ".cache/huggingface/hub"]
    for key in ("HF_HUB_CACHE", "HUGGINGFACE_HUB_CACHE", "HF_HOME"):
        value = os.environ.get(key)
        if value:
            path = Path(value).expanduser()
            roots.append(path / "hub" if key == "HF_HOME" else path)
    return list(dict.fromkeys(root.resolve() for root in roots))


def _find_cached_model(name):
    from huggingface_hub import try_to_load_from_cache

    for cache_root in _cache_roots():
        cached = try_to_load_from_cache(MODEL_REPO, f"{name}/model.onnx", cache_dir=cache_root)
        if isinstance(cached, str) and Path(cached).is_file():
            return Path(cached)
    return None


def _download_model(name):
    from huggingface_hub import hf_hub_download

    return Path(hf_hub_download(MODEL_REPO, f"{name}/model.onnx"))


def ensure_model_file(level):
    """Return a real local file, copying/downloading only if it is absent."""
    name = model_name(level)
    target = MODEL_DIR / f"{name}.onnx"
    with _PREPARE_LOCK:
        if target.is_file() and target.stat().st_size:
            return target
        source = _find_cached_model(name)
        if source is None:
            try:
                source = _download_model(name)
            except Exception as exc:
                raise RuntimeError(
                    f"本地模型不存在且下载失败，请把 {name}/model.onnx 下载后重命名放到：{target}。"
                    "模型地址：https://huggingface.co/deepghs/anime_censor_detection/tree/main；"
                    "网络受限时可在启动 Forge 前设置 HF_ENDPOINT=https://hf-mirror.com。"
                ) from exc
        # Never leave a half-copied .onnx file that a later launch might load.
        target.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=target.parent, suffix=".part", delete=False) as handle:
            staged = Path(handle.name)
        try:
            shutil.copyfile(source, staged)
            if not staged.stat().st_size:
                raise RuntimeError(f"模型文件为空：{source}")
            staged.replace(target)
        finally:
            staged.unlink(missing_ok=True)
    return target
