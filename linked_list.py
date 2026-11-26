"""Кольцевой двусвязный список с конечным обходом в обе стороны."""

from __future__ import annotations

import operator
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
        for node in self:
            if node.next_item is None:
                node.next_item = first_item

    @property
    def last(self) -> Optional[LinkedListItem[T]]:
        """Последний узел или None для пустого списка."""
        return self.first_item.previous_item if self.first_item is not None else None

    def __iter__(self) -> Iterator[LinkedListItem[T]]:
        """Перебирает узлы от первого до последнего."""
        node = self.first_item
        while node is not None:
            yield node
            node = node.next_item
            if node is self.first_item:
                break

    def __next__(self) -> LinkedListItem[T]:
        """Возвращает следующий узел при вызове next() для списка."""
        if self._cursor is None:
            self._cursor = iter(self)
        return next(self._cursor)

    def __reversed__(self) -> Iterator[T]:
        """Перебирает значения от последнего до первого."""
        node = self.last
        while node is not None:
            yield node.data
            if node is self.first_item:
                break
            node = node.previous_item

    def values(self) -> Iterator[T]:
        """Перебирает значения в прямом порядке."""
        return (node.data for node in self)

    def __len__(self) -> int:
        """Возвращает количество узлов в списке."""
        return sum(1 for _ in self)

    def node_at(self, index: int) -> LinkedListItem[T]:
        """Возвращает узел по индексу."""
        index = operator.index(index)
        if index < 0:
            index += len(self)
        for position, node in enumerate(self):
            if position == index:
                return node
        raise IndexError("Индекс за пределами списка")

    def __getitem__(self, index: int) -> T:
        """Возвращает значение по индексу."""
        return self.node_at(index).data

    def __contains__(self, item: object) -> bool:
        """Проверяет, есть ли значение в списке."""
        return any(value == item for value in self.values())

    def _find(self, item: T) -> LinkedListItem[T]:
        """Возвращает первый узел с указанным значением."""
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
        successor = node.next_item
        if successor is node:
            self.first_item = None
            node.next_item = None
        else:
            if self.first_item is node:
                self.first_item = successor
            node.previous_item.next_item = successor
        self._cursor = None

    def remove(self, item: T) -> None:
        """Удаляет первое совпадение или возбуждает ValueError."""
        self._detach(self._find(item))

    def move(self, source: int, target: int) -> None:
        """Перемещает узел на указанный индекс."""
        positions = range(len(self))
        source = positions[source]
        target = positions[target]
        if source == target:
            return

        node = self.node_at(source)
        self._detach(node)
        if target == 0:
            self._insert_after(self.last, node)
            self.first_item = node
        else:
            self._insert_after(self.node_at(target - 1), node)
