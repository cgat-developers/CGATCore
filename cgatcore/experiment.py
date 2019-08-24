'''experiment.py - writing reproducible scripts
=========================================================

The :mod:`experiment` modules contains utility functions for argument
parsing, logging and record keeping within scripts.

This module is imported by most CGAT scripts. It provides convenient
and consistent methods for

   * `Record keeping`_
   * `Argument parsing`_
   * `Input/Output redirection`_
   * `Logging`_
   * `Running external commands`_
   * `Benchmarking`_

See :doc:`../scripts/cgat_script_template` on how to use this module.

The basic usage of this module within a script is::

    """script_name.py - my script

    Mode Documentation
    """
    import sys
    import optparse
    import CGAT.experiment as E

    def main(argv=None):
        """script main.

        parses command line options in sys.argv, unless *argv* is given.
        """

        if not argv: argv = sys.argv

        # setup command line parser
        parser = E.OptionParser(version="%prog version: $Id$",
                                usage=globals()["__doc__"] )

        parser.add_option("-t", "--test", dest="test", type="string",
                          help="supply help")

        # add common options (-h/--help, ...) and parse
        # command line
        (options, args) = E.Start(parser)

        # do something
        # ...
        E.info("an information message")
        E.warn("a warning message)

        ## write footer and output benchmark information.
        E.Stop()

    if __name__ == "__main__":
        sys.exit(main(sys.argv))

Record keeping
--------------

The central functions in this module are the :py:func:`Start` and
:py:func:`Stop` methods which are called before or after any work is
done within a script.

The :py:func:`Start` is called with an E.OptionParser object.
:py:func:`Start` will add additional command line arguments, such as
``--help`` for command line help or ``--verbose`` to control the
:term:`loglevel`.  It can also add optional arguments for scripts
needing database access, writing to multiple output files, etc.

:py:func:`Start` will write record keeping information to a
logfile. Typically, logging information is output on stdout, prefixed
by a `#`, but it can be re-directed to a separate file. Below is a
typical output::

    # output generated by /ifs/devel/andreas/cgat/beds2beds.py --force-output --exclusive-overlap --method=unmerged-combinations --output-filename-pattern=030m.intersection.tsv.dir/030m.intersection.tsv-%s.bed.gz --log=030m.intersection.tsv.log Irf5-030m-R1.bed.gz Rela-030m-R1.bed.gz  # nopep8
    # job started at Thu Mar 29 13:06:33 2012 on cgat150.anat.ox.ac.uk -- e1c16e80-03a1-4023-9417-f3e44e33bdcd
    # pid: 16649, system: Linux 2.6.32-220.7.1.el6.x86_64 #1 SMP Fri Feb 10 15:22:22 EST 2012 x86_64
    # exclusive                               : True
    # filename_update                         : None
    # ignore_strand                           : False
    # loglevel                                : 1
    # method                                  : unmerged-combinations
    # output_filename_pattern                 : 030m.intersection.tsv.dir/030m.intersection.tsv-%s.bed.gz
    # output_force                            : True
    # pattern_id                              : (.*).bed.gz
    # stderr                                  : <open file \'<stderr>\', mode \'w\' at 0x2ba70e0c2270>
    # stdin                                   : <open file \'<stdin>\', mode \'r\' at 0x2ba70e0c2150>
    # stdlog                                  : <open file \'030m.intersection.tsv.log\', mode \'a\' at 0x1f1a810>
    # stdout                                  : <open file \'<stdout>\', mode \'w\' at 0x2ba70e0c21e0>
    # timeit_file                             : None
    # timeit_header                           : None
    # timeit_name                             : all
    # tracks                                  : None

The header contains information about:

    * the script name (``beds2beds.py``)

    * the command line options (``--force-output --exclusive-overlap
      --method=unmerged-combinations
      --output-filename-pattern=030m.intersection.tsv.dir/030m.intersection.tsv-%s.bed.gz
      --log=030m.intersection.tsv.log Irf5-030m-R1.bed.gz
      Rela-030m-R1.bed.gz``)

    * the time when the job was started (``Thu Mar 29 13:06:33 2012``)
    * the location it was executed (``cgat150.anat.ox.ac.uk``)
    * a unique job id (``e1c16e80-03a1-4023-9417-f3e44e33bdcd``)
    * the pid of the job (``16649``)

    * the system specification (``Linux 2.6.32-220.7.1.el6.x86_64 #1
      SMP Fri Feb 10 15:22:22 EST 2012 x86_64``)

It is followed by a list of all options that have been set in the script.

Once completed, a script will call the :py:func:`Stop` function to
signify the end of the experiment.

:py:func:`Stop` will output to the log file that the script has
concluded successfully. Below is typical output::

    # job finished in 11 seconds at Thu Mar 29 13:06:44 2012 -- 11.36 0.45 0.00 0.01 \
      -- e1c16e80-03a1-4023-9417-f3e44e33bdcd

The footer contains information about:

   * the job has finished (``job finished``)
   * the time it took to execute (``11 seconds``)
   * when it completed (``Thu Mar 29 13:06:44 2012``)
   * some benchmarking information (``11.36  0.45  0.00  0.01``)
     which is ``user time``, ``system time``,
     ``child user time``, ``child system time``.
   * the unique job id (``e1c16e80-03a1-4023-9417-f3e44e33bdcd``)

The unique job id can be used to easily retrieve matching information
from a concatenation of log files.

Argument parsing
----------------

The module provides :class:`OptionParser` to facilitate option
parsing.  :class:`OptionParser` is derived from the
:py:class:`optparse.OptionParser` class, but has improvements to
provide better formatted output on the command line. It also allows to
provide a comma-separated list to options that accept multiple
arguments. Thus, ``--method=sort --method=crop`` and
``--method=sort,crop`` are equivalent.

Additionally, there are set of commonly used option groups that are
used in many scripts. The :func:`Start` method has options to automatically
add these. For example::

   (options, args) = E.Start(parser, add_output_options=True)

will add the option ``--output-filename-pattern``. Similarly::

   (options, args) = E.Start(parser, add_database_options=True)

will add multiple options for scripts accessing databases, such as
``--database-host`` and ``--database-username``.

Input/Output redirection
------------------------

:func:`Start` adds the options ``--stdin``, ``--stderr` and
``--stdout`` which allow using files as input/output streams.

To make this work, scripts should not read from sys.stdin or write to
sys.stdout directly, but instead use ``options.stdin`` and
``options.stdout``. For example to simply read all lines from stdin
and write to stdout, use::

   (options, args) = E.Start(parser)

   input_data = options.stdin.readlines()
   options.stdout.write("".join(input_data))

The script can then be used in many different contexts::

   cat in.data | python script.py > out.data
   python script.py --stdin=in.data > out.data
   python script.py --stdin=in.data --stdout=out.data

The method handles gzip compressed files transparently. The following
are equivalent::

   zcat in.data.gz | python script.py | gzip > out.data.gz
   python script.py --stdin=in.data.gz --stdout=out.data.gz

For scripts producing multiple output files, use the argument
``add_output_options=True`` to :func:`Start`. This provides the option
``--output-filename-pattern`` on the command line. The user can then
supply a pattern for output files. Any ``%s`` appearing in the pattern
will be substituted by a ``section``. Inside the script, When opening
an output file, use the method :func:`open_output_file` to provide a
file object::

   output_histogram = E.open_output_file(section="histogram")
   output_stats = E.open_output_file(section="stats")

If the user calls the script with::

   python script.py --output-filename-pattern=sample1_%s.tsv.gz

the script will create the files ``sample1_histogram.tsv.gz`` and
``sample1_stats.tsv.gz``.

This method will also add the option ``--force-output`` to permit
overwriting existing files.

Logging
-------

:py:mod:`experiment` provides the well known logging methods from
the :py:mod:`logging` module such as :py:func:`info`,
:py:func:`warn`, etc. These are provided so that no additional import
of the :py:mod:`logging` module is required, but either functions
can be used.

Running external commands
-------------------------

The :func:`run` method is a shortcut :py:func:`subprocess.call` and
similar methods with some additional sanity checking.

Benchmarking
------------

The :func:`Start` method records basic benchmarking information when a
script starts and :func:`Stop` outputs it as part of its final log
message::

    # job finished in 11 seconds at Thu Mar 29 13:06:44 2012 -- 11.36 0.45 0.00 0.01 \
      -- e1c16e80-03a1-4023-9417-f3e44e33bdcd

See `Record keeping`_ for an explanations of the fields.

To facilitate collecting benchmark information from running multiple
scripts, these data can be tagged and saved in a separate file. See the
command line options ``--timeit``, ``--timeit-name``, ``--timeit-header``
in :func:`Start`.

The module contains some decorator functions for benchmarking
(:func:`benchmark`) and caching function (:func:`cached_function`) or
class method (:func:`cached_method`) calls.

API
---

'''

