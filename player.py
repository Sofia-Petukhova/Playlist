"""Окно музыкального плеера на Tkinter."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk
from typing import Callable, Optional

from playlist import Composition, PlayList


class PlayerWindow:
    """Редактор плейлистов и управление воспроизведением."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.title("Музыкальный плеер")
        root.minsize(620, 390)
        self.name = "Мой плейлист"
        self.library = {self.name: PlayList()}
        body = ttk.Frame(root, padding=16)
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=1)
        body.rowconfigure(3, weight=1)

        ttk.Label(body, text="Плейлист").grid(row=0, sticky="w")
        header = ttk.Frame(body)
        header.grid(row=1, sticky="ew", pady=(4, 14))
        self.selector = ttk.Combobox(header, state="readonly")
        self.selector.pack(side="left", fill="x", expand=True)
        self.selector.bind("<<ComboboxSelected>>", self._switch)
        self._buttons(header, [("Создать", self.create), ("Удалить плейлист", self.delete)])
        ttk.Label(body, text="Композиции").grid(row=2, sticky="w")
        pane = ttk.Frame(body)
        pane.grid(row=3, sticky="nsew", pady=4)
        self.tracks = tk.Listbox(pane, exportselection=False, activestyle="dotbox", height=10)
        scroll = ttk.Scrollbar(pane, command=self.tracks.yview)
        scroll.pack(side="right", fill="y")
        self.tracks.configure(yscrollcommand=scroll.set)
        self.tracks.pack(fill="both", expand=True)
        self.tracks.bind("<Double-Button-1>", self.play_selected)
        self.tracks.bind("<Return>", self.play_selected)
        edit = ttk.Frame(body)
        edit.grid(row=4, sticky="w", pady=(0, 12))
        self._buttons(edit, [("Добавить файлы", self.add), ("Убрать трек", self.remove),
                             ("Выше", lambda: self.move(-1)), ("Ниже", lambda: self.move(1))])
        controls = ttk.Frame(body)
        controls.grid(row=5, sticky="w")
        self._buttons(controls, [("Назад", lambda: self.step(-1)), ("Играть", self.play_selected),
                                 ("Стоп", self.stop), ("Вперёд", lambda: self.step(1))])
        self.status = tk.StringVar(root)
        ttk.Label(body, textvariable=self.status).grid(row=6, sticky="w", pady=(10, 0))
        self._refresh()
        root.after(150, self._poll)
        root.protocol("WM_DELETE_WINDOW", self.close)

    @staticmethod
    def _buttons(parent: ttk.Frame, actions: list[tuple[str, Callable[[], None]]]) -> None:
        """Добавляет кнопки в одну строку."""
        for label, action in actions:
            ttk.Button(parent, text=label, command=action).pack(side="left", padx=2)

    @property
    def playlist(self) -> Optional[PlayList]:
        """Плейлист, открытый в окне."""
        return self.library.get(self.name)

    def _refresh(self, selected: int = 0) -> None:
        """Обновляет список плейлистов и треков."""
        self.selector.configure(values=tuple(self.library))
        self.selector.set(self.name)
        self.tracks.delete(0, tk.END)
        playlist = self.playlist
        if playlist is not None:
            for track in playlist.values():
                self.tracks.insert(tk.END, track.title)
        if self.tracks.size():
            self._select_track(min(selected, self.tracks.size() - 1))
        self._update_status()

    def _select_track(self, index: int) -> None:
        """Выделяет строку и прокручивает список до неё."""
        self.tracks.selection_clear(0, tk.END)
        self.tracks.selection_set(index)
        self.tracks.see(index)

    def _update_status(self) -> None:
        """Показывает состояние выбранного плейлиста."""
        playlist = self.playlist
        if playlist is None:
            self.status.set("Создайте плейлист, чтобы добавить музыку.")
        elif playlist.current is not None:
            self.status.set(f"Играет — {playlist.current.title}")
        elif self.tracks.size():
            self.status.set("Воспроизведение остановлено")
        else:
            self.status.set("Добавьте аудиофайлы в плейлист.")

    def _switch(self, _event: tk.Event) -> None:
        """Открывает выбранный плейлист."""
        new_name = self.selector.get()
        if self.name != new_name:
            self.stop()
            self.name = new_name
            self._refresh()

    def create(self) -> None:
        """Создаёт именованный плейлист."""
        name = (simpledialog.askstring("Новый плейлист", "Название", parent=self.root) or "").strip()
        if not name:
            return
        if name in self.library:
            messagebox.showinfo("Плейлист уже есть", "Выберите другое название.", parent=self.root)
            return
        self.stop()
        self.library[name] = PlayList()
        self.name = name
        self._refresh()

    def delete(self) -> None:
        """Удаляет выбранный плейлист."""
        if self.playlist is not None:
            self.stop()
            del self.library[self.name]
            self.name = next(iter(self.library), "")
            self._refresh()

    def add(self) -> None:
        """Добавляет выбранные музыкальные файлы."""
        playlist = self.playlist
        if playlist is None:
            return
        paths = filedialog.askopenfilenames(parent=self.root, title="Добавить композиции",
                                            filetypes=[("Музыка", ("*.wav", "*.mp3", "*.ogg")),
                                                       ("Все файлы", "*")])
        if paths:
            start = self.tracks.size()
            for path in paths:
                playlist.append(Composition(Path(path)))
            self._refresh(start)

    def remove(self) -> None:
        """Удаляет выбранную запись."""
        playlist = self.playlist
        selection = self.tracks.curselection()
        if playlist is not None and selection:
            index = selection[0]
            track = playlist[index]
            self._audio_action(lambda: playlist.remove(track))
            self._refresh(index)

    def move(self, offset: int) -> None:
        """Перемещает выбранную запись на соседнюю позицию."""
        playlist = self.playlist
        selection = self.tracks.curselection()
        if playlist is not None and selection:
            index = selection[0]
            target = index + offset
            if 0 <= target < self.tracks.size():
                playlist.move(index, target)
                self._refresh(target)

    def _audio_action(self, action: Callable[[], None]) -> None:
        """Выполняет команду и показывает ошибку звука."""
        try:
            action()
        except OSError as exc:
            messagebox.showerror("Ошибка воспроизведения", str(exc), parent=self.root)

    def play_selected(self, _event: Optional[tk.Event] = None) -> None:
        """Запускает трек, выделенный в списке."""
        playlist = self.playlist
        selection = self.tracks.curselection()
        if playlist is not None and selection:
            track = playlist[selection[0]]
            self._audio_action(lambda: playlist.play_all(track))
            self._update_status()

    def step(self, direction: int) -> None:
        """Переключает воспроизведение и выделяет текущую композицию."""
        playlist = self.playlist
        if playlist is not None:
            self._audio_action(playlist.next_track if direction > 0 else playlist.previous_track)
            self._update_status()
            for index, track in enumerate(playlist.values()):
                if track is playlist.current:
                    self._select_track(index)
                    break

    def stop(self) -> None:
        """Завершает воспроизведение вручную."""
        playlist = self.playlist
        if playlist is not None:
            playlist.stop()
            self._update_status()

    def _poll(self) -> None:
        """Проверяет, пора ли запустить следующий трек."""
        playlist = self.playlist
        if playlist is not None and playlist.track_finished():
            self.step(1)
        self.root.after(150, self._poll)

    def close(self) -> None:
        """Освобождает аудиофайл и закрывает окно."""
        self.stop()
        self.root.destroy()


if __name__ == "__main__":
    window = tk.Tk()
    PlayerWindow(window)
    window.mainloop()
