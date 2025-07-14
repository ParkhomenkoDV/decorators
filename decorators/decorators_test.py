from colorama import Back
import pytest

from decorators import logger, deprecated


def test_logger(capsys):
    # Тестируемые функции с декоратором
    @logger
    def add(a, b):
        """Складывает два числа."""
        return a + b

    @logger
    def mock_func():
        return 42

    # Проверка вывода в консоль
    result = add(2, 3)
    captured = capsys.readouterr()
    assert captured.out == "add: start\nadd: end\n"
    assert result == 5

    # Проверка декоратора на функции без аргументов
    result = mock_func()
    captured = capsys.readouterr()
    assert result == 42
    assert captured.out == "mock_func: start\nmock_func: end\n"

    # Проверка сохранения метаданных функции
    assert add.__name__ == "add"
    assert add.__doc__ == "Складывает два числа."
    assert add.__module__ == "decorators.decorators_test"


def test_deprecated(capsys):
    test_message = "This function is deprecated"

    @deprecated(test_message)
    def test_func():
        return 42

    @deprecated("Some warning")
    def sample_func(x: int, y: int) -> int:
        """Sample function for testing"""
        return x + y

    # Тест проверяет вывод сообщения об устаревании
    result = test_func()
    captured = capsys.readouterr()
    print(captured.out)
    assert result == 42  # Проверяем, что функция работает
    assert test_message in captured.out  # Проверяем сообщение
    assert Back.RED in captured.out  # Проверяем цвет

    # Тест проверяет сохранение метаданных функции
    assert sample_func.__name__ == "sample_func"
    assert sample_func.__doc__ == "Sample function for testing"
    assert sample_func.__annotations__ == {"x": int, "y": int, "return": int}

    # Тест проверяет, что декоратор вызывает ошибку при нестроковом сообщении
    with pytest.raises(AssertionError):

        @deprecated(123)  # type: ignore
        def bad_func():
            pass
