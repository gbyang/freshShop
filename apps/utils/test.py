import re

from MxShop.settings import MOBILE_REGEX

if not re.match(MOBILE_REGEX, '15889607783'):
    print('no')
else:
    print('yes')