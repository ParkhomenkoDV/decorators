from functools import wraps, lru_cache, singledispatch
import logging
import warnings

# from memory_profiler import profile as memoryit  # готовый декоратор для замера использования памяти
from dataclasses import dataclass
import time

from colorama import Fore, Back

# https://nuancesprog.ru/p/17759/

"""
Декораторы Python - это эффективные инструменты, 
помогающие создавать чистый, многократно используемый и легко сопровождаемый код.

Можно считать декораторы функциями, 
которые принимают другие функции в качестве входных данных 
и расширяют их функциональность без изменения основного назначения.

Чтобы написать этот декоратор, нужно сначала подобрать ему подходящее имя.

Затем передать ему другую функцию в качестве входной и вернуть ее в качестве выходной. 
Выходная функция обычно является расширенной версией входной. 

Поскольку нам неизвестно, какие аргументы использует входная функция, 
можем передать их из функции-обертки с помощью выражений *args и **kwargs. 

Теперь можно применить декоторатор к любой другой функции,
прописав перед ее объявлением @ и имя декоратора.
"""

"""
Встроенный декоратор @wraps из functools обновляет функцию-обертку, 
чтобы она выглядела как оригинальная функция и наследовала ее имя и свойства, 
а не документацию и имя декоратора.
"""


def logger(function):
    """Регистрация начала и окончания выполнения функции"""

    @wraps(function)
    def wrapper(*args, **kwargs):
        """wrapper documentation"""
        print(f"{function.__name__}: start")
        result = function(*args, **kwargs)
        print(f"{function.__name__}: end")
        return result

    return wrapper


def deprecated(sms: str):
    """Вывод предупреждений"""

    assert isinstance(sms, str)

    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            print(Back.RED + sms + Back.RESET)
            return function(*args, **kwargs)

        return wrapper

    return decorator


def ignore_extra_kwargs(function):
    """Игнорирует лишние именные аргументы"""

    @wraps(function)
    def wrapper(*args, **kwargs):
        return function(
            *args,
            **{k: v for k, v in kwargs.items() if k in function.__code__.co_varnames},
        )

    return wrapper


def logs(level: str):
    """Обработка логов: ошибки и предупреждения, только ошибки,"""

    assert isinstance(level, str)
    level = level.strip().upper()

    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(__name__)
            if level == "NOTSET":
                logger.log(logging.NOTSET, "log")
                result = function(*args, **kwargs)
            elif level == "DEBUG":
                logger.log(logging.DEBUG, "log")
                result = function(*args, **kwargs)
            elif level == "INFO":
                logger.log(logging.INFO, "log")
                result = function(*args, **kwargs)
            elif level == "WARNING":
                logger.log(logging.WARNING, "log")
                result = function(*args, **kwargs)
            elif level == "ERROR":
                logger.log(logging.ERROR, "log")
                result = function(*args, **kwargs)
            elif level == "CRITICAL":
                logger.log(logging.CRITICAL, "log")
                result = function(*args, **kwargs)
            else:
                raise Exception(
                    f"level {level} not in {('NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')}"
                )
            logger.log(logging.NOTSET, "log")
            return result

        return wrapper

    return decorator


def warns(action: str):
    """Обработка предупреждений: пропуск (pass), игнорирование (ignore), исключение (error)"""

    assert isinstance(action, str)
    action = action.strip().lower()

    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            if action == "pass":
                result = function(*args, **kwargs)
            elif action == "ignore":
                warnings.filterwarnings("ignore")
                result = function(*args, **kwargs)
            elif action == "error":
                warnings.filterwarnings("error")
                result = function(*args, **kwargs)
            else:
                raise ValueError(
                    f"action {action} not in {('pass', 'ignore', 'error')}"
                )
            warnings.filterwarnings("default")
            return result

        return wrapper

    return decorator


def try_except(action: str = "pass"):
    """Обработка исключений"""

    assert type(action) is str, "type(action) is str"
    action = action.strip().lower()
    assert action in ("pass", "raise"), 'action in ("pass", "raise")'

    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except Exception as exception:
                if action == "raise":
                    raise exception
                else:
                    print(exception)

        return wrapper

    return decorator


def timeit(rnd: int = 4):
    """Измерение времени выполнения ф-и"""

    assert isinstance(rnd, int)

    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            tic = time.perf_counter()
            result = function(*args, **kwargs)
            tac = time.perf_counter()
            elapsed_time = tac - tic
            print(
                Fore.YELLOW
                + f'"{function.__name__}" elapsed {round(elapsed_time, rnd)} seconds'
                + Fore.RESET
            )
            return result

        return wrapper

    return decorator


def delay(t: int):
    """Задержка выполнения ф-и"""

    assert isinstance(t, int)

    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            time.sleep(t)
            result = function(*args, **kwargs)
            return result

        return wrapper

    return decorator


def cache(function):
    """Кэширование ф-и"""

    @wraps(function)
    def wrapper(*args, **kwargs):
        cache_key = args + tuple(kwargs.items())
        if cache_key in wrapper.cache:
            output = wrapper.cache[cache_key]
        else:
            output = function(*args)
            wrapper.cache[cache_key] = output
        return output

    wrapper.cache = dict()
    return wrapper


