import random
from dataclasses import dataclass
from typing import Iterable, Iterator, Tuple, overload


@dataclass(frozen=True, slots=True)   # frozen - нельзя менять поля после создания; slots - меньше памяти, фиксированный набор атрибутов
class Book:
    """Представляет типовую книгу в каталоге."""

    title: str
    author: str
    year: int
    genre: str
    isbn: str

    def __contains__(self, keyword: str) -> bool:
        """Проверяет, присутствует ли ключевое слово в названии или имени автора."""
        normalized = keyword.lower()
        return normalized in self.title.lower() or normalized in self.author.lower()

    def short(self) -> str:
        return f"{self.title} ({self.year})"


@dataclass(frozen=True, slots=True)
class PrintedBook(Book):
    """Физическая книга с количеством страниц и типом переплета."""

    pages: int
    cover_type: str = "мягкий переплет"

    def describe_binding(self) -> str:
        return f"{self.pages} стр., {self.cover_type}"

    def __repr__(self) -> str:
        return (
            f"Печатная Книга({self.title!r}, {self.author!r}, {self.year}, "
            f"{self.genre!r}, {self.isbn}, стр={self.pages})"
        )


@dataclass(frozen=True, slots=True)
class DigitalBook(Book):
    """Электронная книга, которую можно вызвать для имитации открытия на устройстве."""

    file_format: str = "epub"
    file_size_mb: float = 1.5

    def __call__(self, device: str) -> str:
        return f"Открываю '{self.title}' на {device} как {self.file_format}"

    def __repr__(self) -> str:
        return (
            f"Цифровая Книга({self.title!r}, {self.author!r}, {self.year}, "
            f"{self.genre!r}, {self.isbn}, {self.file_format}, {self.file_size_mb}МБ)"
        )


class BookCollection:
    """Списокоподобная коллекция, сохраняющая порядок книг."""

    def __init__(self, books: Iterable[Book] | None = None) -> None:
        self.books: list[Book] = list(books) if books else []

    def __iter__(self) -> Iterator[Book]:
        return iter(self.books)

    def __len__(self) -> int:
        return len(self.books)

    @overload
    def __getitem__(self, index: int) -> Book: ...

    @overload
    def __getitem__(self, index: slice) -> "BookCollection": ...

    def __getitem__(self, index: int | slice) -> Book | "BookCollection":
        result = self.books[index]
        if isinstance(index, slice):
            return BookCollection(result)
        return result

    def __contains__(self, book_or_isbn: Book | str) -> bool:
        isbn = book_or_isbn.isbn if isinstance(book_or_isbn, Book) else book_or_isbn
        return any(book.isbn == isbn for book in self.books)

    def __add__(self, other: "BookCollection") -> "BookCollection":
        """Объединяет две коллекции без дублирования ISBN."""
        combined = BookCollection(self.books)
        for book in other:
            if book not in combined:
                combined.add(book)
        return combined

    def add(self, book: Book) -> None:
        self.books.append(book)

    def extend(self, books: Iterable[Book]) -> None:
        for book in books:
            self.add(book)

    def remove(self, book_or_isbn: Book | str) -> Book:
        """Удаляет книгу по экземпляру или ISBN и возвращает удаленную книгу."""
        isbn = book_or_isbn.isbn if isinstance(book_or_isbn, Book) else book_or_isbn
        for idx, candidate in enumerate(self.books):
            if candidate.isbn == isbn:
                return self.books.pop(idx)
        raise KeyError(f"Книга с ISBN {isbn} не найдена")

    def pop_random(self, rng: random.Random) -> Book:
        if not self.books:
            raise IndexError("Невозможно взять случайную книгу из пустой коллекции")
        index = rng.randrange(len(self.books))
        return self.books.pop(index)

    def snapshot(self) -> list[Book]:
        """Возвращает неглубокую копию внутреннего хранилища."""
        return list(self.books)


class IndexDict:
    """Словарная структура, поддерживающая индексы для книг."""

    def __init__(self) -> None:
        self.by_isbn: dict[str, Book] = {}
        self.by_author: dict[str, set[Book]] = {}
        self.by_year: dict[int, set[Book]] = {}

    def __len__(self) -> int:
        return len(self.by_isbn)

    def __iter__(self) -> Iterator[Tuple[str, Book]]:
        return iter(self.by_isbn.items())

    def __getitem__(self, key: str | tuple[str, str | int]) -> Book | BookCollection:
        if isinstance(key, tuple):
            field, value = key
            normalized_field = field.lower()
            if normalized_field == "author":
                return self.get_by_author(str(value))
            if normalized_field == "year":
                return self.get_by_year(int(value))
            raise KeyError(f"Неподдерживаемое поле индекса '{field}'")
        return self.by_isbn[key]

    def __contains__(self, key: Book | str) -> bool:
        isbn = key.isbn if isinstance(key, Book) else key
        return isbn in self.by_isbn

    def add(self, book: Book) -> None:
        self.by_isbn[book.isbn] = book
        self.by_author.setdefault(book.author.lower(), set()).add(book)
        self.by_year.setdefault(book.year, set()).add(book)

    def remove(self, book_or_isbn: Book | str) -> Book:
        isbn = book_or_isbn.isbn if isinstance(book_or_isbn, Book) else book_or_isbn
        book = self.by_isbn.pop(isbn)

        authors = self.by_author.get(book.author.lower())
        if authors is not None:
            authors.discard(book)
            if not authors:
                self.by_author.pop(book.author.lower(), None)

        years = self.by_year.get(book.year)
        if years is not None:
            years.discard(book)
            if not years:
                self.by_year.pop(book.year, None)

        return book

    def get_by_author(self, author: str) -> BookCollection:
        return BookCollection(self.by_author.get(author.lower(), ()))

    def get_by_year(self, year: int) -> BookCollection:
        return BookCollection(self.by_year.get(year, ()))

    def rebuild(self, books: Iterable[Book]) -> None:
        self.by_isbn.clear()
        self.by_author.clear()
        self.by_year.clear()
        for book in books:
            self.add(book)


