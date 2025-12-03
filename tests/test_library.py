import random

import pytest

from src.library import (
    BookCollection,
    DigitalBook,
    IndexDict,
    Library,
    PrintedBook,
    add_book_event,
    missing_lookup_event,
    random_book,
    refresh_index_event,
    remove_book_event,
    run_simulation,
    search_author_event,
    search_genre_event,
    search_year_event,
)


def make_printed_book(
    isbn: str,
    author: str = "Автор теста",
    year: int = 2000,
    genre: str = "жанр",
) -> PrintedBook:
    return PrintedBook(
        "Тестовая",
        author,
        year,
        genre,
        isbn,
        pages=150,
        cover_type="твердый переплет",
    )


def test_printed_book_binding_and_repr() -> None:
    book = make_printed_book("000")
    assert book.describe_binding() == "150 стр., твердый переплет"
    repr_str = repr(book)
    assert "Печатная Книга" in repr_str
    assert "стр=150" in repr_str


def test_digital_book_call_and_repr() -> None:
    digital = DigitalBook("Цифр", "Автор", 2023, "жанр", "111", "pdf", 3.25)
    assert digital("читалка") == "Открываю 'Цифр' на читалка как pdf"
    repr_str = repr(digital)
    assert "Цифровая Книга" in repr_str
    assert "3.25МБ" in repr_str


def test_book_collection_basic_operations() -> None:
    book_1 = make_printed_book("001")
    book_2 = make_printed_book("002")
    collection = BookCollection([book_1, book_2])
    assert len(collection) == 2
    assert book_1 in collection
    sliced = collection[:1]
    assert isinstance(sliced, BookCollection)
    assert len(sliced) == 1


def test_index_dict_author_and_year_lookup() -> None:
    book_1 = make_printed_book("010", author="Автор А", year=2001)
    book_2 = make_printed_book("020", author="Автор Б", year=2002)
    index = IndexDict()
    index.add(book_1)
    index.add(book_2)
    assert index[book_1.isbn] is book_1
    author_matches = index["author", book_1.author]
    assert len(author_matches) == 1
    assert book_1 in author_matches
    year_matches = index["year", book_2.year]
    assert book_2 in year_matches
    removed = index.remove(book_1.isbn)
    assert removed is book_1
    assert book_1.isbn not in index


def test_library_commons_and_index_refresh() -> None:
    library = Library()
    book = make_printed_book("123")
    library.add_book(book)
    assert library.get_by_isbn(book.isbn) is book
    assert book in library.find_by_author(book.author)
    library.remove_book(book.isbn)
    with pytest.raises(KeyError):
        library.get_by_isbn(book.isbn)
    # Обновление индексов не должно падать на пустой коллекции.
    library.refresh_indexes()


def test_event_messages_and_searches(capsys: pytest.CaptureFixture[str]) -> None:
    rng = random.Random(2)
    library = Library()
    add_book_event(library, rng)
    out = capsys.readouterr().out
    assert "[добавление]" in out
    remove_book_event(library, rng)
    out = capsys.readouterr().out
    assert "[удаление]" in out
    assert len(library.books) == 0
    remove_book_event(library, rng)
    out = capsys.readouterr().out
    assert "Библиотека пуста" in out
    add_book_event(library, rng)
    add_book_event(library, rng)
    search_author_event(library, rng)
    assert "[поиск-автора]" in capsys.readouterr().out
    search_year_event(library, rng)
    assert "[поиск-года]" in capsys.readouterr().out
    search_genre_event(library, rng)
    assert "[поиск-жанра]" in capsys.readouterr().out


def test_refresh_and_missing_lookup_events(capsys: pytest.CaptureFixture[str]) -> None:
    library = Library()
    refresh_index_event(library)
    assert "[переиндексация]" in capsys.readouterr().out
    missing_lookup_event(library, random.Random(4))
    assert "не найдена" in capsys.readouterr().out


def test_run_simulation_no_steps(capsys: pytest.CaptureFixture[str]) -> None:
    run_simulation(steps=0, seed=42)
    assert capsys.readouterr().out == ""


def test_random_book_generates_valid_entry() -> None:
    rng = random.Random(5)
    book = random_book(rng)
    assert book.isbn
    assert book.genre
