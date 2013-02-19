# IIFWriter.py module


import csv
import ConfigParser
import os, sys
from decimal import Decimal
from time import localtime, strftime


class Error(Exception): pass
class FileFormatError(Error): pass


class IIFWriter:

    def __init__(self, transactions, filename=None):
        self.cfg = ConfigParser.SafeConfigParser()
        self.cfg.read('qbutils.cfg')
        self.transactions = transactions[:]
        params = self.transactions.pop(0)
        self.import_account='TEMPIMPORT'
        if params.has_key("Type"):
            self.type = params["Type"]
            self.import_account='TEMPIMPORT'
            self.trns_account = self._account(self.type)
            print 'Transaction Account: '+self.trns_account
            self.import_account = self._account('DEFAULT')
            if self.type.upper() == 'BANK':
                self.debit_trans_type = 'CHECK'
                self.credit_trans_type = 'DEPOSIT'
            elif self.type.upper() == 'CCARD':
                self.debit_trans_type = 'CREDIT CARD'
                self.credit_trans_type = 'CCARD REFUND'
            else:
                self.debit_trans_type = 'UNKNOWN'
        else:
            raise FileFormatError, 'Unknown input type'
        if filename == sys.stdout: 
            self.filename = sys.stdout
        elif filename:
            self.filename = filename + ".iif"
        elif params["Filename"]:
            self.filename = params["Filename"] + ".iif"
        else:
            self.filename = strftime("%Y%m%d_%H%M%S.iif", localtime())

    def _openfile(self):
        """Open the csv output file."""
        if self.filename == sys.stdout:
            self.writer = csv.writer(self.filename, 'excel-tab')
        else:
            self.writer = csv.writer(open(self.filename, 'w'), 'excel-tab')

    def _write_header(self):
        """Write IIF transaction header lines to output file"""
        header = (("!TRNS", "DATE", "TRNSTYPE", "ACCNT", "NAME", "AMOUNT", "MEMO"),
                  ("!SPL", "DATE", "TRNSTYPE", "ACCNT", "NAME", "AMOUNT", "MEMO"),
                  ("!ENDTRNS",))
        self.writer.writerow(header[0])
        self.writer.writerow(header[1])
        self.writer.writerow(header[2])
 
    def _account(self, str):
        """Lookup account mapping based on payee name input string.
           if there are no matches, then return default account is returned."""
        try:
            tmpstr = self.cfg.get('ACCOUNTS', str)
        except:
            tmpstr = self.import_account
        return tmpstr

    def _format_trns(self, trns_dict):
        """Format the trns transaction line."""
        tmplist = ['TRNS']
        tmplist.append(trns_dict['D'])
        if float(trns_dict['T']) > 0:
            tmplist.append(self.credit_trans_type)
        else:
            tmplist.append(self.debit_trans_type)
        tmplist.append(self.trns_account)
        tmplist.append(trns_dict['P'])
        tmplist.append(trns_dict['T'])
        try: tmplist.append(trns_dict['M'])  #memo is optional
        except: tmplist.append(' ')
        return tmplist[:]

    def _format_spl(self, trns_list):
        """Format the spl transaction line."""
        tmplist = trns_list[:]
        tmplist[0] = 'SPL'
        tmplist[3] = self._account(tmplist[4])
        tmplist[5] = str(Decimal(tmplist[5]) * -1)
        return tmplist[:]

    def write(self):
        """Main process control"""
        endtrns = ("ENDTRNS",)
        self._openfile() 
        self._write_header()
        for trans in self.transactions:
            trns_line = self._format_trns(trans)
            spl_line = self._format_spl(trns_line)
            self.writer.writerow(trns_line)
            self.writer.writerow(spl_line)
            self.writer.writerow(endtrns)


if __name__ == "__main__":
    pass
