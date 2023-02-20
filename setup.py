from setuptools import setup


setup(
    name='exchange-1c',
    version='0.0.1',
    extras_require={
        'dev': [
            'pytest==7.2.1',
        ],
    },
    py_modules=['exchange_1c'],
)
