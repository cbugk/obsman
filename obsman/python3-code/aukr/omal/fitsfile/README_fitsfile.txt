This module  includes FitsFile class, for modelling .fit files.
It also consists of a method in class, whose duty is to upgrade the file.
Whole purpose of it was to help automate observation management, as package
OMAL stands for.

The way to update that script lays on:
    -- updating aukr.omal.const.HDR_KEYS list
    -- updating aukr.omal.sqlitedb.ObservatoryDB class' create and insert functions
    -- updating the FitsFile class
  as necessary. This task, although seems a bit overwhelming, is not expected to harm
  present functionality (hoping modularity was designed well enough initially)

Task above should be the only relatively frequent change there is to be performed. Other parts
  were, I dare say, overthought; which renders them either fundamentally wrong, or implemented good enough.