class Library:
    """Библиотека объединяет коллекции и предоставляет вспомогательные методы поиска."""

    def __init__(self, books: Iterable[Book] | None = None) -> None:
        self.books = BookCollection(books)
        self.indexes = IndexDict()
        self.indexes.rebuild(self.books)

    def add_book(self, book: Book) -> None:
        self.books.add(book)
        self.indexes.add(book)

    def remove_book(self, isbn: str) -> Book:
        removed = self.books.remove(isbn)
        self.indexes.remove(isbn)
        return removed

    def remove_random(self, rng: random.Random) -> Book:
        removed = self.books.pop_random(rng)
        self.indexes.remove(removed)
        return removed

    def refresh_indexes(self) -> None:
        self.indexes.rebuild(self.books)

    def find_by_author(self, author: str) -> BookCollection:
        return self.indexes.get_by_author(author)

    def find_by_year(self, year: int) -> BookCollection:
        return self.indexes.get_by_year(year)

    def find_by_genre(self, genre: str) -> BookCollection:
        return BookCollection(
            book for book in self.books if book.genre.lower() == genre.lower()
        )

    def get_by_isbn(self, isbn: str) -> Book:
        return self.indexes[isbn]


TITLES = [
    "Война и мир",
    "Преступление и наказание",
    "Тихий Дон",
    "Мастер и Маргарита",
    "Евгений Онегин",
]

AUTHORS = [
    "Лев Толстой",
    "Федор Достоевский",
    "Михаил Шолохов",
    "Михаил Булгаков",
    "Александр Пушкин",
]

GENRES = ["роман", "история", "классика", "фантастика", "детектив"]


def random_isbn(rng: random.Random) -> str:
    """Генерирует псевдо-строку ISBN-13."""
    return f"{rng.randint(100, 999)}-{rng.randint(1000000000000, 9999999999999)}"


def random_book(rng: random.Random) -> Book:
    """Создает печатную или цифровую книгу со случайными параметрами."""
    title = rng.choice(TITLES)
    author = rng.choice(AUTHORS)
    genre = rng.choice(GENRES)
    year = rng.randint(1980, 2024)
    isbn = random_isbn(rng)

    if rng.random() < 0.5:
        pages = rng.randint(120, 720)
        cover_type = rng.choice(["мягкий переплет", "твердый переплет"])
        return PrintedBook(title, author, year, genre, isbn, pages, cover_type)

    file_format = rng.choice(["epub", "pdf", "mobi"])
    file_size = round(rng.uniform(0.8, 15.0), 2)
    return DigitalBook(title, author, year, genre, isbn, file_format, file_size)


def add_book_event(library: Library, rng: random.Random) -> None:
    candidate = random_book(rng)
    while candidate.isbn in library.indexes:
        candidate = random_book(rng)
    library.add_book(candidate)
    print(f"[добавление] Сохранена {candidate.short()} от {candidate.author} [{candidate.isbn}]")


def remove_book_event(library: Library, rng: random.Random) -> None:
    if len(library.books) == 0:
        print("[удаление] Библиотека пуста, нечего удалять")
        return
    removed = library.remove_random(rng)
    print(f"[удаление] Удалена {removed.short()} [{removed.isbn}]")


def search_author_event(library: Library, rng: random.Random) -> None:
    author = rng.choice(AUTHORS)
    matches = library.find_by_author(author)
    titles = ", ".join(book.short() for book in matches) or "нет совпадений"
    print(f"[поиск-автора] {author}: {titles}")


def search_year_event(library: Library, rng: random.Random) -> None:
    year = rng.randint(1980, 2024)
    matches = library.find_by_year(year)
    print(f"[поиск-года] {year}: найдено {len(matches)} книг")


def search_genre_event(library: Library, rng: random.Random) -> None:
    genre = rng.choice(GENRES)
    matches = library.find_by_genre(genre)
    sample = matches[:3]
    titles = ", ".join(book.short() for book in sample) or "нет совпадений"
    print(f"[поиск-жанра] {genre}: {len(matches)} книг -> {titles}")


def refresh_index_event(library: Library) -> None:
    library.refresh_indexes()
    print(f"[переиндексация] Перестроены индексы для {len(library.indexes)} книг")


def missing_lookup_event(library: Library, rng: random.Random) -> None:
    fake_isbn = random_isbn(rng)
    try:
        library.get_by_isbn(fake_isbn)
        print(f"[поиск] Неожиданно найдена книга с ISBN {fake_isbn}")
    except KeyError:
        print(f"[поиск] Книга с ISBN {fake_isbn} не найдена, обработано без ошибок")


def run_simulation(steps: int = 20, seed: int | None = None) -> None:
    """Запускает псевдослучайную симуляцию библиотеки."""
    rng = random.Random(seed)
    library = Library()

    events = (
        lambda: add_book_event(library, rng),
        lambda: remove_book_event(library, rng),
        lambda: search_author_event(library, rng),
        lambda: search_year_event(library, rng),
        lambda: search_genre_event(library, rng),
        lambda: refresh_index_event(library),
        lambda: missing_lookup_event(library, rng),
    )

    for step in range(1, steps + 1):
        event = rng.choice(events)
        print(f"\nШаг {step}")
        event()
