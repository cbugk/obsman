import shutil, errno, os, glob
from ..log import getLogger
from ..args import args
from ..calc import ref
from ..const import BIAS_DIR, DARK_DIR, FLAT_DIR, OBJCT_DIR, OTHER_DIR

# Directories
ARCH_DIR  = args.archdir
TMP_DIR   = f'{ARCH_DIR}/tmp'

# Create module's logger
logger = getLogger(__name__)


def copyToTmp(dirList):
    ''':param dirList: list of paths of directories to be copied into temporary storage
    :returns: list of paths of directories in archive's temporary storage
    '''
    try:
        tmpDirList = []
        for directory in dirList:
            shutil.copytree(directory, f'{TMP_DIR}/{os.path.basename(directory)}')
            tmpDirList.append(f'{TMP_DIR}/{os.path.basename(directory)}')
        return tmpDirList
    except OSError as exc: # python >2.5
        if exc.errno == errno.ENOTDIR:
            shutil.copy(args.importdir, TMP_DIR)
        else: raise
    
def moveToArchive(obsv):
    '''Moves observation folders in archive's temporary storage into archive itself.
    References are concatenated with an underscore inbetween.
    :param obsv: Obsv object referring to observation directory in archive's temporary storage
    :returns: True if successful
    '''
    try:
        if obsv.isNew:
            obsvName = obsv.name + '_' + ref(obsv.hash)
        else:
            obsvName = obsv.name
            
        archObsvRoot = f'{ARCH_DIR}/{obsvName}'
        # self.branchList = [BIAS_DIR, DARK_DIR, FLAT_DIR, objctBranch, OTHER_DIR]
        # copy first three
        for branch in [BIAS_DIR, DARK_DIR, FLAT_DIR]:
            shutil.copytree(f'{obsv.path}/{branch}', f'{archObsvRoot}/{branch}')
        # copy objctBranch
        shutil.copytree(f'{obsv.path}/{obsv.branchList[3]}', f'{archObsvRoot}/{OBJCT_DIR}')
        # copy/create OTHER_DIR
        if os.path.exists(f'{obsv.path}/{OTHER_DIR}'):
            shutil.copytree(f'{obsv.path}/{OTHER_DIR}', f'{archObsvRoot}/{OTHER_DIR}')
        else:
            os.makedirs(f'{archObsvRoot}/{OTHER_DIR}')
        # remove folder in archdir/tmp (provided --no-copy argument is not provided)
        if not args.nocopy:
            shutil.rmtree(obsv.path)
        return True
    except OSError as exc: # python >2.5
        if exc.errno == errno.ENOTDIR:
            shutil.copy(obsv.path, ARCH_DIR)
        else: raise

def cleanTmp():
    '''Deletes all files/directories in archive's temporary storage
    :returns: True if successful
    '''
    try:
        [shutil.rmtree(tmpObsv) for tmpObsv in sorted(glob.glob(f'{TMP_DIR}/*/'))]
        return True
    except OSError as exc: # python >2.5
        logger.warning(exc)

def removeFromArchFolder(obsv):
    ''':param obsv: Obsv object referring to archived observation to be removed
    :returns: True if successful
    '''
    try:
        shutil.rmtree(f'{ARCH_DIR}/{obsv.name}')
        return True
    except OSError as exc:
        logger.warning(exc)

def removeFromArchByRef(ref):
    ''':param ref: Reference of archived observation to be removed.
    :returns: True if successful
    '''
    try:
        [shutil.rmtree(archObsv) for archObsv in sorted(glob.glob(f'{ARCH_DIR}/*_{ref}'))]
        return True
    except OSError as exc:
        logger.warning(exc)  