import re
import sys
import time
import inspect
import copy
import os
import collections
import subprocess
import functools
import gzip
import warnings
import pipes
import argparse
import textwrap
import random
import uuid
import yaml
# import convenience functions from logging
import logging
import logging.config
from logging import warning, info, log, debug, error, critical
from logging import warning as warn


class DefaultOptions:
    stdlog = sys.stdout
    stdout = sys.stdout
    stderr = sys.stderr
    stdin = sys.stdin
    loglevel = 2
    timeit_file = None

global_starting_time = time.time()
global_options = DefaultOptions()
global_args = None
global_id = uuid.uuid4()
global_benchmark = collections.defaultdict(int)

class OptionParser(argparse.ArgumentParser):

    '''CGAT derivative of OptionParser.
    '''

    def __init__(self, *args, **kwargs):
        # if "--short" is a command line option
        # remove usage from kwargs
        if "--no-usage" in sys.argv:
            kwargs["usage"] = None

        argparse.ArgumentParser.__init__(self, *args,formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                       **kwargs)

        # set new option parser
        # parser.formatter.set_parser(parser)
        if "--no-usage" in sys.argv:
            self.add_argument("--no-usage", dest="help_no_usage",
                            action="store_true",
                            help="output help without usage information")


def callbackShortHelp(option, opt, value, parser):
    '''output short help (only command line options).'''
    # clear usage and description
    parser.set_description(None)
    parser.set_usage(None)
    # output help
    parser.print_help()
    # exit
    parser.exit()


