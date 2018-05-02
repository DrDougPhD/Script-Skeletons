#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import os
from datetime import datetime
import logging
from io import TextIOWrapper
import colorlog
import sys


def prepare(app, args):
    return CommandLineInterface(app=app, args=args)


def add_subcommands(subcmd_modules, parser):
    subparsers = parser.add_subparsers(dest='subcommand')
    for module in subcmd_modules:
        subcommand = subparsers.add_parser(
            name=module.__name__.split('.')[-1],
            help=module.__doc__ or '',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
        module.cli(subcommand)


class CommandLineInterface(object):
    def __init__(self, app, args):
        self.app = app
        self.start_time = datetime.now()

        self.cli_arguments = args
        self.log = logging.getLogger(app)

    def __enter__(self):
        self.setup_logger()

        # figure out which argument key is the longest so that all the
        # parameters can be printed out nicely
        self.log.debug('Command-line arguments:')
        length_of_longest_key = len(max(vars(self.cli_arguments).keys(),
                                        key=lambda k: len(k)))
        for arg in vars(self.cli_arguments):
            value = getattr(self.cli_arguments, arg)
            if callable(value):
                self.log.debug('\t{argument_key}:\t{value}'.format(
                    argument_key=arg.rjust(length_of_longest_key, ' '),
                    value='{}.{}()'.format(value.__module__, value.__name__)
                ))

            elif isinstance(value, TextIOWrapper):
                self.log.debug('\t{argument_key}:\t{value}'.format(
                    argument_key=arg.rjust(length_of_longest_key, ' '),
                    value=value.name))

            else:
                self.log.debug('\t{argument_key}:\t{value}'.format(
                    argument_key=arg.rjust(length_of_longest_key, ' '),
                    value=value))

        self.log.debug(self.start_time)

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type in (KeyboardInterrupt, SystemExit):
            return False

        elif exc_type is not None:
            self.log.exception("Something happened and I don't know "
                               "what to do")
            return False

        else:
            finish_time = datetime.now()
            self.log.debug(finish_time)
            self.log.debug('Execution time: {time}'.format(
                time=(finish_time - self.start_time)
            ))
            self.log.debug("#" * 20 + " END EXECUTION " + "#" * 20)
            return True

    def setup_logger(self):
        self.log = logging.getLogger(self.app)
        self.log.setLevel(logging.DEBUG)

        # create file handler which logs even debug messages
        log_file = os.path.join('/tmp', self.app + '.log')
        in_dev_debug_file_handler = logging.FileHandler(
            os.path.join('/tmp', '{}.development.log'.format(self.app))
        )
        in_dev_debug_file_handler.setLevel(logging.DEBUG)

        readable_debug_file_handler = logging.FileHandler(
            os.path.join('/tmp', '{}.debug.log'.format(self.app))
        )
        readable_debug_file_handler.setLevel(logging.DEBUG)

        # create console handler with a higher log level
        command_line_logging = logging.StreamHandler()

        if self.cli_arguments.verbose:
            command_line_logging.setLevel(logging.DEBUG)

            # add relpathname log format attribute so as to only show the file
            #  in which a log was initiated, relative to the project path
            #  e.g. pathname = /full/path/to/project/package/module.py
            #       relpathname = package/module.py
            default_record_factory = logging.getLogRecordFactory()
            project_path = os.path.dirname(os.path.abspath(sys.argv[0])) + \
                           os.sep
            def relpathname_record_factory(*args, **kwargs):
                record = default_record_factory(*args, **kwargs)
                record.relpathname = record.pathname.replace(project_path, '')
                return record
            logging.setLogRecordFactory(relpathname_record_factory)

            # add colors to the logs!
            colored_files_funcs_linenos_formatter = colorlog.ColoredFormatter(
                fmt=(
                    "%(asctime)s - %(log_color)s%(levelname)-8s%(reset)s"
                    " [ %(relpathname)s::%(funcName)s():%(lineno)s ] "
                    "%(message)s"
                ),
                datefmt='%Y-%m-%d %H:%M:%S',
                reset=True,
            )
            in_dev_debug_file_handler.setFormatter(
                colored_files_funcs_linenos_formatter)
            command_line_logging.setFormatter(
                colored_files_funcs_linenos_formatter)

        else:
            command_line_logging.setLevel(logging.INFO)

        # add the handlers to the logger
        self.log.addHandler(in_dev_debug_file_handler)
        self.log.addHandler(command_line_logging)
        self.log.addHandler(readable_debug_file_handler)
