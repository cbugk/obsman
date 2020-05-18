import aukr.omal.functions as fcns
from aukr.omal.args import args
from aukr.omal.log import getLogger

logger = getLogger(__name__)

for ref in args.rmRefs:
    if (fcns.removeObsvByRef(ref)):
        logger.debug(f'Removed Obsv: {ref}')
    else:
        logger.debug(f'Could not remove: {ref}')
