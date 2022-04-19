#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [ ]

test_requirements = [ ]

setup(
    author="Iqui Balam Heredia Marin",
    author_email='iquibalamhm@gmail.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Python Algebra process the video image and sends a message to Ubuntu",
    entry_points={
        'console_scripts': [
            'python_algebra=python_algebra.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='python_algebra',
    name='python_algebra',
    packages=find_packages(include=['python_algebra', 'python_algebra.*']),
    package_data={'python_algebra':['*.py']},
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/iquibalamhm/python_algebra',
    version='0.1.0',
    zip_safe=False,
)
