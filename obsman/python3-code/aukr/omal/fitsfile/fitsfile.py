# Uses upgrade-script from 2019-Summer-Interns: Mirzhalilov and Khuzhakulov
#  ( see: Fits.updateScript() )

# For FitsFile.upgradeScript() method
from astropy import time, coordinates as coord
import astropy.io.fits as fits
import os
import datetime
# For rest
from ..log import getLogger
from .. import calc
from ..const import OBS_ALT, MAX_DAYS_APART_LIMIT

# Create module's logger
logger  = getLogger(__name__)


### Class for FITS files within observations
# Created and accessed by Obsv objects only
# raises SomeError unless constructed. This was chosen over 'return None', because
# this seems more efficient than checking (almost always) previously checked
# user input.
class FitsFile:
    '''Class representing FITS files (.fit). Please modify upgradeScript()
    method as required for handling new observation headers
    '''
    
    def __init__(self, path, mode='readonly'):
        ''':param path: path to fits file to be parsed (can be relative)
        :param mode: indicates if file will be modified (choose 'readonly', 'update')
        '''
        self.mode = None  # from constructor
        self.path = None  # from constructor, made absolute
        self.name = None  # from self.path, full name of file (.fit included)
        self.hdul = None  # from astropy.io.fits.open(path, mode), HDUList, to flush() changes made
        self.hdr  = None  # from self.hdul[0].header, Primary HDU's header, parse below params
        self.date = None  # from self.header, inserted at observation (parsed as "YYYY-MM-DD")
        self.hash = None  # from AUKR-REF in self.header, OR given by Obsv.update() at creation
        self.obsvHash = None # calculated from self.hash
        self.isNew = None # from self.header, true if 'AUKR-REF' field exists


        # Set self.path (absolute) and self.name
        self.path = os.path.abspath(path)
        self.name = os.path.basename(path)

        # Set self.mode
        if (mode == 'update') or (mode == 'readonly'):
            self.mode = mode
        else:
            logger.debug(f"Use 'update' or 'readonly', mode: {mode}")
            raise ValueError("Use 'update' or 'readonly'")

        # Import header and HDUList from file
        self.hdul = fits.open(self.path, mode=self.mode)
        self.hdr  = self.hdul[0].header
        
        # Make sure must haves (OBJECT, TELESCOP, DATE-OBS) cards  exist 
        if ('OBJECT' not in self.hdr):
            logger.debug(f'Who deleted OBJECT from header?: {self.name}')
            raise ValueError('FITS file must have \'OBJECT\' field')
        if ('TELESCOP' not in self.hdr):
            logger.debug(f'Who deleted TELESCOP from header?: {self.name}')
            raise ValueError('FITS file must have \'TELESCOP\' field')
        if ('DATE-OBS' not in self.hdr):
            logger.debug(f'Who deleted DATE-OBS from header?: {self.name}')
            raise ValueError('FITS file must have \'DATE-OBS\' field')

        # Sets self.date, as 'YYYY-MM-DD' from 'DATE-OBS' in fits header.
        # 'DATE-OBS' must be in form '2000-01-01T23:59:59
        if calc.isDate(self.hdr['DATE-OBS'], format='%Y-%m-%dT%H:%M:%S'):
            self.date = self.hdr['DATE-OBS'].split('T')[0]
        else:
            logger.debug(f'DATE-OBS is misformatted: {self.name}')
            raise ValueError('DATE-OBS is misformatted')
       
        # Set self.ref, as AUKR-REF in fits header, set self.isNew accordingly.
        # leave ref as is for brand-new observations.
        if 'AUKR-REF' not in self.hdr:
            self.isNew = True
        else:
            ref = self.hdr['AUKR-REF']
            (date, item) = calc.validDateAndItem(ref) #may throw ValueError
            if calc.areWithinRange(self.date, date, MAX_DAYS_APART_LIMIT):
                self.hash = calc.hash(ref)
                # (FitsFile's hash) is its (Obsv's hash) + (item number) 
                self.obsvHash = (self.hash - item)
                self.isNew = False
            else:
                logger.debug(f'{date} {ref} contradicts {self.date} {self.name}')
                raise ValueError('Date and Ref mismatch')
            
        # Provided everything went well
        logger.info(f'Created FitsFile: {self.date} | {self.name}')


    def update(self, newHash):
        '''Requires self.mode='update'. Fits header is rendered archive-ready;
        unless was archived ("AUKR-REF" in header). New fits headers upgraded in
        the process
        :returns: True if succeeds
        '''
        if self.mode != 'update':
            logger.debug(f'Couldn\'t update header (readonly): {self.path}')
            return False

        if not self.isNew:
            logger.debug(f'Couldn\'t update header (AUKR-REF field exists): {self.path}')
            return True
        # Right now: self.ref=None and self.isNew=True, see parseRef if in doubt

        # Proper way of importing with validation is bellow:
        #(newDate, newItem) = calc.validDateAndItem(calc.ref(newHash))
        # However only Obsv objects interract with FitsFile
        # thus, trusting source
        (newDate, newItem) = calc.dateAndItem(newHash)
        #newItem non-zero and dates are within max seperation limit
        if newItem and (calc.areWithinRange(newDate, self.date, MAX_DAYS_APART_LIMIT)):
            self.hash     = newHash
            self.obsvHash = (self.hash - newItem)
        else:
            logger.debug(f'hdr not updated({calc.dateAndItem(newHash)[0]}|{newHash} contradicts {self.date}|{self.name})')
            return False
        
        isUpgraded = ''
        if self.upgradeScript():
            isUpgraded = 'Upgraded'
        
        # Add card for ref, and set
        self.hdr.append('AUKR-REF')
        self.hdr.set('AUKR-REF', value=calc.ref(self.hash), comment='file reference in Ankara University')

        # Save changes to file (hdul closed after getting out of scope,
        # for explicitly closing: fits.HDUList.close(self.hdul) )
        fits.HDUList.flush(self.hdul)

        logger.info(f'Updated ({isUpgraded})  FitsFile: {self.date} {self.name}')
        return True

    # Built on script originally written by Mirzhalilov and Khuzhakulov (2019 Summer)
    # Keep this method at the end of class for convienience/seperation
    def upgradeScript(self):
        '''Script by Mirzhalilov and Khuzhakulov, upgrades observations to
        standard they proposed (2019 Summer Internship). Not applied, if
        "BJD-TDB or "MIDTIME" keywords present in fits header.
        '''
        if ('BJD-TDB' in self.hdr) or ('MIDTIME' in self.hdr):
            logger.debug(f'Already  upgraded: {self.date} {self.name}')
            return False

        #---Script--Start
        # Gets the value with the corresponding key
        JD_UTC   = self.hdr['JD']
        RA       = self.hdr['OBJCTRA'].split()
        DEC      = self.hdr['OBJCTDEC'].split()
        obs_long = self.hdr['SITELONG'].split()
        obs_lat  = self.hdr['SITELAT'].split()

        # Formatting RA in (h)our, (m)inute, (s)econd format
        RA = f'{RA[0]}h{RA[1]}m{RA[2]}s'
        # Formatting DEC in (d)egree, arc(m)inute and arc(s)econd
        DEC = f'{DEC[0]}d{DEC[1]}m{DEC[2]}s'
        # Converts obs_long and obs_lat into float
        obs_long = (((float(obs_long[2]) / 60) + float(obs_long[1])) / 60) + float(obs_long[0])
        obs_lat = (((float(obs_lat[2]) / 60) + float(obs_lat[1])) / 60) + float(obs_lat[0])
        # Setting Coordinate of observing object in the sky
        target = coord.SkyCoord(RA, DEC, frame='icrs')
        # Setting coordinate of observatory
        observatory = coord.EarthLocation(obs_long, obs_lat, OBS_ALT)
        # Creating time object by using JD taken from header which is beginning of observation
        JD_UTC = time.Time(JD_UTC, format='jd', scale='utc', location=observatory)
        # Adding half of exposure time to JD in order to calculate time of middle of the observation
        New_JD = JD_UTC + datetime.timedelta(seconds=float(self.hdr['EXPTIME'])/2)
        # Converting JD to UTC
        t_jd = time.Time(New_JD, format='jd', scale='utc')
        MIDTIME = t_jd.iso
        # Creating new time by using MIDTIME and Location of the observatory to calculate LST
        t1 = time.Time(MIDTIME,scale='utc',location=observatory)
        LST = t1.sidereal_time('mean')
        # target time difference in the time variable New_JD  between traveling to the centre of solar sytstem and traveling to the earth
        ltt_bary = New_JD.light_travel_time(target)
        # Firstly, changing New_JD from UTC unit to TDB and then adding to the time difference that was calculated above
        time_barycentre = New_JD.tdb + ltt_bary
        real_bjd = time_barycentre.value

        # Create cards for keywords
        self.hdr.append('BJD-TDB')
        self.hdr.append('MIDTIME')
        self.hdr.append('LST')
        self.hdr.append('PI')
        self.hdr.append('PRJTNUM')
        self.hdr.append('GAIN')
        self.hdr.append('PSCALE')
        self.hdr.append('EPOCH')
        self.hdr.append('RDNOISE')

        # Set new cards created
        self.hdr.set('BJD-TDB',  value=real_bjd, comment='Dynamic Barycentric Julian Day')
        self.hdr.set('MIDTIME',  value=MIDTIME , comment='DATE-OBS of Mid Exposure Time in UT')
        self.hdr.set('LST'    ,  value=str(LST), comment='Local Sidereal Time' )
        self.hdr.set('PI'     ,                  comment='Principle Investigator')
        self.hdr.set('PRJTNUM',                  comment='Project Number')
        self.hdr.set('GAIN'   ,  value=1.5     , comment='e-/count')
        self.hdr.set('PSCALE' ,  value=0.754   , comment='\'\'/pixel')
        self.hdr.set('EPOCH'  ,  value=2000.0    )
        self.hdr.set('RDNOISE',  value=11.5    , comment='e-')
        #---Script--End

        return True
#End of FitsFile class
