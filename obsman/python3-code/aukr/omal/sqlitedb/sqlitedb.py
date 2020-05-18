import sqlite3, os
from ..args import args
from ..log  import getLogger
from ..const import TABLE_FITS, TABLE_OBSV, HDR_KEYS
from .. import calc

# Create module's logger
logger = getLogger(__name__)


# IMPORTANT: put KEYWORDS in double-quotes, some have special characters (e.g. 'DATE-OBS').
# Note: Use ..fits.printFitsHdr() for inspectation of fits files

### OBSERVATION
# Inserts row to observation table
# see obsCreateTable for datatypes

#
class ObservatoryDB:
    '''class for handling sqlite3 database file
    '''
    conn        = None
    cursor      = None
    obsvTable   = None
    fitsTable   = None

    def __init__(self, dbfile, obsvTable, fitsTable):
        ''':param dbfile: path for .db file
        :param obsvTable: tablename for Obsv objects
        :param fitsTable: tablename for FitsFile objects
        '''
        self.conn       = sqlite3.connect(dbfile)
        self.cursor     = self.conn.cursor()
        self.obsvTable  = obsvTable
        self.fitsTable  = fitsTable


#    def __query(self, string):
#        '''This method is for internal use only. Lets any command to be executed
#        in sqlite3 database.
#        :param string: SQL command to be issued.
#        :returns: result of the query (list, print for details)
#        '''
#        self.cursor.execute(string)
#        return self.cursor.fetchall()

    
    def queryHashRange(self, column, lowerHash, upperHash):
        '''Returns column(s) which are in range of specified hashes
        :param lowerHash: lowest hash allowed
        :param upperHash: upper limit of hashes, is forbidden
        :returns: result of the query (list, print for details)
        '''
        self.cursor.execute(
            f'SELECT {column} FROM obsv WHERE ({lowerHash}<=HASH and HASH<{upperHash})'
        )
        return self.cursor.fetchall()

    #
    def queryObsv(self, hash, column):
        ''':param hash: hash for Obsv to be queried
        :param column: column(s) to be fetched
        :returns: True if successful
        '''
        self.cursor.execute(
            f'SELECT {column} FROM {self.obsvTable} WHERE HASH = {hash};'
        )
        return self.cursor.fetchall()

    #
    def queryFits(self, hash, column):
        ''':param hash: hash for FitsFile to be queried
        :param column: column(s) to be fetched
        :returns: True if successful
        '''
        self.cursor.execute(
            f'SELECT {column} FROM {self.fitsTable} WHERE HASH = {hash};'
        )
        return self.cursor.fetchall()

    #
    def insertObsv(self, obsv):
        ''':param obsv: Obsv object to be inserted into database
        :returns: True if successful
        '''
        try:
            self.cursor.execute(
                f'INSERT INTO {self.obsvTable} VALUES ('
                f'"{obsv.hash}",'
                f'"{obsv.date}",'
                f'"{obsv.tlscp}",'
                f'"{obsv.objct}",'
                f'"{obsv.path}"'
                f');'
            )
            self.conn.commit()
            return True
        except Exception as e:
            logger.warning(f'Could not insert: {e}')
            return False



    # Not for stand-alone use, to  be used when an Obsv is being inserted
    def insertFits(self, fitsFile):
        ''':param fitsFile: FitsFile object to be inserted into database
        :returns: True if successful
        '''
        try:
            hdrItems = ''
            for j in range(1, len(HDR_KEYS)): # 'SIMPLE' boundary cases
                hdrItems += (f',"{fitsFile.hdr[HDR_KEYS[j]]}"' if HDR_KEYS[j] in fitsFile.hdr else f',"NULL"')

            self.cursor.execute(
                f'INSERT INTO {self.fitsTable} VALUES ('
                f'"{fitsFile.hash}"'
                f',"{fitsFile.obsvHash}"'
                f',"{fitsFile.path}"' # absolute path of file
                # HEADER KEYWORDS BELOW
                # Insert integer inplace of boolean (SQLite3 specific)
                f',"{(1 if fitsFile.hdr["SIMPLE"] else 0)}"'
                # Insert from second element of HDR_KEYS
                f'{hdrItems}'
                f');'
            )
            self.conn.commit()
            return True
        except Exception as e:
            logger.warning(f'Could not insert: {fitsFile.path}')
            logger.warning(e)
            return False

    def deleteObsv(self, obsv):
        '''Deletes entries for Obsv and corresponding FitsFiles from their respective tables
        :param obsv: Obsv object to be deleted
        :returns: True if successful
        '''
        try:
            self.cursor.execute(
                f'DELETE FROM {self.obsvTable} WHERE "HASH" = {obsv.hash}'
            )
            self.cursor.execute(
                f'DELETE FROM {self.fitsTable} WHERE "OBSV-HASH" = {obsv.hash}'
            )
            self.conn.commit()
            return True
        except Exception as e:
            logger.warning(f'{e}')
            return False

    def deleteObsvByRef(self, ref):
        '''Deletes entries for Obsv and corresponding FitsFiles from their respective tables
        :param ref: ref of Obsv to be deleted
        :returns: True if successful
        '''
        try:
            self.cursor.execute(
                f'DELETE FROM {self.obsvTable} WHERE "HASH" = {calc.hash(ref)}'
            )
            self.cursor.execute(
                f'DELETE FROM {self.fitsTable} WHERE "OBSV-HASH" = {calc.hash(ref)}'
            )
            self.conn.commit()
            return True
        except Exception as err:
            #logger.warning(f'{e}')
            exception_type = type(err).__name__
            print(exception_type)
            return False

    # Creates single-table for observations, with four essential columns.
    # Shall be used for creation/migration only.
    def createObsvTable(self): #returns boolean
        '''Creates table for storing Obsv object information (named as self.obsvTable value)
        :returns: True if successful
        '''
        try:
            self.cursor.execute(
                f'CREATE TABLE IF NOT EXISTS {self.obsvTable} (\n'
                f'"HASH" INTEGER PRIMARY KEY\n'
                f',"DATE" TEXT NOT NULL\n' # YYYY-MM-DD, also foldername in 
                f',"TELESCOP" TEXT NOT NULL\n'
                f',"OBJECT" TEXT NOT NULL\n'
                f',"PATH" TEXT NOT NULL\n'
                f');'
            )
            self.conn.commit()
            return True
        except Exception as e:
            logger.warning(f'{e}')
            return False


    # Creates single-table for FITS-Headers
    # Shall be used at creation/migration only
    def createFitsTable(self): #returns boolean
        '''Creates table for storing FitsFile object information (named as self.fitsTable value)
        :returns: True if successful
        '''
        try:
            self.cursor.execute(
            #print(   # for debugging when table not created, print the string
                f'CREATE TABLE IF NOT EXISTS {self.fitsTable} (\n'
                f'"HASH" INTEGER PRIMARY KEY,\n' # file's hash
                f'"OBSV-HASH" INTEGER NOT NULL,\n' # hash for parent Obsv
                f'"PATH" TEXT NOT NULL,\n' # absolute path of file
                # HEADER KEYWORDS BELOW (AUKR-REF in header for archived files)
                f'"{HDR_KEYS[0]}" INTEGER,\n' #for bool
                f'"{HDR_KEYS[1]}" INTEGER,\n' 
                f'"{HDR_KEYS[2]}" INTEGER,\n'
                f'"{HDR_KEYS[3]}" INTEGER,\n'
                f'"{HDR_KEYS[4]}" INTEGER,\n' 
                f'"{HDR_KEYS[5]}" REAL,\n'           #float
                f'"{HDR_KEYS[6]}" REAL,\n'           #float
                f'"{HDR_KEYS[7]}" TEXT NOT NULL,\n'  #str   "DATE-OBS"
                f'"{HDR_KEYS[8]}" REAL,\n'           #float
                f'"{HDR_KEYS[9]}" REAL,\n'           #float
                f'"{HDR_KEYS[10]}" REAL,\n'          #float
                f'"{HDR_KEYS[11]}" REAL,\n'          #float
                f'"{HDR_KEYS[12]}" REAL,\n'          #float
                f'"{HDR_KEYS[13]}" REAL,\n'          #float
                f'"{HDR_KEYS[14]}" INTEGER,\n' 
                f'"{HDR_KEYS[15]}" INTEGER,\n' 
                f'"{HDR_KEYS[16]}" INTEGER,\n' 
                f'"{HDR_KEYS[17]}" INTEGER,\n' 
                f'"{HDR_KEYS[18]}" TEXT,\n'          #str
                f'"{HDR_KEYS[19]}" TEXT,\n'          #str
                f'"{HDR_KEYS[20]}" TEXT,\n'          #str
                f'"{HDR_KEYS[21]}" INTEGER,\n' 
                f'"{HDR_KEYS[22]}" REAL,\n'          #float
                f'"{HDR_KEYS[23]}" TEXT,\n'          #str
                f'"{HDR_KEYS[24]}" TEXT,\n'          #str
                f'"{HDR_KEYS[25]}" TEXT,\n'          #str
                f'"{HDR_KEYS[26]}" TEXT,\n'          #str
                f'"{HDR_KEYS[27]}" TEXT,\n'          #str
                f'"{HDR_KEYS[28]}" TEXT,\n'          #str
                f'"{HDR_KEYS[29]}" TEXT,\n'          #str
                f'"{HDR_KEYS[30]}" REAL,\n'          #float
                f'"{HDR_KEYS[31]}" REAL,\n'          #float
                f'"{HDR_KEYS[32]}" REAL,\n'          #float
                f'"{HDR_KEYS[33]}" REAL,\n'          #float
                f'"{HDR_KEYS[34]}" REAL,\n'          #float
                f'"{HDR_KEYS[35]}" REAL,\n'          #float
                f'"{HDR_KEYS[36]}" TEXT,\n'          #str
                # the image     #astropy.io.fits.header._HeaderCommentaryCards
                f'"{HDR_KEYS[37]}" TEXT,\n'          #str
                f'"{HDR_KEYS[38]}" TEXT NOT NULL,\n' #str "OBJECT"
                f'"{HDR_KEYS[39]}" TEXT NOT NULL,\n' #str "TELESCOP"
                f'"{HDR_KEYS[40]}" TEXT,\n'          #str
                f'"{HDR_KEYS[41]}" TEXT,\n'          #str
                f'"{HDR_KEYS[42]}" TEXT,\n'          #str
                f'"{HDR_KEYS[43]}" TEXT,\n'          #str
                f'"{HDR_KEYS[44]}" TEXT,\n'          #str
                f'"{HDR_KEYS[45]}" TEXT,\n'          #float
                f'"{HDR_KEYS[46]}" TEXT,\n'          #str
                f'"{HDR_KEYS[47]}" TEXT,\n'          #str    
                f'"{HDR_KEYS[48]}" TEXT,\n'          #str #was null in sample
                f'"{HDR_KEYS[49]}" TEXT,\n'          #str #was null in sample
                f'"{HDR_KEYS[50]}" TEXT,\n'          #float
                f'"{HDR_KEYS[51]}" TEXT,\n'          #float
                f'"{HDR_KEYS[52]}" TEXT,\n'          #float
                f'"{HDR_KEYS[53]}" TEXT,\n'          #float
                f'"{HDR_KEYS[54]}" TEXT NOT NULL\n'  #str   "AUKR-REF"
                # END of HEADER KEYWORDS
                f');'
            )
            self.conn.commit()
            return True
        except Exception as e:
            logger.warning(f'{e}')
            return False

    


# Create database object to connect provided sqlite3.db file
archiveDB  = ObservatoryDB(args.dbfile, TABLE_OBSV, TABLE_FITS)
if not archiveDB.createFitsTable():
    logger.info(f'Table "{TABLE_FITS}" could not be created')
if not archiveDB.createObsvTable():
    logger.info(f'Table "{TABLE_OBSV}" could not be created')
