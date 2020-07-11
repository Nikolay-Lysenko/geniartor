"""
Just a regular `setup.py` file.

Author: Nikolay Lysenko
"""


import os
from setuptools import setup, find_packages


current_dir = os.path.abspath(os.path.dirname(__file__))

description = 'Music composition by optimizing of evaluational scores.'
with open(os.path.join(current_dir, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='geniartor',
    version='0.1.0',
    description=description,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Nikolay-Lysenko/geniartor',
    author='Nikolay Lysenko',
    author_email='nikolay-lysenco@yandex.ru',
    license='MIT',
    keywords=[
        'ai_music',
        'algorithmic_composition',
        'generative_art',
    ],
    packages=find_packages(),
    package_data={
        'geniartor': [
            'configs/default_config.yml',
            'configs/sinethesizer_presets.yml'
        ]
    },
    python_requires='>=3.6',
    install_requires=[
        'pretty-midi',
        'PyYAML',
        'sinethesizer',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Artistic Software',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
    ]
)
