#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SYNOPSIS

	[python3] skeleton.py [-h,--help] [-v,--verbose] LANGUAGE SCRIPT_NAME[.py|.sh]


DESCRIPTION

	Create a skeleton script for a given language, automatically filled with
	useful tools.


ARGUMENTS

	-h, --help		show this help message and exit
	LANGUAGE			specify the script's language, to be placed as the shebang
								current options: python, python3, bash

	SCRIPT_NAME		the name of the script to be created

AUTHOR

	Doug McGeehan <djmvfb@mst.edu>


LICENSE

	Copyright 2017 Doug McGeehan, licensed under the GNU GPLv3.

"""
import os

__appname__ = "skeleton"
__author__ = "Doug McGeehan <djmvfb@mst.edu>"
__version__ = "0.0pre0"
__license__ = "GNU GPLv3"

import argparse
from datetime import datetime
import sys
import logging

logger = logging.getLogger(__appname__)


class BaseSkeletonBuilder(object):
    def __init__(self, name, store_in):
        self.name = name
        logger.debug('Script name: {}'.format(name))
        logger.debug('Directory: {}'.format(store_in))


# TODO: implement deprecation warning using the warnings class
class Python2SkeletonBuilder(BaseSkeletonBuilder):
    pass


class Python3SkeletonBuilder(BaseSkeletonBuilder):
    pass


class BashSkeletonBuilder(BaseSkeletonBuilder):
    pass


builders = {
    'python': Python3SkeletonBuilder,
    'python3': Python3SkeletonBuilder,
    'python2': Python2SkeletonBuilder,
    'bash': BashSkeletonBuilder,
}

def script_factory(name, language, store_in=None):
    builder_class = builders[language]
    builder = builder_class(name=name, store_in=store_in)
    return '/path/to/script'


def main(args):
    directory = os.path.abspath(os.path.dirname(args.script_path))
    filename = os.path.basename(args.script_path)
    script_path = script_factory(name=filename, store_in=directory,
                                 language=args.language)
    logger.info('{0} script output to "{1}"'.format(args.language, script_path))


def setup_logger(args):
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    # todo: place them in a log directory, or add the time to the log's
    # filename, or append to pre-existing log
    fh = logging.FileHandler(__appname__ + ".log")
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()

    if args.verbose:
        ch.setLevel(logging.DEBUG)
    else:
        ch.setLevel(logging.INFO)

    # create formatter and add it to the handlers
    fh.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    ch.setFormatter(logging.Formatter(
        '%(message)s'
    ))
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)


def get_arguments():
    parser = argparse.ArgumentParser(
        description="Description printed to command-line if -h is called."
    )
    # during development, I set default to False so I don't have to keep
    # calling this with -v
    parser.add_argument('-v', '--verbose', action='store_true',
                        default=False, help='verbose output')

    parser.add_argument('script_path', metavar='SCRIPT_PATH',
                        help="specify the script's path")

    parser.add_argument('language', metavar='LANGUAGE',
                        help="specify the script's language: python, python3, bash")

    return parser.parse_args()


if __name__ == '__main__':
    try:
        start_time = datetime.now()

        args = get_arguments()
        setup_logger(args)
        logger.debug(start_time)

        main(args)

        finish_time = datetime.now()
        logger.debug(finish_time)
        logger.debug('Execution time: {time}'.format(
            time=(finish_time - start_time)
        ))
        logger.debug("#" * 20 + " END EXECUTION " + "#" * 20)

        sys.exit(0)

    except KeyboardInterrupt as e:  # Ctrl-C
        raise e

    except SystemExit as e:  # sys.exit()
        raise e

    except Exception as e:
        logger.exception("Something happened and I don't know what to do D:")
        sys.exit(1)
