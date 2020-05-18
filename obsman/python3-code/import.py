from aukr.omal import log, functions as fcns

## Use of logfile is encouraged only when it is preiodically deleted.
## Otherwise prefer setting "verboselevel=logging.DEBUG", and "logfile=''"
## This file should suffice as an example for simple interactions with
## the aukr.omal package

# Create logger (leave as "__name__", even though not strictly necessary)
# logger.warning(), logger.info(), logger.debug() are different methods for
# logging/printing internal messages. Please use print or another logger for
# your needs, if possible
logger  = log.getLogger(__name__)

# For aesthetics/readibility
log.banner('START', logger)

# Removes files/directories from archive's temporary directory (almost always necessary)
fcns.cleanup()

# After copying provided observation directories into temporary directory,
# returns a list of Obsv objects (FitsFile objects in Obsv.fitsTree object)
tmpObsvList = fcns.getTmpObsvList('update')

# Tries inserting Obsv objects in list above into archive database; if
# successful, copies them into archive directory
fcns.tmpToArch(tmpObsvList)

# Returns Obsv objects from observations in archive directory (all of them)
#archObsvList = fcns.getArchObsvList()

# Removes files/folders left from temporary Obsv objects' insertion process
# (Suggested. Unlike top cleanse, not necessary)
fcns.cleanup()

# For aesthetics/readibility
log.heading1('FINISH', logger)
