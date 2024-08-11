from setuptools import setup

setup(
    name='nape-eval',
    version='1.0.0',
    py_modules=['main'],
    entry_points='''
        [console_scripts]
        nape-eval=main:main
    ''',
)