import re
from datetime import date, time
from typing import Tuple, List, Any, Type, TypeVar, Generic
from itertools import zip_longest


V = TypeVar('V')
T = TypeVar('T', bound='Value')


class Value(Generic[V]):
    _re = r'(.+?): (.+)'

    _sections: List[Tuple[str, str]] = [
        ('1CClientBankExchange', 'КонецФайла'),
        ('СекцияРасчСчет', 'КонецРасчСчет'),
        ('СекцияДокумент', 'КонецДокумента'),
    ]

    def __init__(self, key: str, value: V):
        self._key = key
        self._value = value

    @property
    def key(self) -> str:
        return self._key

    @property
    def value(self) -> V:
        return self._value

    def __bool__(self) -> bool:
        return bool(self._value)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__} <{self._key}: {self._value!r}>'

    def dump(self) -> str:
        return f'{self._key}: {self.dump_value()}'

    def dump_value(self) -> str:
        raise NotImplementedError()

    @classmethod
    def load(cls: Type[T], string: str) -> T:
        match = re.fullmatch(cls._re, string)

        if not match:
            raise ValueError()

        return cls(match.group(1), cls.load_value(match.group(2)))

    @classmethod
    def load_value(cls, value: str) -> V:
        raise NotImplementedError()

    @classmethod
    def is_section_start(cls, key: str) -> bool:
        return key in (k for (k, _) in cls._sections)

    @classmethod
    def is_section_end(cls, key: str) -> bool:
        return key in (k for (_, k) in cls._sections)

    def __eq__(self, other: 'Value') -> bool:
        return self.key == other.key and self.value == other.value


class String(Value[str]):
    @classmethod
    def load_value(cls, string: str) -> str:
        return string

    def dump_value(self) -> str:
        return self._value


class Date(Value[date]):
    _date_format = r'%d.%m.%Y'
    _date_re = r'(\d{2})\.(\d{2})\.(\d{4})'

    def dump_value(self) -> str:
        return self._value.strftime(self._date_format)

    @classmethod
    def load_value(cls, string: str) -> date:
        match = re.fullmatch(cls._date_re, string)

        if not match:
            raise ValueError()

        return date(
            int(match.group(3)),
            int(match.group(2)),
            int(match.group(1)),
        )


class Time(Value[time]):
    _time_format = r'%H:%M:%S'
    _time_re = r'(\d{2}):(\d{2}):(\d{2})'

    def dump_value(self) -> str:
        return self._value.strftime(self._time_format)

    @classmethod
    def load_value(cls, string: str) -> time:
        match = re.fullmatch(cls._time_re, string)

        if not match:
            raise ValueError()

        return time(
            int(match.group(1)),
            int(match.group(2)),
            int(match.group(3)),
        )


class Token(Value[bool]):
    _re = r'\w+'

    def __init__(self, key, value=True):
        super().__init__(key, value)

    def dump(self) -> str:
        return self._key

    def __bool__(self) -> bool:
        return True

    @classmethod
    def load(cls, string: str) -> 'Token':
        match = re.fullmatch(cls._re, string)

        if not match:
            raise ValueError()

        return cls(string)

    @classmethod
    def load_value(cls, string) -> bool:
        return True


class Section:
    def __init__(self, *values: Value[Any]):
        self._values = list(values)

    @property
    def values(self) -> List[Value[Any]]:
        return self._values

    def dump(self) -> str:
        return '\r\n'.join(value.dump() for value in self._values if value)

    def __eq__(self, other: 'Section') -> bool:
        for index, value in enumerate(self.values):
            if value != other.values[index]:
                return False

        return True


class File:
    def __init__(self, *sections: Section):
        self._sections = list(sections)

    @property
    def sections(self) -> List[Section]:
        return self._sections

    def dump(self):
        return '\r\n'.join(section.dump() for section in self._sections if section)

    def __eq__(self, other: 'File') -> bool:
        for index, section in enumerate(self.sections):
            if section != other.sections[index]:
                return False

        return True


def dump(file: File) -> str:
    return file.dump()


def load(string: str) -> File:
    sections: List[Section] = []

    lines = string.strip('\r\n').split('\r\n')

    for line, next_line in zip_longest(lines, lines[1:]):
        value = None

        for cls in Token, Date, Time:
            try:
                value = cls.load(line)
            except ValueError:
                pass

        if value is None:
            value = String.load(line)

        if Value.is_section_start(value.key) or not sections:
            sections.append(Section())

        sections[-1].values.append(value)

        if Value.is_section_end(value.key) and next_line and not Value.is_section_start(next_line):
            sections.append(Section())

    return File(*sections)
