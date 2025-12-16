### Ошибка 1 - ошибка границы цикла (off-by-one)
Место: src/library.py, функция run_simulation

Симптом:
При запуске симуляции с steps=1 не выполняется ни одного шага (лог пустой).

Как воспроизвести:
Запустить:
`python -c "from src.library import run_simulation; run_simulation(steps=1, seed=42)"`


Отладка:
Установлен breakpoint на строке цикла `for step in range(1, steps):`.
В отладчике видно, что `steps = 1`, а диапазон `range(1, steps)` превращается в `range(1, 1)` (пустой), поэтому тело цикла не выполняется.
Call Stack показывает остановку в `run_simulation` (вызов из debug_run.py).

Причина:
Неверная граница диапазона: используется `range(1, steps)`, который не включает последний шаг.

Исправление:
Заменено на:
`for step in range(1, steps + 1):`

Проверка:
Повторный запуск с `steps=1` выводит `Шаг 1` и выполняет событие.

Доказательства:

**Точка останова в цикле симуляции:**

![Breakpoint](assets/lab5/bug1_breakpoint_loop.png)

**Кадр стека и значения локальных переменных:**

![Call Stack и Locals](assets/lab5/bug1_callstack_and_locals.png)
