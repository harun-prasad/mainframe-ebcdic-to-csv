"""Use this script to convert mainframe dBase file to CSV file.
Usage: 

python dbf2csv.py <dbf file.dbf>

This outputs CSV files named the "<dbf file>.csv"

e.g.
python dbf2csv.py "data\pipe001l.dbf"

Note: 
data\pipe001l.dbf was downloaded from  ftp://ftpe.rrc.texas.gov/shpipeln/Pipelines/pipeline001.zip
"""

import csv
from dbfread import DBF
import os
import sys

if len(sys.argv) > 1:
    DBFFileName = sys.argv[1]
else:
    DBFFileName = "" #"D:\workspace-python\ebcdic\src\surv001Labpt.dbf"
if not DBFFileName.endswith('.dbf'):
    print ("Filename does not end with .dbf")
    exit(1)
print("Converting %s to csv" % DBFFileName)
csvFileName = DBFFileName[:-4]+ ".csv"
csvFile = open(csvFileName,'w', newline='\n')
table = DBF(DBFFileName)
writer = csv.writer(csvFile, quotechar='"')

writer.writerow(table.field_names)
counter = 0
for record in table:
    counter += 1
    if counter % 1000 == 0:
        print(counter)
    writer.writerow(list(record.values()))

print ("Done... with", counter, "records.")