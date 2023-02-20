from datetime import datetime
from exchange_1c import load, File, Section, Token, String, Date, Time


def test_load_string():
    assert load(
            '1CClientBankExchange\r\n'
            'Номер: 0\r\n'
            'КвитанцияДата: 01.01.1970\r\n'
            'КвитанцияВремя: 01:01:01\r\n'
            'КонецФайла'
        ) == File(
            Section(
                Token('1CClientBankExchange'),
            ),
            Section(
                String('Номер', '0'),
                Date('КвитанцияДата', datetime(1970, 1, 1)),
                Time('КвитанцияВремя', datetime(1970, 1, 1, 1, 1, 1)),
            ),
            Section(
                Token('КонецФайла'),
            ),
        )