def open_file(filename, mode="r", create_dir=False, encoding="utf-8"):
    '''open file in *filename* with mode *mode*.

    If *create* is set, the directory containing filename
    will be created if it does not exist.

    gzip - compressed files are recognized by the
    suffix ``.gz`` and opened transparently.

    Note that there are differences in the file
    like objects returned, for example in the
    ability to seek.

    returns a file or file-like object.
    '''

    _, ext = os.path.splitext(filename)

    if create_dir:
        dirname = os.path.abspath(os.path.dirname(filename))
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname)

    if ext.lower() in (".gz", ".z"):
        # in gzip, r defaults to "rt", so make it compatible with open
        if mode == "r":
            mode = "rt"
        elif mode == "w":
            mode = "wt"
        return gzip.open(filename, mode, encoding=encoding)
    else:
        return open(filename, mode, encoding=encoding)


def get_header():
    """return a header string with command line options and timestamp

    """
    system, host, release, version, machine = os.uname()

    return "output generated by %s\njob started at %s on %s -- %s\npid: %i, system: %s %s %s %s" %\
           (" ".join(sys.argv),
            time.asctime(time.localtime(time.time())),
            host,
            global_id,
            os.getpid(),
            system, release, version, machine)


def get_params(options=None):
    """return a string containing script parameters.

    Parameters are all variables that start with ``param_``.
    """
    result = []
    if options:
        members = options.__dict__
        for k, v in sorted(members.items()):
            result.append("%-40s: %s" % (k, str(v)))
    else:
        vars = inspect.currentframe().f_back.f_locals
        for var in [x for x in list(vars.keys()) if re.match("param_", x)]:
            result.append("%-40s: %s" %
                          (var, str(vars[var])))

    if result:
        return "\n".join(result)
    else:
        return "# no parameters."


def get_footer():
    """return a header string with command line options and
    timestamp.
    """
    return "job finished in %i seconds at %s -- %s -- %s" %\
           (time.time() - global_starting_time,
            time.asctime(time.localtime(time.time())),
            " ".join(["%5.2f" % x for x in os.times()[:4]]),
            global_id)


