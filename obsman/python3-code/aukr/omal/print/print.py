# Author: Celil Bugra Karacan (psykobug@github)
# Last updated: 2019-09-28
# version: v.1.0.0

from ..log import getLogger

# Create module's logger
logger = getLogger(__name__)


def fitsHeader(hdul): # hudl = astropy.io.fits.open(filePath, mode='readonly')
    '''Function for inspecting data-types within header, and and example for
    how to parse information. (note: header[keyIndex] == header[KEYWORD])
    prefer KEYWORD (than keyIndex) in general as column order may change in future.
    use print(repr(header)) INSTEAD.
    '''
    hdul.info()
    header = hdul[0].header
    print("-----------------------------------StartPrint-----------------------------------")
    keyIndex = 0
    for KEYWORD in header:
        keyIndex += 1
        # e.g.  4  NAXIS1    1024    <class 'int'>    /fastest changing axis
        print( f"{keyIndex:02}  {KEYWORD:8}\t{str(header[KEYWORD]):20}\t{str(type(header[KEYWORD])):15}\t/{header.comments[KEYWORD]}")
    print("-------------------------------------Finish-------------------------------------")
    return
