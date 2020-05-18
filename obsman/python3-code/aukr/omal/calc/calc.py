import datetime, os
from ..const import REF_LENGTH, YEAR_2K, MAX_ITEM_PER_DAY, MAX_ITEM_PER_OBSV
from ..log import getLogger

# Create module's logger
logger  = getLogger(__name__)

# Functions for (REF)-(HASH)-(DATE & ITEM) conversions. Hash is the bridge
# between other two, and is also the database PRIMARY KEY.

def isDate(date, format='%Y-%m-%d'):
    '''Checks if provided string is a date.
    Invalid: '-2000-01-01', '2000-13-01', '2000-01-32'
    (check datetime.datetime for format info).

    :param date: string, default 'YYYY-MM-DD'
    :param format: (optional) default '%Y-%m-%d'
    :returns: True if date, False otherwise
    '''
    try:
        datetime.datetime.strptime(date, format)
        return True
    except ValueError:
        return False

def areWithinRange(date1, date2, range):
    '''Checks whether dates are not seperated more than the range
    (required for cases with bad normalization data).
    :param date1: 'YYYY-MM-DD'
    :param date2: 'YYYY-MM-DD'
    :param range: integer max number of days allowed
    :returns: True if within range, False otherwise
    '''
    (year1, month1, day1) = date1.split('-')
    (year2, month2, day2) = date2.split('-')
    if (year1 == year2) and (month1 == month2) and (abs(int(day1) - int(day2)) <= range):
        return True
    else:
        return False

def ref(hash):
    '''Handle the range of hash number beforehand.
    :param hash: integer, hash refering an Fits/Obsv object
    :returns: string, hex from hash (witout 0x)
    '''
    try:
        return hex(hash).split('x')[-1].zfill(REF_LENGTH).upper()
    except TypeError:
        logger.warning(f'hash ({hash}) is not a valid integer')

def hash(ref):
    '''Handle spaces and length beforehand.
    :param ref: ref of Fits/Obsv object
    :returns: integer, corresponding hash number (always calculated)
    '''
    try:
        return int(ref, 16) # throws ValueError if not hex (e.g. 'ASDFGH')
    except [ValueError, TypeError]:
        logger.warning(f'ref({ref}) is not a valid hex (without 0x)')

def itemZeroHash(date):
    '''Generates hash for initial Obsv for date.
    :param date: 'YYYY-MM-DD' (must be valid)
    :returns: integer, zeroth item of the day
    '''
    (year, month, day) = date.split('-') # throws ValueError if date=''
    # Crude approx. of days since YEAR_2K. 12 months, 31 days each makes
    # 372 days per year. Insert leading zeros even though not necessary
    # since bef year 2003, god damn time travellers.
    try:
        return ( ( (int(year)-YEAR_2K)*372 + (int(month)-1)*31 + (int(day)-1) ) * MAX_ITEM_PER_DAY )
    except:
        logger.warning(f'date({date}) has to be valid (YYYY-MM-DD)')
	
def dateAndItem(hash):
    '''Calculates responding date string and item number from hash (must be valid).
    :param hash: hash of Fits/Obsv object
    :returns: tuple ('YYYY-MM-DD', item)
    :raises ValueError: if ref is invalid
    '''
    # Construct a date string
    # Crude approx. of days since YEAR_2K.
    # 12 months 31 days each, makes 372 days per year
    try:
        itemNum = hash % MAX_ITEM_PER_OBSV # 0 means Obsv, else FitsFile
        daysSinceYear2k = hash // MAX_ITEM_PER_DAY
        yy = daysSinceYear2k // 372    # YY=19 for 2019 [v1.0.0]
        mm = ((daysSinceYear2k % 372) // 31) + 1
        dd = ((daysSinceYear2k % 372) % 31) + 1
        return (f'20{yy:02}-{mm:02}-{dd:02}', itemNum) # ensure leading zeros
    except Exception as e:
        logger.debug(f'Could not parse hash: {hash}')
        raise ValueError('Illegal REF (ref not hexadecimal)').with_traceback(e.__traceback__)

def validDateAndItem(ref):
    '''Calculates responding date string and item number from ref (validates ref).
    :param ref: ref of Fits/Obsv object
    :returns: tuple ('YYYY-MM-DD', item)
    :raises ValueError: if ref is invalid
    '''
    # Cannot be empty nor have spaces
    if (not ref) or (' ' in ref):
        logger.debug(f'Illegal REF (empty or has space(s)): {ref})')
        raise ValueError(f'Illegal REF (empty or has space(s)): {ref})')

    # Hash hexadecimal to decimal, after checking ref length
    if len(ref) != REF_LENGTH:
        logger.debug(f'Illegal REF (ref length not {REF_LENGTH})')
        raise ValueError(f'Illegal REF (ref length not {REF_LENGTH})')

    try:
        hashFromRef = hash(ref)
    except ValueError as e:
        logger.debug('Illegal REF (ref not hexadecimal)')
        raise ValueError('Illegal REF (ref not hexadecimal)').with_traceback(e.__traceback__)

    (dateOfRef, itemNum) = dateAndItem(hashFromRef)

    # Make sure ref points to a valid date (unlike 2005-02-29 or 2000-06-31)
    if isDate(dateOfRef):
        return (dateOfRef, itemNum)
    else:
        logger.debug(f'Illegal REF (does not point a real date): {dateOfRef}')
        raise ValueError('Illegal REF (does not point a real date)')
