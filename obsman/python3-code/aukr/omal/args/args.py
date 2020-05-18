import logging
from ..const import default_archdir, default_dbfile, default_importdir, default_logfile
from argparse import ArgumentParser

# cli arguments
def getArgs():
    parser = ArgumentParser(description='Observation Management Tool (v1.0.0) - Ankara University Kreiken Observatory')

    # Folder which holds new observations to be imported into archive
    parser.add_argument(
        '-i', '--import-directory', type=str, default=default_importdir, dest='importdir',
        help=f'Directory from which new observations shall be imported (default "{default_importdir}")'
    )

    # Directory for storing archived/upgraded observations, can provide a desired destination
    parser.add_argument(
        '-a', '--archive-directory', type=str, default=default_archdir, dest='archdir',
        help=f'Directory in which archived observations and new observations (until imported) are stored (default "{default_archdir}")'
    )

    # SQLite3 database file, can provide a desired destination
    parser.add_argument(
        '-d', '--database-file', type=str, default=default_dbfile, dest='dbfile',
        help=f'Path of database file to be used for inserting/querying observations (default "{default_dbfile}")'
    )

    # To view debugging info on console, logfile is set for debug mode
    parser.add_argument(
        '--debug', action='store_const', dest='verboselevel', const=logging.DEBUG,
        default=logging.WARNING, help='print debugging info onto console'
    )

    # Logfile destination must be provided, otherwise no logs
    parser.add_argument(
        '-l', '--log-file', type=str, default=default_logfile, dest='logfile',
        help=f'Logfile to print out debug information (default "{default_dbfile if default_dbfile else "none"}"), can be used with alongside "-d" or "-v"'
    )

    parser.add_argument(
        '-v', '--verbose', action='store_const', dest='verboselevel', const=logging.INFO,
        help='print user-readable information'
    )

    parser.add_argument(
        '--no-copy', action='store_const', dest='nocopy', const=True, default=False,
        help='disables copying files into archdir/tmp first'
    )
    
    parser.add_argument(
        '--remove', action='store', dest='rmRefs', nargs='+',
        help='Reference of Observation to be removed (from filesystem and databse)'
    )

    return parser.parse_args()

args = getArgs()

"""
# Alternative way of setting args without command-line arguments.
# good for automated usage, todo: provide a method for programs to enter a
# a config prior to execution.
# Lacks the observation removal functionality.
class arguments:
    def __init__(self, importdir=default_importdir, archdir=default_archdir, dbfile=default_dbfile, logfile=default_logfile, verboselevel=logging.DEBUG, rmRefs=''):
        '''
        :param importdir: Directory from which new observations shall be imported (default "./import_data")
        :param archdir: Directory in which archived observations and new observations (until imported) are stored (default "/obsman/obsv_arch")
        :param dbfile: Path of database file to be used for inserting/querying observations (default ".aukr_obsv.db")
        :param verboselevel: logging.WARNING, logging.INFO, logging.DEBUG
        :param logfile: Logfile to print out debug information
        '''
        self.importdir   = importdir
        self.archdir      = archdir
        self.dbfile       = dbfile
        self.verboselevel = verboselevel
        self.logfile      = logfile
        self.rmRefs        = rmRefs
args = arguments()
"""
