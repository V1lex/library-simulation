CASE = 1

import random
from src.library import (
    run_simulation, Library, PrintedBook, BookCollection,
    add_book_event, remove_book_event, search_year_event, search_genre_event
)

def case_1():
    run_simulation(steps=1, seed=42)

def case_2():
    library = Library()
    library.add_book(PrintedBook("Тест", "Автор", 2000, "роман", "ISBN-1", pages=100))
    result = library.find_by_genre("роман")
    print("Найдено:", len(result))

def case_3():
    rng = random.Random(1)
    library = Library()
    remove_book_event(library, rng)

def case_4():
    c1 = BookCollection()
    c2 = BookCollection()
    c1.add(PrintedBook("A", "Автор", 2000, "роман", "ISBN-A", pages=100))
    print("len(c1) =", len(c1))
    print("len(c2) =", len(c2))
    print("same_storage =", c1.books is c2.books)

def case_5():
    rng = random.Random(17)
    library = Library()
    add_book_event(library, rng)
    search_year_event(library, rng)
    search_genre_event(library, rng)

cases = {1: case_1, 2: case_2, 3: case_3, 4: case_4, 5: case_5}
cases[CASE]()