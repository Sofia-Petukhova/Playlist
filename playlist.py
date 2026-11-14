"""Композиции и порядок воспроизведения плейлиста."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

import audio
from linked_list import LinkedList, LinkedListItem


@dataclass(frozen=True, eq=False)
class Composition:
    """Отдельная запись в плейлисте, даже если тот же файл добавлен дважды."""

    path: Path

    @property
    def title(self) -> str:
        """Название для отображения в окне."""
        return self.path.stem


class PlayList(LinkedList[Composition]):
    """Переключает треки по ссылкам и сохраняет текущий узел при перестановке."""

    def __init__(self, play_file: Callable[[Path], None] = audio.play_file,
                 stop_audio: Callable[[], None] = audio.stop) -> None:
        super().__init__()
        self._playing: Optional[LinkedListItem[Composition]] = None
        self._play_file = play_file
        self._stop_audio = stop_audio

    @property
    def current(self) -> Optional[Composition]:
        """Играющая композиция или None после остановки."""
        return self._playing.data if self._playing is not None else None

    def _start(self, node: Optional[LinkedListItem[Composition]]) -> None:
        if node is not None:
            self._playing = None
            self._play_file(node.data.path)
            self._playing = node

    def play_all(self, item: Composition) -> None:
        """Начинает воспроизведение с выбранной композиции."""
        self._start(self._find(item))

    def next_track(self) -> None:
        """Переходит вперёд, включая переход с последнего трека на первый."""
        self._start(self._playing.next_item if self._playing is not None else self.first_item)

    def previous_track(self) -> None:
        """Переходит назад, включая переход с первого трека на последний."""
        self._start(self._playing.previous_item if self._playing is not None else self.last)

    def stop(self) -> None:
        """Останавливает активный поток."""
        if self._playing is not None:
            self._playing = None
            self._stop_audio()

    def remove(self, item: Composition) -> None:
        """При удалении играющего трека продолжает со следующего."""
        node = self._find(item)
        playing = node is self._playing
        successor = node.next_item
        self._detach(node)
        if playing:
            self.stop()
            if successor is not node:
                self._start(successor)

    def move(self, source: int, target: int) -> None:
        """Переставляет узел на указанную позицию без перезапуска музыки."""
        node = self.node_at(source)
        destination = self.node_at(target)
        if node is destination:
            return
        order = range(len(self))
        forward = order[source] < order[target]
        self._detach(node)
        previous = destination if forward else destination.previous_item
        self._insert_after(previous, node)
        if not forward and destination is self.first_item:
            self.first_item = node
