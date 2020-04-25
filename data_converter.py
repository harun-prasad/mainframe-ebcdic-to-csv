__author__ = "Harun Prasad P"
__copyright__ = "Copyright 2020, Harun Prasad P"
__license__ = "Proprietory"
__version__ = "1.0.1"
__status__ = "Production"

class DataConverter(object):
    """https://www.tutorialspoint.com/cobol/cobol_data_types.htm
    """

    def __init__(self):
        pass
    
    def setEncoding(self, encoding):
        self.encoding = encoding

    def decode(self, fieldBytes, encoding):
        if self.encoding:
            return fieldBytes.decode(encoding)
        else:
            return str(fieldBytes,"utf-8")

    def convert(self, fieldBytes, fieldType, size, scale=None, encoding="cp037"):
        if fieldType == "uinteger": # unsigned integer
            fieldString = self.decode(fieldBytes, encoding)
            return fieldString.strip()
        elif fieldType == "integer": # signed integer # TODO confirm
            fieldString = self.decode(fieldBytes, encoding)
            return fieldString.strip()
        elif fieldType == "string":
            fieldString = self.decode(fieldBytes, encoding).strip()
            return fieldString
        elif fieldType == "decimal":
            fieldString = self.decode(fieldBytes, encoding)
            fieldString = fieldString[:(size-scale)]+"."+fieldString[-scale:]
            return fieldString.strip()
        elif fieldType == "packedDecimal":
            fieldString = fieldBytes.hex() # e.g. '0034560c'
            # http://www.3480-3590-data-conversion.com/article-packed-fields.html
            f1 = fieldString[(len(fieldString)-1-size):(size - scale)].lstrip("0") + \
                    ("." + fieldString[size-scale:-1] if scale>0 else "") # e.g. '34.560'
            if not f1:
                f1 = "0"
            fieldString = ("-" if (fieldString[-1] == 'd') else "") + f1 #0xd is <0, 0xf is unsigned, and 0xc >=0
            fieldString = str(eval(fieldString)) # e.g. '34.56'
            return fieldString



