
import sys
import QIFParser
import IIFWriter

def main(infilename, outfilename=None):
    qif = QIFParser.QIFParser(infilename)
    qif.parse()
    if outfilename:
        iif = IIFWriter.IIFWriter(qif.transactions, outfilename)
    else:
        iif = IIFWriter.IIFWriter(qif.transactions)
    iif.write()
    

if __name__ == "__main__":
    if len(sys.argv) > 3 or len(sys.argv) < 2:
        print 'Usage: %s <<importfile>>.qif <<outputfile>>' % sys.argv[0]
        print '    outputfile is optional and should not contain a file extention.'
    elif len(sys.argv) == 2:
        main(sys.argv[1])
    elif len(sys.argv) == 3:
        if sys.argv[2] == 'sys.stdout':
            main(testfilename, sys.stdout)
        else:
            main(testfilename, sys.argv[2])