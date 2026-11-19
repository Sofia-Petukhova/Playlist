"""Окно музыкального плеера на Tkinter."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk
from typing import Callable, Optional

import audio
from playlist import Composition, PlayList


class PlayerWindow:
    """Редактор плейлистов и управление воспроизведением."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.title("Музыкальный плеер")
        root.minsize(620, 390)
        self.library = {"Мой плейлист": PlayList()}
        self.name = "Мой плейлист"
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
        for label, action in actions:
            ttk.Button(parent, text=label, command=action).pack(side="left", padx=2)

    @property
    def playlist(self) -> Optional[PlayList]:
        """Плейлист, открытый в окне."""
        return self.library.get(self.name)

    def _refresh(self, selected: int = 0) -> None:
        self.selector.configure(values=tuple(self.library))
        self.selector.set(self.name)
        self.tracks.delete(0, tk.END)
        if self.playlist is not None:
            for node in self.playlist:
                self.tracks.insert(tk.END, node.data.title)
        if self.tracks.size():
            index = min(selected, self.tracks.size() - 1)
            self.tracks.selection_set(index)
            self.tracks.see(index)
        self._status()

    def _status(self) -> None:
        track = self.playlist.current if self.playlist is not None else None
        if track is not None:
            self.status.set(f"Играет — {track.title}")
        elif self.playlist is None:
            self.status.set("Создайте плейлист, чтобы добавить музыку.")
        elif self.playlist.first_item is None:
            self.status.set("Добавьте аудиофайлы в плейлист.")
        else:
            self.status.set("Воспроизведение остановлено")

    def _switch(self, _event: tk.Event) -> None:
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
        if self.playlist is None:
            return
        paths = filedialog.askopenfilenames(parent=self.root, title="Добавить композиции",
                                            filetypes=[("Музыка", ("*.wav", "*.mp3", "*.ogg")),
                                                       ("Все файлы", "*")])
        if paths:
            start = len(self.playlist)
            for path in paths:
                self.playlist.append(Composition(Path(path)))
            self._refresh(start)

    def remove(self) -> None:
        """Удаляет выбранную запись."""
        selection = self.tracks.curselection()
        if selection:
            index = selection[0]
            self._audio_action(lambda: self.playlist.remove(self.playlist[index]))
            self._refresh(index)

    def move(self, offset: int) -> None:
        """Перемещает выбранную запись на соседнюю позицию."""
        selection = self.tracks.curselection()
        if selection:
            index = selection[0]
            target = index + offset
            if 0 <= target < self.tracks.size():
                self.playlist.move(index, target)
                self._refresh(target)

    def _audio_action(self, action: Callable[[], None]) -> None:
        try:
            action()
        except OSError as exc:
            messagebox.showerror("Ошибка воспроизведения", str(exc), parent=self.root)
        self._status()

    def play_selected(self, _event: Optional[tk.Event] = None) -> None:
        """Запускает трек, выделенный в списке."""
        selection = self.tracks.curselection()
        if selection:
            self._audio_action(lambda: self.playlist.play_all(self.playlist[selection[0]]))

    def step(self, direction: int) -> None:
        """Переключает воспроизведение и выделяет текущую композицию."""
        playlist = self.playlist
        if playlist is not None:
            self._audio_action(playlist.next_track if direction > 0 else playlist.previous_track)
            for index, node in enumerate(playlist):
                if node.data is playlist.current:
                    self.tracks.selection_clear(0, tk.END)
                    self.tracks.selection_set(index)
                    self.tracks.see(index)
                    break

    def stop(self) -> None:
        """Завершает воспроизведение вручную."""
        if self.playlist is not None:
            self.playlist.stop()
            self._status()

    def _poll(self) -> None:
        if self.playlist is not None and self.playlist.current is not None and not audio.is_playing():
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
