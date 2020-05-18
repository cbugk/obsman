import os, glob
from ..args import args
from ..obsv import Obsv
from ..const import MAX_ITEM_PER_DAY
from .. import filesys, calc, sqlitedb, log

# Create module's logger
logger = log.getLogger(__name__)

def cleanup():
    '''Removes all files/folders in archdir/tmp
    '''
    log.heading1('cleanup', logger)
    filesys.cleanTmp()
    logger.info(f'Cleaned: {os.path.abspath(filesys.TMP_DIR)}')

def getTmpObsvList(mode='readonly'):
    '''Clone new observation folders into aukr.omt.filesys.TMP_DIR
    :param mode: Sets Obsv objects' mode members, choose 'readonly' or 'update'.
    :returns: list of (temporary) Obsv objects from archdir/tmp folder
    '''
    log.heading1('getTempObsvList', logger)
    # list of new-observation paths from temporary directory
    importPathList = sorted(glob.glob(f'{args.importdir}/*-*-*'))
    #log paths catched up
    logger.debug(f'To be imported: {[os.path.basename(path) for path in importPathList]}')
    #copy subfolders to archive/tmp then return Obsv object list out of them
    #return [Obsv(path, mode=mode) for path in filesys.copyToTmp(importPathList)]
    try:
        return [Obsv(path, mode='update') for path in (importPathList if args.nocopy else filesys.copyToTmp(importPathList))]
    except ValueError:
        return None


def tmpToArch(tmpObsvList):
    '''Inserts Obsv object (returned by getTmpObsvList) from archdir/tmp into database,
    then moves folders in archdir/tmp into archdir (appends ref e.g. '_ABC123')
    :param tmpObsvList: list of (temporary) Obsv objects from archdir/tmp folder
    '''
    log.heading1('tmpToArch', logger)
    logger.debug(f'To be imported: {[tmpObsv.name for tmpObsv in tmpObsvList]}')
    for tmpObsv in tmpObsvList:
        log.heading2('tmpToArch', logger)
        logger.debug(f'Try insert: {tmpObsv.path}')
        if tmpObsv.insert():
            try:
                logger.debug(f'Try move: {tmpObsv.path}')
                filesys.moveToArchive(tmpObsv)
                logger.warning(f'Moved into {args.archdir}: {tmpObsv.name}')
            except FileExistsError:
                logger.warning(f'Probable database reconstruction from original observation (ignore otherwise): {tmpObsv.name}')
                logger.warning(f'Observation already in archdir, remove before updating: {tmpObsv.name}_{calc.ref(tmpObsv.hash)}')
        else:
            logger.debug(f'Could not insert: {tmpObsv.name}')


def getArchObsvList(mode='readonly'):
    '''Re-parses archived observations in archdir.
    :param mode: Sets Obsv objects' mode members, choose 'readonly' or 'update'.
    :returns: list of Obsv objects from archdir folder
    '''
    log.heading2('getArchObsvList', logger)
    # list of archived-observation paths from archdir
    archPathList = sorted(glob.glob(f'{args.archdir}/*-*-*_*'))
    # log paths catched up
    logger.debug(f'ArchObsv: {[os.path.basename(path) for path in archPathList]}')
    return [Obsv(path, mode=mode) for path in archPathList]

# Remove Obsv objects from both database and filesystem
def removeFromArch(obsvList):
    '''Removes Obsv objects provided, from both database and filesystem
    :param obsvList: list of Obsv objects to be removed from archive
    '''
    log.heading1('removeFromArch', logger)
    for obsv in obsvList:
        sqlitedb.archiveDB.deleteObsv(obsv)
        filesys.removeFromArchFolder(obsv)
        logger.debug(f'Removed: {obsv.name}')

def getHashListByDate(startDate, endDate=''):
    '''Looks for observations within range. If endDate not provided, returns
    hashes for only provided date.
    :param startDate: lower limit of date range
    :param endDate: upper limit of date range
    :returns: hashes for observations within the range
    '''
    # Set boundaries for hashes within range
    if calc.isDate(startDate):
        lowerHash = calc.itemZeroHash(startDate)

        if endDate:
            if calc.isDate(endDate):
                upperHash = calc.itemZeroHash(endDate) + MAX_ITEM_PER_DAY
            else:
                logger.warning(f'End date is not valid: {endDate}')
        else:
            upperHash = lowerHash + MAX_ITEM_PER_DAY
    else:
        logger.warning(f'Start date is not valid: {startDate}')

    # return HASHes which fall in the time period
    return [rowResult[0] for rowResult in sqlitedb.archiveDB.queryHashRange('HASH', lowerHash, upperHash)]

#
def removeObsvByRef(ref):
    '''Removes observation from both filesystem and database
    :returns: True if succesful
    '''
    if (filesys.removeFromArchByRef(ref) and sqlitedb.archiveDB.deleteObsvByRef(ref)):
        return True
    