class MultiLineFormatter(logging.Formatter):
    '''logfile formatter: add identation for multi-line entries.'''

    def format(self, record):

        s = logging.Formatter.format(self, record)
        if s.startswith("#"):
            prefix = "#"
        else:
            prefix = ""
        if record.message:
            header, footer = s.split(record.message)
            s = s.replace("\n", " \\\n%s" % prefix + " " * (len(header) - 1))
        return s


def start(parser=None,
          argv=None,
          quiet=False,
          no_parsing=False,
          add_csv_options=False,
          add_database_options=False,
          add_pipe_options=True,
          add_cluster_options=False,
          add_output_options=False,
          logger_callback=None,
          return_parser=False):
    """set up an experiment.

    The :py:func:`Start` method will set up a file logger and add some
    default and some optional options to the command line parser.  It
    will then parse the command line and set up input/output
    redirection and start a timer for benchmarking purposes.

    The default options added by this method are:

    ``-v/--verbose``
        the :term:`loglevel`

    ``timeit``
        turn on benchmarking information and save to file

    ``timeit-name``
         name to use for timing information,

    ``timeit-header``
         output header for timing information.

    ``seed``
         the random seed. If given, the python random
         number generator will be initialized with this
         seed.

    Optional options added are:

    add_csv_options

       ``dialect``
            csv_dialect. the default is ``excel-tab``, defaulting to
            :term:`tsv` formatted files.

    add_database_options
       ``-C/--connection``
           psql connection string
       ``-U/--user``
           psql user name

    add_cluster_options
       ``--use-cluster``
           use cluster
       ``--cluster-priority``
           cluster priority to request
       ``--cluster-queue``
           cluster queue to use
       ``--cluster-num-jobs``
           number of jobs to submit to the cluster at the same time
       ``--cluster-options``
           additional options to the cluster for each job.

    add_output_options
       ``-P/--output-filename-pattern``
            Pattern to use for output filenames.

    Arguments
    ---------

    param parser : :py:class:`E.OptionParser`
       instance with command line options.

    argv : list
        command line options to parse. Defaults to
        :py:data:`sys.argv`

    quiet : bool
        set :term:`loglevel` to 0 - no logging

    no_parsing : bool
        do not parse command line options

    return_parser : bool
        return the parser object, no parsing. Useful for inspecting
        the command line options of a script without running it.

    add_csv_options : bool
        add common options for parsing :term:`tsv` separated files.

    add_database_options : bool
        add common options for connecting to various databases.

    add_pipe_options : bool
        add common options for redirecting input/output

    add_cluster_options : bool
        add common options for scripts submitting jobs to the cluster

    add_output_options : bool
        add commond options for working with multiple output files

    logger_callback : object
        callback function to further configure logging system. The
        callback should accept the options as first parameter and
        return a logger.

    Returns
    -------
    tuple
       (:py:class:`E.OptionParser` object, list of positional
       arguments)

    """

    if argv is None:
        argv = sys.argv

    global global_args, global_starting_time

    # save default values given by user
    user_defaults = copy.copy(parser.parse_args([]))

    global_starting_time = time.time()

    group = parser.add_argument_group("Script timing options")

    group.add_argument("--timeit", dest='timeit_file', type=str,
                     help="store timeing information in file.")
    group.add_argument("--timeit-name", dest='timeit_name', type=str,
                     help="name in timing file for this class of jobs ")
    group.add_argument("--timeit-header", dest='timeit_header',
                     action="store_true",
                     help="add header for timing information.")

    group = parser.add_argument_group("Common options")

    group.add_argument("--random-seed", dest='random_seed', type=int,
                     help="random seed to initialize number generator "
                     "with")

    group.add_argument("-v", "--verbose", dest="loglevel", type=int,
                     help="loglevel. The higher, the more output.")

    group.add_argument("--log-config-filename",
                     dest="log_config_filename",
                     type=str,
                     default="logging.yml",
                     help="Configuration file for logger.")

    group.add_argument("--tracing", dest="tracing", type=str,
                     choices=["function"],
                     default=None,
                     help="enable function tracing.")

    group.add_argument("-?", type=callbackShortHelp,
                     help="output short help (command line options only.")

    if quiet:
        parser.set_defaults(loglevel=0)
    else:
        parser.set_defaults(loglevel=1)

    parser.set_defaults(
        timeit_file=None,
        timeit_name='all',
        timeit_header=None,
        random_seed=None,
        tracing=None,
    )

    if add_csv_options:
        parser.add_argument("--csv-dialect", dest="csv_dialect", type=str,
                          help="csv dialect to use.")

        parser.set_defaults(
            csv_dialect="excel-tab",
            csv_lineterminator="\n",
        )

    if add_cluster_options:
        group = parser.add_argument_group("cluster options")
        group.add_argument("--no-cluster", "--local", dest="without_cluster",
                         action="store_true",
                         help="do no use cluster - run locally.")
        group.add_argument("--cluster-priority", dest="cluster_priority",
                         type=int,
                         help="set job priority on cluster.")
        group.add_argument("--cluster-queue", dest="cluster_queue",
                         type=str,
                         help="set cluster queue.")
        group.add_argument("--cluster-num-jobs", dest="cluster_num_jobs",
                         type=int,
                         help="number of jobs to submit to the queue execute "
                         "in parallel.")
        group.add_argument("--cluster-parallel",
                         dest="cluster_parallel_environment",
                         type=str,
                         help="name of the parallel environment to use ")
        group.add_argument("--cluster-options", dest="cluster_options",
                         type=str,
                         help="additional options for cluster jobs, passed "
                         "on to queuing system.")
        group.add_argument("--cluster-queue-manager",
                         dest="cluster_queue_manager",
                         type=str,
                         choices=["sge", "slurm", "torque", "pbspro"],
                         help="cluster queuing system ")
        group.add_argument("--cluster-memory-resource",
                         dest="cluster_memory_resource",
                         type=str,
                         help="resource name to allocate memory with ")
        group.add_argument("--cluster-memory-default",
                         dest="cluster_memory_default",
                         type=str,
                         help="default amount of memory to allocate ")

        parser.set_defaults(without_cluster=False,
                            cluster_queue=None,
                            cluster_priority=None,
                            cluster_num_jobs=None,
                            cluster_parallel_environment=None,
                            cluster_options=None,
                            cluster_memory_resource=None,
                            cluster_memory_default="unlimited",
                            cluster_queue_manager="sge")

    if add_output_options or add_pipe_options:
        group = parser.add_argument_group("Input/output options")

        if add_output_options:
            group.add_argument(
                "-P", "--output-filename-pattern",
                dest="output_filename_pattern", type=str,
                help="OUTPUT filename pattern for various methods ")

            group.add_argument("-F", "--force-output", dest="output_force",
                             action="store_true",
                             help="force over-writing of existing files.")

            parser.set_defaults(output_filename_pattern="%s",
                                output_force=False)

        if add_pipe_options:

            group.add_argument("-I", "--stdin", dest="stdin", type=str,
                             help="file to read stdin from [default = stdin].")
            group.add_argument("-L", "--log", dest="stdlog", type=str,
                             help="file with logging information "
                             "[default = stdout].")
            group.add_argument("-E", "--error", dest="stderr", type=str,
                             help="file with error information "
                             "[default = stderr].")
            group.add_argument("-S", "--stdout", dest="stdout", type=str,
                             help="file where output is to go "
                             "[default = stdout].")

            parser.set_defaults(stderr=sys.stderr)
            parser.set_defaults(stdout=sys.stdout)
            parser.set_defaults(stdlog=sys.stdout)
            parser.set_defaults(stdin=sys.stdin)

    if add_database_options:
        group = parser.add_argument_group("database connection options")
        group.add_argument(
            "--database-url", dest="database_url", type=str,
            help="database connection url, for example sqlite:///./csvdb.")

        group.add_argument(
            "--database-schema", dest="database_schema", type=str,
            help="database schem")
        
        parser.set_defaults(database_url="sqlite:///./csvdb")
        parser.set_defaults(database_schema=None)

    if return_parser:
        return parser

    if not no_parsing:
        global_args = parser.parse_args()

    if global_args.random_seed is not None:
        random.seed(global_args.random_seed)

    if add_pipe_options:
        if global_args.stdout != sys.stdout:
            global_args.stdout = open_file(global_args.stdout, "w")
        if global_args.stderr != sys.stderr:
            if global_args.stderr == "stderr":
                global_args.stderr = global_args.stderr
            else:
                global_args.stderr = open_file(global_args.stderr, "w")
        if global_args.stdlog != sys.stdout:
            global_args.stdlog = open_file(global_args.stdlog, "a")
        if global_args.stdin != sys.stdin:
            global_args.stdin = open_file(global_args.stdin, "r")
    else:
        global_args.stderr = sys.stderr
        global_args.stdout = sys.stdout
        global_args.stdlog = sys.stdout
        global_args.stdin = sys.stdin

    # reset log_config_filename if logging.yml does not exist
    if global_args.log_config_filename == "logging.yml" and not os.path.exists(
            global_args.log_config_filename):
        global_args.log_config_filename = None

    if global_args.log_config_filename:
        if os.path.exists(global_args.log_config_filename):
            # configure logging from filename
            with open(global_args.log_config_filename) as inf:
                dict_yaml = yaml.load(inf)
            logging.config.dictConfig(dict_yaml)
        else:
            raise OSError("file {} with logging configuration does not exist".format(
                global_args.log_config_filename))
    else:
        # configure logging from command line options
        # map from 0-10 to logging scale
        # 0: quiet
        # 1: little verbositiy
        # >1: increased verbosity
        if global_args.loglevel == 0:
            lvl = logging.ERROR
        elif global_args.loglevel == 1:
            lvl = logging.INFO
        else:
            lvl = logging.DEBUG

        if global_args.stdout == global_args.stdlog:
            logformat = '# %(asctime)s %(levelname)s %(message)s'
        else:
            logformat = '%(asctime)s %(levelname)s %(message)s'

        logging.basicConfig(
            level=lvl,
            format=format,
            stream=global_args.stdlog)

        # set up multi-line logging
        # Note that .handlers is not part of the API, might change
        # Solution is to configure handlers explicitely.
        for handler in logging.getLogger().handlers:
            handler.setFormatter(MultiLineFormatter(logformat))

    if logger_callback:
        logger = logger_callback(global_options)
    else:
        logger = logging.getLogger("cgatcore")

    logger.info(get_header())
    logger.info(get_params(global_args))

    if global_args.tracing == "function":
        sys.settrace(trace_calls)

    return global_args


