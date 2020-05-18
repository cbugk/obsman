This is the alpha release of OMAL(Observation Management and Archiving Library)
[named after the long-lasting Pontic Greek dance, in the hopes it too shall last]

As of September 2019, this package is intended for local use only within AUKR.
Later versions might be released online (e.g. github, gitlab etc.)

--PRESENT-BRANCHES:
    - args       -- list of variables provided through cli (aukr.omal.args.args)
                      check module for alternative method of manually setting

    - calc       -- functions calculating ref-hash-dateItem conversions; or checking valdity
                      of their inputs

    - const      -- contant values which do not change throughout a version of the library


    - filesys    -- functions handling files/folders within archdir


    - fitsfile   -- class FitsFile defined (represents .fit files archived or not)
                      also script to upgrade newly recorded .fit files (check README in there)

    - log        -- function to create loggers per module ( aukr.omal.log.getLogger(__name__) )


    - obsv       -- class Obsv defined (represents observation files arhcived or not)


    - sqlitedb   -- functions concerning SQLite3 (like inserting into, selecting from, etc.)


    and
    - functions  -- public interface of the library, for applications to be built on it

