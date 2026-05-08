from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DEFAULT_AVATAR_PATH = BASE_DIR / "static" / "images" / "default-avatar.png"


def get_default_avatar() -> bytes | None:
    """
    Возвращает байты дефолтного аватара из статики.
    Если файл не найден — возвращает None.
    """
    if DEFAULT_AVATAR_PATH.exists():
        return DEFAULT_AVATAR_PATH.read_bytes()
    return None
