import os, glob
from ..const import BIAS_DIR, DARK_DIR, FLAT_DIR, OBJCT_DIR, OTHER_DIR,\
    MAX_CONTROL_ITEM, MAX_OBSV_PER_DAY, MAX_ITEM_PER_DAY, MAX_ITEM_PER_OBSV
from .. import calc, log
from ..fitsfile import FitsFile
from ..sqlitedb import archiveDB

# Create module's logger
logger  = log.getLogger(__name__)

class Obsv:
    '''Class for representing observations (each has its own directory)
    '''

    def __init__(self, path, mode='readonly'):
        ''':param path: path to observation folder to be parsed (can be relative)
        :param mode: indicates if file will be modified (choose 'readonly', 'update')
        '''

        self.isNew       = None
        self.mode        = None    # from constructor
        self.path        = None    # from constructor
        self.name        = None    # from self.path
        self.fitsTree    = []      # from filesystem, list of FitsFile objects
        self.tlscp       = None    # from fitsTree
        self.objct       = None    # from fitsTree
        self.date        = None    # from foldername inserted at observation event
                            #("YYYY-MM-DD" or "YYYY-MM-DD_F00BA2")
        self.hash        = None   # from foldername inserted at observation archiving
                            #process, if any ("F00BA2")

        log.heading2('ObsvInit', logger) # for more readable logs
        logger.debug(f'Constructing Obsv: {path}')
        self.path = path # for readable logs incase not a dir
        # Check directory exists
        if not os.path.isdir(path):
            logger.debug(f'Not a directory: {path}')
            return None
        self.path = os.path.abspath(path)
        self.name = os.path.basename(path)
        self.mode = mode
        
        # Import date and ref if applicable,
        # else get default-ref and set isNew=True
        self.parseDateRef()

        # import fitsTree, tlscp, object if data the same in all headers
        # updates fits files of new observations, provided mode='update'
        self.parseFitsTree()


    def parseDateRef(self):
        '''Parses date and ref from observations foldername (validates first)
        '''
        # Seperate the foldername from last underscore
        # ('', '', 'str') returned if delimeter not found
        (date, delim, ref) = self.name.rpartition('_')

        # Possible archived observation
        if delim:
            # Check pre-delimeter for date
            if calc.isDate(date):
                self.date = date
            else:
                logger.debug(f'Foldername fault (DATE not real): {self.path}')
                raise ValueError
            # Check post-delimeter for ref
            (date, item) = calc.validDateAndItem(ref)
            if date == self.date and item == 0:
                self.hash = calc.hash(ref)
            else:
                logger.debug(f'Foldername fault (REF for wrong day or is a file): {self.path}')
                raise ValueError
            # Explicitly set isNew False (rather than None)
            self.isNew = False
        # Possible new observation
        else:          
            # ref = os.path.basename(path) rigth now
            if calc.isDate(ref):
                self.date = ref
            else:
                logger.debug(f'Foldername fault (not a date): {self.path}')
                raise ValueError
            # Set as new observation
            self.isNew = True
            # Get default Obsv.ref for the day
            self.hash = calc.itemZeroHash(self.date)


    def parseFitsTree(self):
        '''Parses FitsFile objects from observation folder, while preserving
        tree structure. Validates FitsFile objects by comparing members
        tlscp and objct (tlscp is observation-wide, objct is branch-wide).
        '''
        # Looks for subfolders (branches), then ".fit" files within each branch;
        # structure is enforced (no recursion is desired, nor implemented).
        # fitsTree is the list of fitsBranches containing FitsFile objects
        # self.fitsTree/fitsBranch/fitsFile

        # get subfolders (with leading slash, so surely are directories)
        fitsDirList = sorted(glob.glob(f'{self.path}/*/'))
        # remove leading slash for proper absolute path format
        fitsDirList = [os.path.dirname(fitsDir) for fitsDir in fitsDirList]
        # get subfolder names, into a parallel list (same order)
        branchList = [os.path.basename(branch) for branch in fitsDirList]

        # Must have subfolders (fitsBranches):
        # BIAS_DIR, DARK_DIR, FLAT_DIR, and (objctBranch, optionally OTHER_DIR)
        if (len(branchList) < 4) or (len(branchList) > 5):
            logger.debug(f'Only [{BIAS_DIR}, {DARK_DIR}, {FLAT_DIR}, Object\'s Folder, {OTHER_DIR}(optional)] are allowed: {self.path}')
            return # terminate without changes
        if (   (BIAS_DIR not in branchList)
            or (DARK_DIR not in branchList)
            or (FLAT_DIR not in branchList)
            ):
            logger.debug(f'Subfolder(s) missing [{BIAS_DIR}, {DARK_DIR}, '
                f'{FLAT_DIR}]: {self.path}')
            return # terminate without changes
            
        # New Obsevation (objctBranch's name can be any non-reserved name)
        if self.isNew:
            # Find out OBJCT_DIR's name by removing all from branchlist-clone
            objctBranch = branchList.copy() # listA = listB is by reference
            objctBranch.remove(BIAS_DIR)
            objctBranch.remove(DARK_DIR)
            objctBranch.remove(FLAT_DIR)
            if (len(objctBranch) == 2) and (OTHER_DIR in branchList): # (5 subfolders)
                objctBranch.remove(OTHER_DIR)
            elif len(objctBranch) != 1: # 5 subfolders but no OTHER_DIR (illegal)
                logger.debug(f'Illegal subfolders {objctBranch}: {self.path}')
                return # terminate without changes
            #Set it to remaining str element instead of a list of length 1
            objctBranch = objctBranch[0]          

        # Archived Observation
        # objctBranch's name must be OBJCT_DIR, OTHER_DIR must exist      
        elif OBJCT_DIR and OTHER_DIR in branchList:
            objctBranch = OBJCT_DIR
        # Violates structrure
        else:
            logger.debug(f'Improper archived subfolder structure: {self.path}')
            return # terminate without changes

        #objctBranch is known at this point, and no violations

        try:
            # Files in objctBranch (will be appended at the end)
            # forces objctBranches into fourth order.
            # Remember, fitsDirList holds paths, branchList holds foldernames
            # and they both have the same order (indexes)
            log.heading3(objctBranch, logger) # for more readable logs
            objctFiles = self.parseFitsBranch(fitsDirList[branchList.index(objctBranch)])
            
            # Import self.objct (only objctBranch files have it, rest have
            # their foldername in lowercase) 
            self.objct = objctFiles[0].hdr['OBJECT'] # all the same anyway
            # Import self.tlscp
            self.tlscp = objctFiles[0].hdr['TELESCOP']
                
            # Import all branches into tree (except OTHER_DIR, has no fits file),
            # after checking 'TELESCOP' cards are consistent
            # Note: can't iterate numerically, in case non-lexicographic objctBranch
            for branch in [BIAS_DIR, DARK_DIR, FLAT_DIR]:
                log.heading3(branch, logger) # for more readable logs
                fitsBranchFiles = self.parseFitsBranch(fitsDirList[branchList.index(branch)])
                if self.tlscp == fitsBranchFiles[0].hdr['TELESCOP']: # all the same
                    self.fitsTree.append(fitsBranchFiles)
                else:
                    self.fitsTree = []
                    self.objct = None
                    self.tlscp = None
                    return# terminate without changes
            # OBJCT_DIR branch added lastly.        
            self.fitsTree.append(objctFiles)
            self.branchList = [BIAS_DIR, DARK_DIR, FLAT_DIR, objctBranch, OTHER_DIR]
        except TypeError:
            logger.warning(f'Subfolders couldn\'t be parsed: {self.path}', exc_info=True)
            return # terminate without changes


    def parseFitsBranch(self, dirPath):
        '''Parses FitsFile objects within a branch (subfolder). Members
        objct and tlscp must be consistent
        :param dirPath: path to directory of branch (subfolder)
        :returns: list of FitsFile objects
        '''
        fitsList = []     # FitsFile objects
        fitsPathList = sorted(glob.glob(f'{dirPath}/*.fit', recursive=False))

        # If no '.fit' files in folder
        if not fitsPathList:
            logger.debug(f'Has no fits files: {dirPath}')
            return
        # If has fits file(s)
        else:
            # Create first FitsFile object, then append to fitsList
            try:
                fitsList.append(FitsFile(fitsPathList[0], mode=self.mode))
            except Exception:
                logger.warning(f'Could not create FitsFile: {fitsPathList[0]}', exc_info=True)

            if self.isNew:
                # Check whether file was archived, albeit this Obsv being new
                if not fitsList[0].isNew:
                    logger.debug(f'Archived FitsFile in fresh Obsv: {fitsList[0].path}')
                    return
            else:
                #Check whether file is fresh, albeit this Obsv being archived
                if self.isNew != fitsList[0].isNew:
                    logger.debug(f'Fresh FitsFile in archived Obsv: {fitsList[0].path}')
                    return
                # Check whether file is foreign
                if self.hash != fitsList[0].obsvHash:
                    logger.debug(f'Foreign FitsFile (first): {fitsList[0].path}')
                    return
                

            # Compare all other members to the first (checked just now);
            # terminate if any inconsistency found
            for j in range(1, len(fitsPathList)):
                # Create FitsFile objects one by one
                try:
                    fitsList.append(FitsFile(fitsPathList[j], self.mode))
                except Exception:
                    logger.warning(f'Could not create FitsFile: {fitsPathList[0]}', exc_info=True)

                # Check if different (if new, obsvHash equal None in both)
                if (   fitsList[0].obsvHash        != fitsList[j].obsvHash
                    or fitsList[0].isNew           != fitsList[j].isNew
                    or fitsList[0].hdr['TELESCOP'] != fitsList[j].hdr['TELESCOP']
                    or fitsList[0].hdr['OBJECT']   != fitsList[j].hdr['OBJECT']
                ):
                    logger.debug(f'Mixed FitsFile: {fitsList[j].path}')
                    return

        # Provided data were consistent]
        return fitsList


    def getFitsList(self):
        '''Makes it easier to loop through all FitsFile objects in member fitsTree
        :returns: a list containing all FitsFile objects 
        '''
        return [fitsFile for branch in self.fitsTree for fitsFile in branch]


    def update(self):
        '''Not for stand-alone use, method for Obsv.insert(). Updates all
        FitsFile objects in member fitsTree, provides them with obsvHash info.
        :returns: True if successful
        '''
        # Update all files in tree (see: reserved item numbers per subfolder in aukr.omal.const)
        if (self.mode == 'update'):
            if (self.fitsTree):
                # for all branches except OTHER_DIR
                for j in range(0, 4): 
                    log.heading3(self.branchList[j], logger) # for more readable logs
                    # for files in current branch
                    for k in range(0, len(self.fitsTree[j])):
                        # (Obsv.hash + shift by 1) + preceding reserved slots + k'th file in branch 
                        fileHash = ((self.hash + 1) + j*MAX_CONTROL_ITEM + k)
                        # If cannot update all files, will return False (no damage yet)
                        if not self.fitsTree[j][k].update(fileHash):
                            return False
            else:
                logger.debug(f'Couldn\'t update Obsv (fitsTree empty): {self.path}')
                return False
        else:
            logger.debug(f'Couldn\'t update Obsv (mode={self.mode}): {self.path}')
            return False

        logger.debug(f'Updated Obsv: {self.path}')
        return True


    def insert(self):
        '''Inserts non-duplicate Obsv into archiveDB, unless daily limit reached.
        :returns: True if successful
        '''
        # Check if self.hash is occupied in database
        hash = self.hash # for iteration over observations in a day, if any
        count = MAX_OBSV_PER_DAY # if count zero max trial is reached
        # Either query returns '' (effectively False), or count becomes 0
        # If duplicate is found before those, fallback
        while count and (archiveDB.queryObsv(hash, "*")):
            # Assuming there shall be one observation per telescope per day.
            # if there exists an observation in database for the telescope,
            # label current observation as duplicate; else iterate for
            # number of observations allowed per day.                
            if archiveDB.queryObsv(hash, "TELESCOP") and (archiveDB.queryObsv(hash, "TELESCOP")[0][0] == self.tlscp):
                logger.warning(f'Obsv ALREADY IN ARCHIVE: {self.name}, (REF={calc.ref(hash)})')
                return False
            else:
                hash = hash + MAX_ITEM_PER_OBSV
                count -= 1
        if not count:
            logger.warning(f'Obsv limit reached for the day: {self.date}')
            return False
        else:
            logger.info(f'Obsv not duplicate, inserting: {self.name}')
            self.hash = hash # empty slot found is taken
        
        # Update FitsFiles in tree, provided Obsv is not duplicate
        if self.update():
            # Insert into tables obsv and fits
            if archiveDB.insertObsv(self):
                logger.debug(f'Obsv into archiveDB: {self.path}')
                for branch in self.fitsTree:
                    #logger.debug(f'Branch: {os.path.dirname(branch[0].path)}')
                    log.heading3(os.path.basename(os.path.dirname(branch[0].path)), logger) # for more readable logs
                    for fitsFile in branch:
                        logger.debug(f'FitsFile: {fitsFile.date} {fitsFile.name}')
                        # Write updated files into database:
                        # if somehow fitsFile not inserted delete all changes and return False
                        if not archiveDB.insertFits(fitsFile):
                            archiveDB.deleteObsv(self)
                            logger.warning(f'FitsFile insertion failed (rolling back): {fitsFile.path}')
                            return False
            else:
                logger.warning(f'Obsv insertion failed: {self.name}')
                return False
        else:
            logger.warning(f'Could not update: {self.name}')
            return False

        logger.info(f'Obsv insertion succeeded: {self.name}')
        return True
# End of Obsv class
