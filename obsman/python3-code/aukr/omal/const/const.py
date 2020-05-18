### CONSTANTS
# Positive Hexadecimal Observation Identifiers (REF, hashable to integer
# uniquely are used for mapping items (MAX_ITEM_PER_DAY many items refer to a
# unique day). However, date is not uniquely transformed to REF (except for
# that day's first-item, which is default Obsv.ref for new observations,
# by design)
#
# e.g. 2036-03-17_D27A2D15 (9th Obsv, 11541rd item); Parent Obsv: D27A0000.
# Check calcValidDateAndItem() function for details
# 
# Note it is expected to have single observation insertions per day and
# many of reserved hashes to be wasted. Even though this approach wastes a
# quite bit of references, makes cristal clear what is referred, and uses 
# only basic aritmetics; while having long enough lifetime with enough
# room for expansion and/or exceptional cases (like 16 observations
# in a day, or 16384 files per observation)


### aukr.omal.[calc, fitsfile, obsv]
OBS_ALT = 1256.69   # Altitude of AUKR Observatory
MAX_DAYS_APART_LIMIT = 2 # Obsv can include normalization-data from n-days apart

#Please update/retire service before: 2044-01-16
YEAR_2K             = 2000 # calendar start, easier hash->'date' conversion
REF_LENGTH          = 8    # between 0000000 and fffffff (hexadecimals)
MAX_ITEM_PER_OBSV   = 16384
MAX_OBSV_PER_DAY    = 16
MAX_ITEM_PER_DAY    = (MAX_ITEM_PER_OBSV * MAX_OBSV_PER_DAY)

# Subfolders in a project, note that their alphabetical order don't play a role.
# unless forced on you, store future features in OTHER_DIR, that was the
# whole purpose in creating it in the first place.
# For the maintainer: enumeration could be handy.
BIAS_DIR  = 'Bias'
DARK_DIR  = 'Dark'
FLAT_DIR  = 'Flat'
OBJCT_DIR = 'Object'
OTHER_DIR = 'Other'

# 1024(Bias) + 1024(Dark) + 1024(Flat) + 102400(Objct) + 383(other) = 16384('0' is for Obsv)
MAX_CONTROL_ITEM    = 1024 # items reserved for BIAS_DIR, DARK_DIR, FLAT_DIR each
MAX_OBJCT_ITEM      = 10240 # items reserved for OBJCT_DIR
MAX_OTHER_ITEM      = 3071 # items reserved for OTHER_DIR


### aukr.omal.args
default_importdir  = '/obsman/tmp-files/upload'
default_archdir     = '/obsman/obsv_arch'
default_dbfile      = '/obsman/aukr_obsv.db'
default_logfile     = ''


### aukr.omal.sqlitedb
# Tablenames used within database (aukr.omat.sqlite.archiveDB)
TABLE_OBSV = 'obsv'
TABLE_FITS = 'fits'

# Keyword list below is closely bound to aukr.omat.sqlite functions.
# do not edit unless updating/debugging
HDR_KEYS = [
    'SIMPLE',   # bool
    'BITPIX',   # int
    'NAXIS',    # int
    'NAXIS1',   # int
    'NAXIS2',   # int
    'BSCALE',   # float
    'BZERO',    # float
    'DATE-OBS', # str
    'EXPTIME',  # float
    'EXPOSURE', # float
    'SET-TEMP', # float
    'CCD-TEMP', # float
    'XPIXSZ',   # float
    'YPIXSZ',   # float
    'XBINNING', # int
    'YBINNING', # int
    'XORGSUBF', # int
    'YORGSUBF', # int
    'READOUTM', # str
    'FILTER',   # str
    'IMAGETYP', # str
    'FOCUSPOS', # int
    'FOCUSSSZ', # float
    'OBJCTRA',  # str
    'OBJCTDEC', # str
    'OBJCTALT', # str
    'OBJCTAZ',  # str
    'OBJCTHA',  # str
    'SITELAT',  # str
    'SITELONG', # str
    'JD',       # float
    'JD-HELIO', # float
    'AIR-MASS', # float
    'FOCALLEN', # float
    'APTDIA',   # float
    'APTAREA',  # float
    'SWCREATE', # str
    # the image # <class 'astropy.io.fits.header._HeaderCommentaryCards'>
    'SBSTDVER', # str
    'OBJECT',   # str
    'TELESCOP', # str
    'INSTRUME', # str
    'OBSERVER', # str
    'NOTES',    # str
    'FLIPSTAT', # str
    'SWOWNER',  # str
    'BJD-TDB',
    'MIDTIME',
    'LST',
    'PI',
    'PRJTNUM',
    'GAIN',
    'PSCALE',
    'EPOCH',
    'RDNOISE',
    'AUKR-REF'
]
