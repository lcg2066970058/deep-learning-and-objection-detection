import json
from pathlib import Path
from config.settings import LAST_OPEN_PATH


def save_last_path(file_path: str):
    """保存最近打开的路径"""
    data = {"last_path": file_path}
    try:
        with open(LAST_OPEN_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def load_last_path() -> str:
    """加载最近打开的路径，返回空字符串如果不存在"""
    if not LAST_OPEN_PATH.exists():
        return ""
    try:
        with open(LAST_OPEN_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            path = data.get("last_path", "")
            # 验证路径是否存在
            if path and Path(path).exists():
                return path
            # 如果路径不存在，返回空字符串
            return ""
    except Exception:
        return ""
