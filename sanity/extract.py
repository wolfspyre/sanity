#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import date, datetime
import re

import cast
import fmt

__license__ = "MIT"
__version__ = "0.1"
__url__ = "http://github.com/smartt/sanity"
__doc__ = "A collection of misguided hacks."

def date_by_pattern(s, pattern, return_match_str=False):
    """
    >>> date_by_pattern('4/20/2014', '%m/%d/%Y')
    datetime.date(2014, 4, 20)

    >>> date_by_pattern('4/20', '%m/%d')
    datetime.date(2014, 4, 20)

    >>> date_by_pattern('4.20', '%m.%d')
    datetime.date(2014, 4, 20)

    >>> date_by_pattern('420', '%m/%d')

    """
    # tokenize..
    bits = s.split(' ')
    d = None

    # and scan..
    for bit in bits:
        try:
            parsed_date = datetime.strptime(bit, pattern).date()
        except ValueError:
            continue
        else:
            if parsed_date.year == 1900:
                d = date(datetime.now().year, parsed_date.month, parsed_date.day)
            else:
                d = date(parsed_date.year, parsed_date.month, parsed_date.day)

            break

    if return_match_str:
        # This is a little sketchy because we're returning a variable that is
        # conceptually just in the for-loop scope, but in python in sticks around.
        return d, bit
    else:
        return d

def just_numbers(s, decimals=False):
    """
    >>> just_numbers(123)
    '123'

    >>> just_numbers('123')
    '123'

    >>> just_numbers('1a2b3c')
    '123'

    >>> just_numbers('1-2-3-')
    '123'

    >>> just_numbers(None)
    ''

    >>> just_numbers(7)
    '7'

    >>> just_numbers('-1')
    '-1'

    >>> just_numbers(-3.14)
    '314'

    >>> just_numbers('-3.14')
    '-314'

    >>> just_numbers('-3.14', decimals=True)
    '-3.14'

    >>> just_numbers('-314', decimals=True)
    '-314'

    >>> just_numbers('314', decimals=True)
    '314'

    >>> just_numbers('-3.14.25')
    '-31425'

    >>> just_numbers('-3.14.25', decimals=True)
    '-3.14'

    >>> just_numbers('1,024')
    '1024'

    """
    if decimals:
        tmp = ''.join([i for i in cast.to_str(s) if ((i >= '0') and (i <= '9') or i == '.')])

        parts = tmp.split('.')

        try:
            output = '{a}.{b}'.format(a=parts[0], b=parts[1])
        except IndexError:
            output = parts[0]

    else:
        output = ''.join([i for i in cast.to_str(s) if (i >= '0') and (i <= '9')])

    try:
        if s[0] == '-':
            output = '-{s}'.format(s=output)
    except:
        pass

    return output

def email(s):
    """
    >>> email("hi@there.com")
    'hi@there.com'

    >>> email("some text, and address hi@there.com and more text")
    'hi@there.com'

    >>> email("     hi@there.com     ")
    'hi@there.com'

    >>> email("Hi There <hi@there.com>")
    'hi@there.com'

    >>> email("one hi@there.com and another foo@bar.com address")
    'hi@there.com'

    """
    # Pattern from https://developers.google.com/edu/python/regular-expressions
    mo = re.search(r'([\w.-]+)@([\w.-]+)', s.replace('<', ' ').replace('>', ' '))

    if mo:
        return '{front}@{back}'.format(front=mo.group(1), back=mo.group(2))
    else:
        return None

def price_like(s):
    """
    >>> price_like('')
    ''

    >>> price_like('$19.95')
    '19.95'

    >>> price_like('19.95')
    '19.95'

    >>> price_like('19.95345')
    '19.95'

    >>> price_like('19.5')
    '19.50'

    >>> price_like('19.')
    '19.00'

    >>> price_like('19')
    '19.00'

    >>> price_like('19.5.34')
    ''

    >>> price_like('.19')
    '0.19'

    """
    if s.strip() == '':
        return ''

    parts = s.split('.')

    if not len(parts):  # == 0
        # This shouldn't happen. split() should always return at least a one-item list
        return ''

    if len(parts) == 2:
        dollars = just_numbers(parts[0].strip())
        cents = just_numbers(parts[1].strip())

    elif len(parts) == 1:
        dollars = just_numbers(parts[0].strip())
        cents = '00'

    else:
        return ''

    if dollars == '':
        dollars = '0'

    if len(cents) == 2:
        pass

    elif len(cents) > 2:
        # Change '12345' to '12'
        cents = cents[:2]

    elif len(cents) == 1:
        # Chagne '5' to '50'
        cents = '%s0' % cents

    else:
        # Change '' to '00'
        cents = '00'

    return "%s.%s" % (dollars, cents)

def price_like_float(s):
    """
    >>> price_like_float('')


    >>> price_like_float('$19.95')
    19.95

    >>> price_like_float('19.95')
    19.95

    >>> price_like_float('19.95345')
    19.95

    >>> price_like_float('19.5')
    19.5

    >>> price_like_float('19.')
    19.0

    >>> price_like_float('19')
    19.0

    >>> price_like_float('19.5.34')


    >>> price_like_float('.19')
    0.19

    """

    try:
        return float(price_like(s))

    except ValueError:
        return

def zipcode(s):
    """
    >>> zipcode(s=90210)
    '90210'
    
    >>> zipcode(s='90210')
    '90210'

    >>> zipcode(s='90210  ')
    '90210'

    >>> zipcode(s='   90210')
    '90210'

    >>> zipcode(s='   90210   ')
    '90210'

    >>> zipcode(s='0210')
    '00210'

    >>> zipcode(s=210)
    '00210'

    >>> zipcode(s='902101234')
    '90210-1234'

    >>> zipcode(s='9021012')
    '00902-1012'

    >>> zipcode(s='90210-1234')
    '90210-1234'

    >>> zipcode(s='90210-12341234')
    '90210-1234'

    >>> zipcode(s='9021012341234')
    '90210-1234'

    """
    z = just_numbers(s)[:9]

    length = len(z)
    
    # Add leading zeros if the ZIP is less than 5 chars
    if length < 5:
        z = fmt.add_leading_padding(s=z, char='0', target_length=5)
    
    elif length == 5:
        pass

    elif length < 9:
        z = fmt.add_leading_padding(s=z, char='0', target_length=9)

    # Now put the '-' back in
    if len(z) == 9:
        z = '{front}-{back}'.format(front=z[0:5], back=z[5:])
        
    return z

## ---------------------
if __name__ == "__main__":
    import doctest
    print "Testing..."
    doctest.testmod()
    print "Done."