def stop(logger=None):
    """stop the experiment.

    This method performs final book-keeping, closes the output streams
    and writes the final log messages indicating script completion.
    """

    if global_args.loglevel >= 1 and global_benchmark:
        t = time.time() - global_starting_time
        global_args.stdlog.write(
            "######### Time spent in benchmarked functions #########\n")
        global_args.stdlog.write("# function\tseconds\tpercent\n")
        for key, value in list(global_benchmark.items()):
            global_args.stdlog.write(
                "# %s\t%6i\t%5.2f%%\n" % (key, value,
                                          (100.0 * float(value) / t)))
        global_args.stdlog.write(
            "#######################################################\n")

    if logger is None:
        logger = logging.getLogger("cgatcore")
    logger.info(get_footer())

    # close files
    if global_args.stdout != sys.stdout:
        global_args.stdout.close()
    # do not close log, otherwise error occurs in atext.py
    # if global_options.stdlog != sys.stdout:
    #   global_options.stdlog.close()

    if global_args.stderr != sys.stderr:
        global_args.stderr.close()

    if global_args.timeit_file:

        outfile = open(global_args.timeit_file, "a")

        if global_args.timeit_header:
            outfile.write("\t".join(
                ("name", "wall", "user", "sys", "cuser", "csys",
                 "host", "system", "release", "machine",
                 "start", "end", "path", "cmd")) + "\n")

        csystem, host, release, version, machine = list(map(str, os.uname()))
        uusr, usys, c_usr, c_sys = ["%5.2f" % x for x in os.times()[:4]]
        t_end = time.time()
        c_wall = "%5.2f" % (t_end - global_starting_time)

        if sys.argv[0] == "run.py":
            cmd = global_args[0]
            if len(global_args) > 1:
                cmd += " '" + "' '".join(global_args[1:]) + "'" # AC hmm not sure what old global_args is not
        else:
            cmd = sys.argv[0]

        result = "\t".join((global_options.timeit_name,
                            c_wall, uusr, usys, c_usr, c_sys,
                            host, csystem, release, machine,
                            time.asctime(time.localtime(global_starting_time)),
                            time.asctime(time.localtime(t_end)),
                            os.path.abspath(os.getcwd()),
                            cmd)) + "\n"

        outfile.write(result)
        outfile.close()