def countcall(function):
    """Подсчитывает количество вызовов функции"""

    @wraps(function)
    def wrapper(*args, **kwargs):
        wrapper.count += 1
        result = function(*args, **kwargs)
        print(f"{function.__name__} has been called {wrapper.count} times")
        return result

    wrapper.count = 0
    return wrapper


def repeat(repeats: int):
    """Вызов ф-и несколько раз подряд"""

    assert isinstance(repeats, int)

    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs) -> tuple:
            res = [None] * repeats
            for i in range(repeats):
                res[i] = function(*args, **kwargs)
            return tuple(res)

        return wrapper

    return decorator


def retry(retries: int, exception_to_check: Exception, sleep_time: int | float = 0):
    """Заставляет функцию, которая сталкивается с исключением, совершить несколько повторных попыток"""

    assert isinstance(retries, int) and retries >= 0
    assert isinstance(exception_to_check, Exception)
    assert isinstance(sleep_time, (int, float)) and sleep_time >= 0

    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            for i in range(1, retries + 1):
                try:
                    return function(*args, **kwargs)
                except exception_to_check as exception:
                    print(
                        f"{function.__name__} raised {exception.__class__.__name__}. Retrying..."
                    )
                    if i < retries:
                        time.sleep(sleep_time)
            # Инициирование исключения, если функция оказалось неуспешной после указанного количества повторных попыток
            raise Exception(f"func {function.__name__} ends fail in {retries} times")

        return wrapper

    return decorator


def rate_limited(frequency: int | float):
    """Ограничивает частоту вызова функции с частотой frequency в секунду"""

    assert isinstance(frequency, (int, float)) and frequency > 0
    min_interval = 1.0 / frequency

    def decorator(function):
        last_time_called = [0.0]

        @wraps(function)
        def wrapper(*args, **kwargs):
            elapsed = time.perf_counter() - last_time_called[0]
            left_to_wait = min_interval - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            ret = function(*args, **kwargs)
            last_time_called[0] = time.perf_counter()
            return ret

        return wrapper

    return decorator


def enforce_kwargs(function):
    """Требует передачу функции только через kwargs"""

    @wraps(function)
    def wrapper(*args, **kwargs):
        if args:
            raise TypeError(f"function {function.__name__} requires only kwargs")
        return function(**kwargs)

    return wrapper


"""
Встроенный декоратор @lru_cache из functools кэширует возвращаемые значения функции, 
используя при заполнении кэша алгоритм LRU - алгоритм замещения наименее часто используемых значений.

Применим этот декоратор для длительно выполняющихся задач, 
которые не меняют результат при одинаковых входных данных, 
например для запроса к базе данных, запроса статической удаленной веб-страницы и выполнения сложной обработки.
"""


def test():
    """Тестирование"""

    @repeat(3)
    @timeit()
    @lru_cache(maxsize=None)
    def heavy_processing(n, show=False):
        time.sleep(n)
        return "pip"

    class Movie:
        def __init__(self, r):
            self._rating = r

        """используется для определения свойств класса, 
        которые по сути являются методами getter, setter и deleter для атрибута экземпляра класса.
    
        Используя декоратор @property, можно определить метод как свойство класса и получить к нему доступ, 
        как к атрибуту класса, без явного вызова метода.
    
        Это полезно, если нужно добавить некоторые ограничения и логику проверки 
        в отношении получения и установки значения."""

        @property
        def rating(self):
            return self._rating

        @rating.setter
        def rating(self, r):
            if 0 <= r <= 5:
                self._rating = r
            else:
                raise ValueError("The movie rating must be between 0 and 5!")

    # позволяет функции иметь различные реализации для разных типов аргументов.
    @singledispatch
    def fun(arg):
        print("Called with a single argument")

    @fun.register(int)
    def _(arg):
        print("Called with an integer")

    @fun.register(list)
    def _(arg):
        print("Called with a list")

    @deprecated("Этой функции не будет в следующей версии!")
    def _foo(n):
        s = 0
        for i in range(n):
            s += n ** (0.5 + i)
        return s

    """
    Декоратор @dataclass в Python используется для декорирования классов.
    
    Он автоматически генерирует магические методы, 
    такие как __init__, __repr__, __eq__, __lt__ и __str__ для классов, 
    которые в основном хранят данные. 
    Это позволяет сократить объем кода и сделать классы более читаемыми и удобными для сопровождения.
    
    Он также предоставляет готовые методы для элегантного представления объектов, 
    преобразования их в формат JSON, обеспечения их неизменяемости и т.д.
    """

    @dataclass
    class Person:
        first_name: str
        last_name: str
        age: int
        job: str

        def __eq__(self, other):
            if isinstance(other, Person):
                return self.age == other.age
            return NotImplemented

        def __lt__(self, other):
            if isinstance(other, Person):
                return self.age < other.age
            return NotImplemented

    print(heavy_processing(2))
    heavy_processing(2)

    print(_foo(10))

    heavy_processing(3)
    batman = Movie(2.5)
    batman.rating

    fun(1)  # Выводит "Called with an integer"

    john = Person(
        first_name="John",
        last_name="Doe",
        age=30,
        job="doctor",
    )

    anne = Person(
        first_name="Anne",
        last_name="Smith",
        age=40,
        job="software engineer",
    )

    print(john == anne)


if __name__ == "__main__":
    import cProfile

    cProfile.run("test()", sort="cumtime")
