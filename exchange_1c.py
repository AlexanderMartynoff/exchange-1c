import re
from datetime import datetime, date, time
from typing import Tuple, List, Any, Type, TypeVar, Generic
from itertools import zip_longest


V = TypeVar('V')
T = TypeVar('T', bound='String')


class String(Generic[V]):
    _re = re.compile(r'(.+?): (.+)')

    _sections: List[Tuple[str, str]] = [
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
        return f'{self._key!r}: {self._value!r}'

    def dump(self) -> str:
        return f'{self._key}: {self.dump_value()}'

    def dump_value(self) -> str:
        return str(self._value)

    @classmethod
    def load(cls: Type[T], string) -> T:
        match = cls._re.match(string)

        if match:
            return cls(match.group(1), match.group(2))

    @classmethod
    def is_section_start(cls, key) -> bool:
        return key in (k for (k, _) in cls._sections)

    @classmethod
    def is_section_end(cls, key) -> bool:
        return key in (k for (_, k) in cls._sections)


class Date(String[date]):
    _format = '%d.%m.%Y'
    _re = re.compile(r'(.+?): (\d{2}:\d{2}:\d{4})')

    def dump_value(self) -> str:
        return self._value.strftime(self._format)

    @classmethod
    def load(cls, string) -> 'Date':
        match = cls._re.match(string)

        if match:
            return cls(match.group(1), datetime.strptime(match.group(2), cls._format).date())


class Time(String[time]):
    _format = '%H:%M:%S'
    _re = re.compile(r'(.+?): (\d{2}:\d{2}:\d{2})')

    def dump_value(self) -> str:
        return self._value.strftime(self._format)

    @classmethod
    def load(cls, string) -> 'Time':
        match = cls._re.match(string)

        if match:
            return cls(match.group(1), datetime.strptime(match.group(2), cls._format).time())


class Token(String[bool]):
    _re = None

    def __init__(self, key, value=True):
        super().__init__(key, value)

    def dump(self) -> str:
        return self._key

    def __bool__(self) -> bool:
        return True

    @classmethod
    def load(cls, string) -> 'Token':
        return cls(string)


class Section:
    def __init__(self, *strings: String[Any]):
        self._strings = list(strings)

    @property
    def strings(self) -> List[String[Any]]:
        return self._strings

    def dump(self) -> str:
        return '\r\n'.join(value.dump() for value in self._strings if value)


class File:
    def __init__(self, *sections: Section):
        self._sections = list(sections)

    @property
    def sections(self) -> List[Section]:
        return self._sections

    def dumps(self):
        return '\r\n'.join(section.dump() for section in self._sections if section)


def dumps(file) -> str:
    return file.dumps()


def load(string: str) -> File:
    lines = string.split('\r\n')

    sections: List[Section] = []

    for line, next_line in zip_longest(lines, lines[1:]):
        value = None

        for cls in Token, Date, Time:
            if cls._re.match(line):
                value = cls.load(line)

        if value is None:
            value = String.load(line)

        if (not sections or
                String.is_section_start(value.key) or
                String.is_section_end(value.key) and not String.is_section_start(next_line)):
            sections.append(Section())

        sections[-1].strings.append(value)

    return File(*sections)
