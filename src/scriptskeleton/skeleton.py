#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SYNOPSIS

	[python3] skeleton.py [-h,--help] [-v,--verbose] LANGUAGE SCRIPT_NAME[.py|.sh]


DESCRIPTION

	Create a skeleton script for a given language, automatically filled with
	useful tools.


ARGUMENTS

	-h, --help		show this help message and exit
	LANGUAGE		specify the script's language, to be placed as the shebang
								current options: python, python3, bash

	SCRIPT_NAME		the name of the script to be created
	                could be a path - e.g. /path/to/

AUTHOR

	Doug McGeehan <djmvfb@mst.edu>


LICENSE

	Copyright 2017 Doug McGeehan, licensed under the GNU GPLv3.

"""
import os
import argparse
from datetime import datetime
import sys
import logging
import pathlib
import shutil
import pwd

__appname__ = "scriptskeleton"
__author__ = "Doug McGeehan <djmvfb@mst.edu>"
__version__ = "0.0pre0"
__license__ = "GNU GPLv3"


logger = logging.getLogger(__appname__)
ROOT_DIRECTORY = pathlib.Path(__file__).parent.resolve()


# TODO: implement cross-platform functionality. Currently only tested in Linux.
# TODO: obtain user's email?
# TODO: config file for specifying user's name and email and other stuff
def get_author():
    """Get the full name and email address of the current user."""
    current_user_id = os.getuid()
    password_db_entry = pwd.getpwuid(current_user_id)
    user_gecos = password_db_entry.pw_gecos
    fullname = user_gecos.split(',')[0]
    return fullname


class BaseSkeletonBuilder(object):
    templates_stored_in = ROOT_DIRECTORY/'templates'
    author = get_author()
    license = 'GNU GPLv3'
    year = datetime.now().year

    def __init__(self, name, store_in: pathlib.Path):
        if name.endswith(self.extension):
            # command line parameter for script's name is the filename
            #   e.g. script.sh, script.py, etc
            # remove the extension
            character_count_to_remove = len(self.extension)
            self.name = name[:-character_count_to_remove]
        else:
            self.name = name

        logger.debug('Script name: {}'.format(name))
        self.store_in = store_in
        logger.debug('Directory: {}'.format(store_in))
        store_in.mkdir(parents=True, exist_ok=True)

    def generate_script(self):
        filename = self.get_script_filename()
        complete_path = self.store_in/filename
        complete_path.write_text(self.populate_template(),
                                 encoding='utf-8')

        for directory in self.directories_to_create:
            path = self.store_in/self.name/directory
            path.mkdir(parents=True, exist_ok=True)
            logger.info('Created directory {}/'.format(path))

        for empty_file_relpath in self.empty_files_to_create:
            # create an empty file
            path = self.store_in/self.name/empty_file_relpath
            path.write_text('', encoding='utf-8')

        for filename, path_to_copy_into in self.files_to_copy.items():
            directory = self.store_in/path_to_copy_into.format(self)
            directory.mkdir(parents=True, exist_ok=True)
            source = self.templates_stored_in/self.skeleton_directory/filename
            destination = directory/filename
            shutil.copy(source, destination)
            logger.info('Copied {} to {}'.format(source, destination))

        return complete_path

    def generate_installation_file(self):
        raise (
            '{}.generate_installation_file() is not implemented!'.format(
                self.__class__.__name__,
            )
        )

    def get_script_filename(self):
        filename = 'run_{name}{ext}'.format(name=self.name,
                                        ext=self.extension)
        logger.debug('Script filename w/ extension: {}'.format(filename))
        return filename

    def populate_template(self):
        with open(self.get_template_path()) as f:
            template_content = f.read()
        content = template_content.format(self)
        return content

    def get_templates_directory(self):
        return ROOT_DIRECTORY/self.templates_stored_in

    def get_template_path(self):
        template_path = self.get_templates_directory()/self.template_filename
        return template_path


# TODO: implement deprecation warning using the warnings class
class Python3SkeletonBuilder(BaseSkeletonBuilder):
    extension = '.py'
    template_filename = 'python3.template'
    skeleton_directory = 'python3'
    directories_to_create = [
        pathlib.Path('cli')/'scripts',
    ]
    empty_files_to_create = [
        '__init__.py',
        pathlib.Path('cli')/'scripts'/'__init__.py'
    ]
    files_to_copy = {
        'config.py': '{0.name}',
        'cli.py': '{0.name}',
        'requirements.txt': '.',
        'subcommand.py': os.path.join('{0.name}', 'cli', 'scripts')
    }

    def generate_installation_file(self):
        filename = 'setup.py'
        template_directory = self.get_templates_directory()/self.skeleton_directory
        template_path = template_directory/'{}.template'.format(filename)
        template_content = template_path.read_text()
        setup_script_content = template_content.format(self)

        complete_path = self.store_in/filename
        complete_path.write_text(setup_script_content,
                                 encoding='utf-8')

        return complete_path


# TODO: implement bash skeleton template
class BashSkeletonBuilder(BaseSkeletonBuilder):
    extension = '.sh'
    template_filename = 'bash.template'

# TODO: implement C++ skeleton template
class CPlusPlusSkeletonBuilder(BaseSkeletonBuilder):
    extension = '.cpp'
    template_filename = 'cpp.template'


builders = {
    '.py': Python3SkeletonBuilder,
    '.sh': BashSkeletonBuilder,
    '.cpp': CPlusPlusSkeletonBuilder,
}


def script_factory(name, store_in=None):
    extension = os.path.splitext(name)[-1]
    builder_class = builders[extension]
    builder = builder_class(name=name, store_in=store_in)
    builder.generate_installation_file()
    return builder.generate_script()


def _main(args):
    script_path = pathlib.Path(args.script_path)
    directory = script_path.parent.resolve()
    filename = script_path.name
    script_path = script_factory(name=filename, store_in=directory)
    logger.info('Script saved to "{}"'.format(script_path))


def setup_logger(args):
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    # todo: place them in a log directory, or add the time to the log's
    # filename, or append to pre-existing log
    fh = logging.FileHandler('/tmp/' + __appname__ + ".log")
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
    parser.add_argument(
        '-v', '--verbose', action='store_true',
        default=False,
        help='verbose output'
    )

    parser.add_argument(
        'script_path', metavar='SCRIPT_PATH',
        help="the path to where the new script will be saved"
    )

    return parser.parse_args()


def main():
    try:
        start_time = datetime.now()

        args = get_arguments()
        setup_logger(args)
        logger.debug(start_time)

        _main(args)

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


if __name__ == '__main__':
    main()
