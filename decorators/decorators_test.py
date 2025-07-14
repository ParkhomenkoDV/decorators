import time
from colorama import Fore, Back
import pytest

from decorators import logger, deprecated, timeit, enforce_kwargs


def test_logger(capsys):
    # Тестируемые функции с декоратором
    @logger
    def add(a: int, b: int) -> int:
        """Складывает два числа."""
        return a + b

    # Проверка вывода в консоль
    result = add(2, 3)
    captured = capsys.readouterr()
    assert captured.out == "add: start\nadd: end\n"
    assert result == 5

    # Проверка сохранения метаданных функции
    assert add.__name__ == "add"
    assert add.__doc__ == "Складывает два числа."
    assert add.__module__ == "decorators.decorators_test"

    @logger
    def mock_func():
        return 42

    # Проверка декоратора на функции без аргументов
    result = mock_func()
    captured = capsys.readouterr()
    assert result == 42
    assert captured.out == "mock_func: start\nmock_func: end\n"


def test_deprecated(capsys):
    test_message = "This function is deprecated"

    @deprecated(test_message)
    def test_func():
        return 42

    # Тест проверяет вывод сообщения об устаревании
    result = test_func()
    captured = capsys.readouterr()
    assert result == 42  # Проверяем, что функция работает
    assert test_message in captured.out  # Проверяем сообщение
    assert Back.RED in captured.out  # Проверяем цвет

    @deprecated("Some warning")
    def sample_func(x: int, y: int) -> int:
        """Sample function for testing"""
        return x + y

    # Тест проверяет сохранение метаданных функции
    assert sample_func.__name__ == "sample_func"
    assert sample_func.__doc__ == "Sample function for testing"
    assert sample_func.__annotations__ == {"x": int, "y": int, "return": int}

    # Тест проверяет, что декоратор вызывает ошибку при нестроковом сообщении
    with pytest.raises(AssertionError):

        @deprecated(123)  # type: ignore
        def bad_func():
            pass


def test_timeit(capsys):
    @timeit()
    def add(a, b):
        return a + b

    # Тест проверяет, что декорированная функция возвращает правильный результат
    result = add(2, 3)
    assert result == 5

    @timeit()
    def sample_func(x: int, y: int) -> int:
        """Sample function for testing"""
        return x + y

    # Тест проверяет сохранение метаданных функции
    assert sample_func.__name__ == "sample_func"
    assert sample_func.__doc__ == "Sample function for testing"
    assert sample_func.__annotations__ == {"x": int, "y": int, "return": int}

    @timeit(2)
    def fast_func():
        time.sleep(0.1)

    # Тест проверяет формат выводимого сообщения
    fast_func()
    captured = capsys.readouterr()
    assert "fast_func" in captured.out
    assert "elapsed" in captured.out
    assert "seconds" in captured.out
    assert Fore.YELLOW in captured.out and Fore.RESET in captured.out

    # Тест проверяет, что декоратор вызывает ошибку при нецелочисленном округлении
    with pytest.raises(AssertionError):

        @timeit("not an integer")  # type: ignore
        def bad_func():
            pass

    # Тест проверяет округление времени выполнения
    @timeit(2)
    def test_rounding():
        time.sleep(0.1234)

    test_rounding()
    captured = capsys.readouterr()
    # Проверяем, что время округлено до 2 знаков
    assert "0.12" in captured.out or "0.13" in captured.out  # Может немного колебаться

    # Тест проверяет, что декоратор действительно измеряет время
    sleep_time = 0.2

    @timeit(3)
    def slow_func():
        time.sleep(sleep_time)

    slow_func()
    captured = capsys.readouterr()
    # Извлекаем измеренное время из вывода
    time_str = captured.out.split("elapsed ")[1].split(" seconds")[0]
    # Проверяем, что измеренное время близко к ожидаемому
    assert pytest.approx(sleep_time, abs=0.05) == float(time_str)


def test_enforce_kwargs():
    # Тестируемые функции
    @enforce_kwargs
    def sample_func(a, b):
        return a + b

    @enforce_kwargs
    def no_args_func():
        return "no args"

    # Проверяет успешный вызов с kwargs
    assert sample_func(a=1, b=2) == 3

    # Проверяет, что позиционные аргументы вызывают ошибку
    with pytest.raises(TypeError) as excinfo:
        sample_func(1, 2)
    assert "requires only kwargs" in str(excinfo.value)
    assert "sample_func" in str(excinfo.value)

    # Проверяет, что смешанные args/kwargs вызывают ошибку
    with pytest.raises(TypeError):
        sample_func(1, b=2)

    # Проверяет работу с функцией без аргументов
    assert no_args_func() == "no args"

    @enforce_kwargs
    def empty_kwargs_func(**kwargs):
        return len(kwargs)

    # Проверяет работу с пустыми kwargs
    assert empty_kwargs_func() == 0

    # Проверяет сохранение метаданных функции
    assert sample_func.__name__ == "sample_func"
    assert no_args_func.__name__ == "no_args_func"

    @enforce_kwargs
    def func_with_defaults(x=1, y=2):
        return x * y

    # Проверяет работу с аргументами по умолчанию
    assert func_with_defaults() == 2
    assert func_with_defaults(x=3) == 6
    assert func_with_defaults(y=4) == 4
    assert func_with_defaults(x=3, y=3) == 9

    with pytest.raises(TypeError):
        func_with_defaults(3)
