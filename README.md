[![Build Status](https://travis-ci.org/Nikolay-Lysenko/geniartor.svg?branch=master)](https://travis-ci.org/Nikolay-Lysenko/geniartor)
[![codecov](https://codecov.io/gh/Nikolay-Lysenko/geniartor/branch/master/graph/badge.svg)](https://codecov.io/gh/Nikolay-Lysenko/geniartor)
[![Maintainability](https://api.codeclimate.com/v1/badges/a5131738e1b284fab9f9/maintainability)](https://codeclimate.com/github/Nikolay-Lysenko/geniartor/maintainability)
[![PyPI version](https://badge.fury.io/py/geniartor.svg)](https://badge.fury.io/py/geniartor)

# Geniartor

## Overview

This is a configurable tool that generates musical phrases or even short pieces.

Here, the process of composition is framed as follows: Variable Neighborhood Search ([VNS](https://en.wikipedia.org/wiki/Variable_neighborhood_search)) is applied to maximize user-defined weighted sum of evaluational criteria. 

Each run of the tool results in creation of a directory that contains:
* MIDI file;
* WAV file;
* Events file in [sinethesizer](https://github.com/Nikolay-Lysenko/sinethesizer) TSV format;
* PDF file with sheet music and its Lilypond source.

Sample outputs produced by the tool are uploaded to a [cloud storage](https://www.dropbox.com/sh/j77p82870u3691p/AABGQWGRhA1pRyPfh79Lgdyma?dl=0).

## Installation

To install a stable version, run:
```bash
pip install geniartor
```

## Usage

To create a new musical phrase, run:
```bash
python -m geniartor \
    [-c path_to_config] \
    [-n number_of_search_passes]
```

Both arguments are optional. [Default config](https://github.com/Nikolay-Lysenko/geniartor/blob/master/geniartor/configs/default_config.yml) is used if `-c` argument is not passed. Similarly, `-n` option has a reasonable default too.

Advanced usage is covered in a [guide](https://github.com/Nikolay-Lysenko/geniartor/blob/master/docs/user_guide.md).
