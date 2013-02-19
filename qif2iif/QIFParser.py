# QIFParser.py module
################################################################################
# QIF file format information:
#  Header, Type of data
#  !Type:Bank         Bank account transactions
#  !Type:Cash         Cash account transactions
#  !Type:CCard        Credit card account transactions
#  !Type:Invst        Investment account transactions
#  !Type:Oth A        Asset account transactions
#  !Type:Oth L        Liability account transactions
#  !Account           Account list or which account follows
#  !Type:Cat          Category list
#  !Type:Class        Class list
#  !Type:Memorized    Memorized transaction list
#  
#  Field    Indicator Explanation
#  D        Date
#  T        Amount
#  C        Cleared status
#  N        Num (check or reference number)
#  P        Payee
#  M        Memo
#  A        Address (up to five lines; the sixth line is an optional message)
#  L        Category (Category/Subcategory/Transfer/Class)
#  S        Category in split (Category/Transfer/Class)
#  E        Memo in split
#  $        Dollar amount of split
#  ^        End of the entry
################################################################################
"""
QIFParser module

This module parses a QIF file and returns a list of dictionary
objects, one per transaction. The list can then be easily processed
by another applcation.

Currently the module only parses bank account and credit card transactions
(!Type:Bank, !Type:CCard).

"""

import os.path
import ConfigParser
from types import *

#Exceptions
class Error(Exception): pass
class FileFormatError(Error): pass
class InvalidInputError(Error): pass


class QIFParser:
    """Parses QIF files into a list of transactions. Each transaction
       is in dictionary format. The transactions are stored in the
       Parse. Transactions list for future processing. The __init__
       method controls the parsing process. Simply calling class
       to parse input. Input can be in either file format or a list
       of string values."""

    valid_qif_types = ['!Type:Bank', '!Type:CCard']

    def __init__(self, stream):
        self.cfg = ConfigParser.SafeConfigParser()
        self.cfg.read('qbutils.cfg')
        self.lines = []
        self.transactions = []
        params = {}
        self.dateformat = self._dateformat()
        print 'DATEFORMAT: '+self.dateformat
        if type(stream) is StringType:
            params["Filename"] = os.path.splitext(stream)[0]
            for line in file(stream):
                if len(line.strip()):
                    self.lines.append(line.strip()) 
        elif type(stream) is ListType:
            params["Filename"] = None
            for line in stream:
                if len(line.strip()):
                    self.lines.append(line.strip()) 
        else:
            raise InvalidInputError, str(type(stream)) + " Input type invalid" 
        if self.valid_qif_types.count(self.lines[0]):
            params["Type"] = self.lines[0].split(':')[1]
        else:
            raise FileFormatError, 'Unknown QIF file type'
        self.transactions.append(params)

    def parse(self):
        """Transform transaction lines into a dictionary of fields and
           corresponding values"""
        di = {}
        for line in self.lines:
            if line[0] in 'D':  #Date - make sure it is MMDDYY
              if self.dateformat == 'MMDDYY':
                di[line[0]] = line[1:]
              else:
                d = line[1:].split('/')
                dswap = d[1]+'/'+d[0]+'/'+d[2]
                di[line[0]] = dswap
            elif line[0] == 'N': # Transaction number (not very useful)
              di[line[0]] = line[1:]
            elif line[0] in 'T':
                di[line[0]] = line[1:].replace(',', '').strip()
            elif line[0] == 'M':
                di[line[0]] = line[1:]   #Memo field, if there is one
            elif line[0] == 'P':
              #Need to map the payee line to a config file map
              if line[1] == '#':
                      stripped = line[2:].replace(':',' ')
                      stripped = stripped.replace('*',' ')
                      di[line[0]] = self._payee(stripped)
              else:
                      stripped = line[1:].replace(':',' ')
                      stripped = stripped.replace('*',' ')
                      di[line[0]] = self._payee(stripped)
            elif line[0] == 'A':
                pass
            elif line[0] == 'C':
                pass
            elif line[0] == '^':
                self.transactions.append(di) 
                di = {}
        return

    def _payee(self, str):
        """Lookup input string in config file and return matching value.
           if there are no matches, then return the input string
           truncated to 25 characters max length."""
        try:
            tmpstr = self.cfg.get('PAYEE', str[:10].strip())
            return tmpstr
        except:
            return str[:25]

    def _dateformat(self):
        """Lookup input string in config file and return matching value.
           if there are no matches, then return the default input string"""
        try:
            tmpstr = self.cfg.get('DATEFORMAT', 'INPUTFORMAT')
            return tmpstr
        except:
            tmpstr = 'DDMMYY'
            return tmpstr


if __name__ == "__main__":
    qif = Parse('.\\july2003.qif')
    print '\n'
    for di in qif.transactions:
        print di
