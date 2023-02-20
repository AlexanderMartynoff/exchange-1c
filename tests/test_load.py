from datetime import date, time
from exchange_1c import load, File, Section, Token, String, Date, Time


def test_load():
    assert load(
            '1CClientBankExchange\r\n'
            'СекцияРасчСчет\r\n'
            'Номер: 0\r\n'
            'КвитанцияДата: 01.01.1970\r\n'
            'КвитанцияВремя: 01:01:01\r\n'
            'КонецРасчСчет\r\n'
            'КонецФайла\r\n'
        ) == File(
            Section(
                Token('1CClientBankExchange'),
            ),
            Section(
                Token('СекцияРасчСчет'),
                String('Номер', '0'),
                Date('КвитанцияДата', date(1970, 1, 1)),
                Time('КвитанцияВремя', time(1, 1, 1)),
                Token('КонецРасчСчет'),
            ),
            Section(
                Token('КонецФайла'),
            ),
        )
