import pytest

from decorators import logger


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
