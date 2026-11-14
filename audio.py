"""Воспроизведение одного локального файла через SDL Mixer."""

from pathlib import Path

from pygame import mixer


def play_file(path: Path) -> None:
    """Запускает файл и сообщает об ошибке устройства или декодирования."""
    try:
        if not mixer.get_init():
            mixer.init()
        mixer.music.load(str(path))
        mixer.music.play()
    except (RuntimeError, OSError) as exc:
        stop()
        raise OSError(f"Не удалось воспроизвести «{path.name}». {exc}") from exc


def stop() -> None:
    """Останавливает поток и освобождает файл."""
    if mixer.get_init():
        mixer.music.stop()
        mixer.music.unload()


def is_playing() -> bool:
    """Проверяет, продолжается ли воспроизведение."""
    return bool(mixer.get_init() and mixer.music.get_busy())
