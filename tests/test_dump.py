from datetime import date, time
from exchange_1c import dump, File, Section, Token, String, Date, Time


def test_dump_token():
    file = dump(
        File(
            Section(
                Token('1CClientBankExchange'),
            ),
        )
    )

    assert file == '1CClientBankExchange'


def test_dump_string():
    file = dump(
        File(
            Section(
                String('Номер', '0'),
            ),
        )
    )

    assert file == 'Номер: 0'


def test_dump_date():
    file = dump(
        File(
            Section(
                Date('КвитанцияДата', date(1970, 1, 1)),
            ),
        )
    )

    assert file == 'КвитанцияДата: 01.01.1970'


def test_dump_time():
    file = dump(
        File(
            Section(
                Time('КвитанцияВремя', time(1, 1, 1)),
            ),
        )
    )

    assert file == 'КвитанцияВремя: 01:01:01'


def test_dump_file():
    file = dump(
        File(
            Section(
                Token('1CClientBankExchange'),
            ),
            Section(
                String('Номер', '0'),
                Date('КвитанцияДата', date(1970, 1, 1)),
                Time('КвитанцияВремя', time(1, 1, 1)),
            ),
            Section(
                Token('КонецФайла'),
            ),
        )
    )

    assert file == (
        '1CClientBankExchange\r\n'
        'Номер: 0\r\n'
        'КвитанцияДата: 01.01.1970\r\n'
        'КвитанцияВремя: 01:01:01\r\n'
        'КонецФайла'
    )