def get_output_file(section):
    '''return filename to write to, replacing any ``%s`` with section in
    the output pattern for files (``--output-filename-pattern``).
    '''
    return re.sub("%s", section, global_args.output_filename_pattern)


def open_output_file(section, mode="w", encoding="utf-8"):
    """open file for writing substituting section in the
    output_pattern (if defined).

    This method will automatically create any parent directories that
    are missing.

    If the filename ends with ".gz", the output is opened as a gzip'ed
    file.

    Arguments
    ---------
    section : string
       section will replace any %s in the pattern for output files.

    mode : char
       file opening mode

    Returns
    -------
    File
        an opened file

    """

    fn = get_output_file(section)

    if fn == "-":
        return global_args.stdout

    if not global_args.output_force and os.path.exists(fn):
        raise OSError(
            "file %s already exists, use --force-output to "
            "overwrite existing files.".format(fn))

    return open_file(fn, mode=mode, create_dir=True, encoding=encoding)


def run(statement,
        return_stdout=False,
        return_stderr=False,
        return_popen=False,
        on_error="raise",
        encoding="utf-8",
        **kwargs):
    '''execute a command line statement.

    By default this method returns the code returned by the executed
    command. If *return_stdout* is True, the contents of stdout are
    returned as a string, likewise for *return_stderr*.

    If *return_popen*, the Popen object is returned.

    ``kwargs`` are passed on to subprocess.call,
    subprocess.check_output or subprocess.Popen.

    Arguments
    ---------

    on_error: string
       Action to perform on error. Valid actions are "ignore" and "raise".

    Raises
    ------

    OSError
       If process failed or was terminated.

    '''

    # remove new lines
    statement = " ".join(re.sub("\t+", " ", statement).split("\n")).strip()

    if "<(" in statement:
        shell = os.environ.get('SHELL', "/bin/bash")
        if "bash" not in shell:
            raise ValueError(
                "require bash for advanced shell syntax: <()")
        # Note: pipes.quote is deprecated. In Py3, use shlex.quote
        # (not present in Py2.7)
        statement = "%s -c %s" % (shell, pipes.quote(statement))

    if return_stdout:
        try:
            output = subprocess.check_output(statement, shell=True, **kwargs)
        except subprocess.CalledProcessError as e:
            if on_error == "raise":
                raise
            output = e.output
        return output.decode(encoding)

    elif return_stderr:
        # expect that process fails
        p = subprocess.Popen(statement,
                             shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             **kwargs)
        stdout, stderr = p.communicate()
        return stderr.decode(encoding)

    elif return_popen:
        return subprocess.Popen(statement, shell=True, **kwargs)

    else:
        retcode = subprocess.call(statement, shell=True, **kwargs)
        if retcode < 0:
            raise OSError("process was terminated by signal: {}".format(-retcode))
        elif retcode > 0:
            raise OSError("process exited with code: {}".format(retcode))
        return retcode


