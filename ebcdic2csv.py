"""Use this script to convert mainframe EBCDIC file and also ASCII  file to CSV file.
Usage: 

python ebcdic2csv.py <configuration file location for layout format> <data file> [<encoding>]

<encoding>: "cp037" for EBCDIC 
            no encoding for ASCII

This outputs CSV files named the "<data file><record name in configuration file>.csv"
The configuration is specified in JSON format. Refer to configuration_file.txt for specification of the configuration file.

e.g.
python ebcdic2csv.py "data\gas_ebcdic_layout.json" "data\gsf001l.ebc" "cp037"

python ebcdic2csv.py "data\oil_gas_well_api_layout.json" "data\maf016.cc001"

Note:
data\gsf001l.ebc was downloaded from ftp://ftpe.rrc.texas.gov/shgled/gsf001l.ebc.gz
data\maf016.cc001 was downloaded from ftp://ftpe.rrc.texas.gov/shpapima/2020-04-18/maf016.cc001
"""

__author__ = "Harun Prasad P"
__copyright__ = "Copyright 2020, Harun Prasad P"
__license__ = "Proprietory"
__version__ = "1.0.1"
__status__ = "Production"

import json
import sys
from collections import OrderedDict
from layout import Layout, LayoutDataProcessor
from data_converter import DataConverter
import pprint

if __name__ == "__main__":
    if len(sys.argv) >=3:
        layout_file = sys.argv[1]
        data_file = sys.argv[2]
        if len(sys.argv) == 4:
            encoding = sys.argv[3]
    else:
        layout_file = "data\gas_ebcdic_layout.json"
        data_file = "data\gsf001l.ebc"
        encoding = "cp037" # for EBCDIC
        # layout_file = "data\oil_gas_well_api_layout.json"
        # data_file = "data\maf016.cc001"
        # encoding = None # for ASCII
    
    dc = DataConverter()
    dc.setEncoding(encoding)

    lo = Layout()
    lo.processLayout(layout_file)
    #Printing string
    # pprint.pprint(lo.layoutRecords)

    ldp = LayoutDataProcessor(data_file, lo, dc)
