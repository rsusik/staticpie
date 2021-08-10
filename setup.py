import io
from setuptools import setup, find_packages
from pie.pie import __version__


def get_requirements():
    with open('requirements.txt') as fp:
        return [req for req in (line.strip() for line in fp) if req and not req.startswith('#')]


setup(
    name='staticpie',
    version=__version__,
    author='Robert Susik',
    author_email='robert.susik@gmail.com',
    options={'bdist_wheel': {'universal': True}},    
    license='GPLv3',
    description=(
        '''Simple and extensible static site generator written in Python.'''
    ),
    long_description=io.open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'pie=pie.pie:main',
        ],
    },
    package_data={'': ['assets/*', 'assets/*/*', 'assets/*/*/*', 'assets/*/*/*/*', 'assets/*/*/*/*/*', 'assets/*/*/*/*/*/*']},
    install_requires=get_requirements(),
    package_dir={'': '.'},
    packages=find_packages(where='.'),
    url='https://github.com/rsusik/staticpie',
    classifiers=[
        'Topic :: Utilities',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Text Processing :: Markup :: Markdown',
        'Topic :: Text Processing :: Markup :: HTML'
    ],
)
