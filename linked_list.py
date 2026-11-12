"""Кольцевой двусвязный список с конечным обходом в обе стороны."""

from __future__ import annotations

from typing import Generic, Iterator, Optional, TypeVar

T = TypeVar("T")


class LinkedListItem(Generic[T]):
    """Узел с данными и взаимными ссылками на соседей."""

    def __init__(self, data: T = None) -> None:
        self.data = data
        self._next: Optional[LinkedListItem[T]] = None
        self._previous: Optional[LinkedListItem[T]] = None

    @property
    def next_item(self) -> Optional[LinkedListItem[T]]:
        """Сосед справа."""
        return self._next

    @next_item.setter
    def next_item(self, value: Optional[LinkedListItem[T]]) -> None:
        # Соседние узлы одного класса обновляются без рекурсивных вызовов сеттеров.
        # pylint: disable=protected-access
        if self._next is not None:
            self._next._previous = None
        self._next = value
        if value is not None:
            if value._previous is not None:
                value._previous._next = None
            value._previous = self

    @property
    def previous_item(self) -> Optional[LinkedListItem[T]]:
        """Сосед слева."""
        return self._previous

    @previous_item.setter
    def previous_item(self, value: Optional[LinkedListItem[T]]) -> None:
        if value is not None:
            value.next_item = self
        elif self._previous is not None:
            self._previous.next_item = None

    def __repr__(self) -> str:
        return f"LinkedListItem({self.data!r})"


class LinkedList(Generic[T]):
    """Список хранит начало кольца и принимает уже связанные узлы."""

    def __init__(self, first_item: Optional[LinkedListItem[T]] = None) -> None:
        self.first_item = first_item
        self._cursor: Optional[Iterator[LinkedListItem[T]]] = None
        if first_item is not None and first_item.next_item is None:
            first_item.next_item = first_item

    @property
    def last(self) -> Optional[LinkedListItem[T]]:
        """Последний узел или None для пустого списка."""
        return self.first_item.previous_item if self.first_item is not None else None

    def __iter__(self) -> Iterator[LinkedListItem[T]]:
        node = self.first_item
        while node is not None:
            yield node
            node = node.next_item
            if node is self.first_item:
                break

    def __next__(self) -> LinkedListItem[T]:
        if self._cursor is None:
            self._cursor = iter(self)
        return next(self._cursor)

    def __reversed__(self) -> Iterator[T]:
        node = self.last
        while node is not None:
            yield node.data
            if node is self.first_item:
                break
            node = node.previous_item

    def __len__(self) -> int:
        return sum(1 for _ in self)

    def node_at(self, index: int) -> LinkedListItem[T]:
        """Находит узел по позиции, включая отрицательные индексы."""
        if index < 0:
            index += len(self)
        for position, node in enumerate(self):
            if position == index:
                return node
        raise IndexError("Индекс за пределами списка")

    def __getitem__(self, index: int) -> T:
        return self.node_at(index).data

    def __contains__(self, item: object) -> bool:
        return any(node.data == item for node in self)

    def _find(self, item: T) -> LinkedListItem[T]:
        for node in self:
            if node.data == item:
                return node
        raise ValueError("Элемент отсутствует в списке")

    def _insert_after(self, previous: Optional[LinkedListItem[T]], node: LinkedListItem[T]) -> None:
        """Вставляет свободный узел, замыкая разорванные связи."""
        if previous is None:
            node.next_item = node
            self.first_item = node
        else:
            successor = previous.next_item
            previous.next_item = node
            node.next_item = successor
        self._cursor = None

    def append_left(self, item: T) -> None:
        """Добавляет значение в начало."""
        node = LinkedListItem(item)
        self._insert_after(self.last, node)
        self.first_item = node

    def append_right(self, item: T) -> None:
        """Добавляет значение в конец."""
        self._insert_after(self.last, LinkedListItem(item))

    append = append_right

    def insert(self, previous: T, item: T) -> None:
        """Вставляет значение после первого совпадения previous."""
        self._insert_after(self._find(previous), LinkedListItem(item))

    def _detach(self, node: LinkedListItem[T]) -> None:
        """Отсоединяет узел, сохраняя кольцо у оставшихся элементов."""
        if node.next_item is node:
            self.first_item = None
            node.next_item = None
        else:
            if self.first_item is node:
                self.first_item = node.next_item
            node.previous_item.next_item = node.next_item
        self._cursor = None

    def remove(self, item: T) -> None:
        """Удаляет первое совпадение или возбуждает ValueError."""
        self._detach(self._find(item))