# some convenient decorators
def benchmark(func):
    """decorator collecting wall clock time spent in decorated method."""

    def wrapper(*arg):
        t1 = time.time()
        res = func(*arg)
        t2 = time.time()
        key = "%s:%i" % (func.__name__, func.__code__.co_firstlineno)
        global_benchmark[key] += t2 - t1
        global_options.stdlog.write(
            '## benchmark: %s completed in %6.4f s\n' % (key, (t2 - t1)))
        global_options.stdlog.flush()
        return res
    return wrapper


class cached_function(object):
    """Decorator that caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned, and
    not re-evaluated.

    Taken from http://wiki.python.org/moin/PythonDecoratorLibrary#Memoize
    """

    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args, **kwargs):
        key = (args, frozenset(list(kwargs.items())))
        try:
            return self.cache[key]
        except KeyError:
            value = self.func(*args, **kwargs)
            self.cache[key] = value
            return value
        except TypeError:
            # uncachable -- for instance, passing a list as an argument.
            # Better to not cache than to blow up entirely.
            return self.func(*args, **kwargs)

    def __repr__(self):
        """Return the function's docstring."""
        return self.func.__doc__

    def __get__(self, obj, objtype):
        """Support instance methods."""
        return functools.partial(self.__call__, obj)

    def delete(self, *args, **kwargs):
        """remove a cache entry"""
        key = (args, frozenset(list(kwargs.items())))
        del self.cache[key]


