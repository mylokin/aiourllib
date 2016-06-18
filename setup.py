import re
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = ''

with open('aiourllib/__init__.py', 'r') as fd:
    regex = re.compile(r'__version__\s*=\s*[\'"]([^\'"]*)[\'"]')
    for line in fd:
        m = regex.match(line)
        if m:
            version = m.group(1)
            break

setup(
    name='aiourllib',
    packages=['aiourllib'],
    package_data={'': ['LICENSE']},
    version=version,
    description='HTTP library for asyncio',
    author='Andrey Gubarev',
    author_email='mylokin@me.com',
    url='https://github.com/mylokin/aiourllib',
    keywords=['http',],
    license='MIT',
    platforms='any',
    install_requires=[],
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ),
)
