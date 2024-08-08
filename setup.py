from setuptools import setup

setup(
    name='nape-eval',
    version='1.0.0',
    py_modules=['main'],
    install_requires=[
        # Add your dependencies here
    ],
    entry_points='''
        [console_scripts]
        nape-eval=main:main
    ''',
)