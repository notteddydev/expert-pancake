from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'A Python package for organising files by classifying them as either photo, video, recording, or document.'
LONG_DESCRIPTION = 'Classifies files by either photo, video, recording, or document, and stores them in corresponding directories. e.g. photos/"1987-12-31 23.59.01.jpg".'

setup(
    name="expertpancake",
    version=VERSION,
    author="notteddydev",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'expertpancake']
)