class cached_property(object):
    '''Decorator for read-only properties.

    Modified from https://wiki.python.org/moin/PythonDecoratorLibrary#Memoize
    '''
    def __init__(self, hello):
        print(hello)

    def __call__(self, fget, doc=None):
        self.fget = fget
        self.__doc__ = doc or fget.__doc__
        self.__name__ = fget.__name__
        self.__module__ = fget.__module__
        return self

    def __get__(self, inst, owner):
        try:
            value = inst._cache[self.__name__]
        except KeyError:
            value = self.fget(inst)
            try:
                cache = inst._cache
            except AttributeError:
                cache = inst._cache = {}
            cache[self.__name__] = value
        return value


class cached_method(object):

    def __init__(self, func):
        self.func = func

    def __get__(self, instance, cls=None):
        if instance is None:
            return self.func
        return functools.partial(self, instance)

    def __call__(self, *args, **kwargs):
        obj = args[0]
        try:
            cache = obj.__cache
        except AttributeError:
            cache = obj.__cache = {}

        key = (self.func, args[1:], frozenset(list(kwargs.items())))
        try:
            return cache[key]
        except KeyError:
            value = self.func(*args, **kwargs)
            cache[key] = value
            return value
        except TypeError:
            # uncachable -- for instance, passing a list as an argument.
            # Better to not cache than to blow up entirely.
            return self.func(*args, **kwargs)


class Counter(object):
    '''a counter class.

    The counter acts both as a dictionary and a object permitting
    attribute access.

    Counts are automatically initialized to 0.

    Instantiate and use like this::

       c = Counter()
       c.input += 1
       c.output += 2
       c["skipped"] += 1

       print str(c)
    '''

    __slots__ = ["_counts"]

    def __init__(self):
        """Store data returned by function."""
        object.__setattr__(self, "_counts", collections.defaultdict(int))

    def __setitem__(self, key, value):
        self._counts[key] = value

    def __getitem__(self, key):
        return self._counts[key]

    def __str__(self):
        return ", ".join("%s=%i" % x for x in self._counts.items())

    def items(self):
        return self._counts.items()

    def __iadd__(self, other):
        for key, val in other.items():
            self._counts[key] += val
        return self

    def iteritems(self):
        return iter(self._counts.items())

    def values(self):
        return self._counts.values()

    def asTable(self, as_rows=True):
        '''return values as tab-separated table (without header).

        Key, value pairs are sorted lexicographically.
        '''
        if as_rows:
            return '\n'.join("%s\t%i" % x
                             for x in sorted(self._counts.items()))
        else:
            columns, values = list(zip(*sorted(self._counts.items())))
            return '{}\n{}'.format("\t".join(columns),
                                   "\t".join(map(str, values)))

    def __getattr__(self, name):
        return self._counts[name]

    def __setattr__(self, name, value):
        self._counts[name] = value


def trace_calls(frame, event, arg):
    """trace functions calls for debugging purposes.

    See https://pymotw.com/2/sys/tracing.html
    """
    if event != 'call':
        return
    co = frame.f_code
    func_name = co.co_name
    if func_name == 'write':
        # Ignore write() calls from print statements
        return
    func_line_no = frame.f_lineno
    func_filename = co.co_filename
    caller = frame.f_back
    if caller is None:
        print('# called: %s:%s (%s) (from None' %
              (func_name, func_line_no, func_filename))
    else:
        caller_line_no = caller.f_lineno
        caller_filename = caller.f_code.co_filename
        print('# called: %s:%s (%s) (from %s:%s)' %
              (func_name, func_line_no, func_filename,
               caller_filename, caller_line_no))
    return


def enable_tracing(level="function"):
    if level == "function":
        sys.settrace(trace_calls)
