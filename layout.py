__author__ = "Harun Prasad P"
__copyright__ = "Copyright 2020, Harun Prasad P"
__license__ = "Proprietory"
__version__ = "1.0.1"
__status__ = "Production"

import json
from collections import OrderedDict
import math
import os
import csv

DELIMITER = ","

class Layout(object):

    def __init__(self):
        pass

    def processLayout(self, layoutFilePath=None):
        self.multiRecord = False
        self.multiRecordMaxKeyFieldPostion = 0
        self.layoutRecords = {}
        lf = open(layoutFilePath) # layout file object
        self.layoutFile = json.load(lf, object_pairs_hook=OrderedDict)
        lf.close()
        self.validate()
        self.printLayoutSummary()

    def printLayoutSummary(self):
        for record in self.layoutRecords:
            print(record, self.layoutRecords[record]["recordLength"])
    
    def validate(self):
        if "layouts" not in self.layoutFile:
            raise ValueError("No layouts attribute present")
        
        if len(self.layoutFile['layouts'])>1:
            self.multiRecord = True

        for layout in self.layoutFile['layouts']:
            if "layoutrecord" not in layout:
                raise ValueError("No layoutrecord attribute present in layout")
            if "layout" not in layout:
                raise ValueError("No layout attribute present in layout")

            (recordLength, keyField, csvHeader) = self.validateLayoutRecordGroup(layout["layout"])
            if self.multiRecord and not keyField:
                raise ValueError("keyfieldvalue not defined for layout")
            
            if keyField and self.multiRecordMaxKeyFieldPostion < keyField["position"]:
                self.multiRecordMaxKeyFieldPostion = keyField["position"]

            csvHeader = ["id","parent_id"] + csvHeader
            self.layoutRecords[layout["layoutrecord"]] = {"recordLength": recordLength, "keyField": keyField, "layout": layout["layout"], "csvHeader": csvHeader, "lastRecordId": 0}
            if "parentlayout" in layout:
                if layout["parentlayout"] not in self.layoutRecords:
                    raise ValueError("parentlayout not present or should be declared before child layout for " + layout["parentlayout"])
                self.layoutRecords[layout["layoutrecord"]]["parentlayout"] = layout["parentlayout"]

    def validateLayoutRecordGroup(self, layout):
        recordLength = 0
        keyField = None
        csvHeader = []
        for field in layout:
            if "repeat" in field:
                if "repeatgroup" not in field:
                    raise ValueError("repeatgroup attribute not provided")
                (rl, kf, ch) = self.validateLayoutRecordGroup(field["repeatgroup"])
                recordLength += rl * field["repeat"]
                if kf:
                    raise ValueError("keyfieldvalue attribute should not be provided inside a repeat field. "+ kf)
                if field["repeat"] == 1:
                    csvHeader.extend(ch)
                elif field["repeat"] > 1:
                    for counter in range(field["repeat"]):
                        flds = (("_"+str(counter)+"|").join(ch) + "_"+str(counter)).split("|")
                        csvHeader.extend(flds)
            else:
                if "name" not in field:
                    raise ValueError("name attribute not provided. " + field)
                if "type" not in field:
                    raise ValueError("type attribute not provided. " + field)
                if "size" not in field:
                    raise ValueError("size attribute not provided. " + field)
                if (field["type"] == "decimal" or field["type"] == "packedDecimal") and "scale" not in field:
                    raise ValueError("scale attribute not provided")
                # recordLength Calculation
                if field["type"] == "uinteger" or field["type"] == "string" or field["type"] == "decimal":
                    recordLength += field["size"]
                    field["bytesize"] = field["size"]
                elif field["type"] == "packedDecimal":
                    recordLength += int(math.ceil((field["size"]+1)/2.0))
                    field["bytesize"] = int(math.ceil((field["size"]+1)/2.0))
                # Adding field position to field
                if "poistion" not in field:
                    field["position"] = recordLength
                # Setting keyField
                if "keyfieldvalue" in field:
                    keyField = field
                csvHeader.append(field["name"])
        return (recordLength, keyField, csvHeader)

class LayoutDataProcessor(object):
    def __init__(self, dataFilePath, layoutObject, dataConverterObject):
        self.inputFile =  open(dataFilePath, "rb") 
        self.inputFileBytes = b""
        self.inputFileBytesPosition = 0
        self.bytesReadCount = 0 #in 128 KB

        self.recordCounter = 0
        
        self.lo = layoutObject
        self.dc = dataConverterObject
        for record in self.lo.layoutRecords:
            csvf = open(dataFilePath + record + ".csv", "w", newline="\n")
            outputFile = csv.writer(csvf, quotechar='"', delimiter=DELIMITER)
            self.lo.layoutRecords[record]["outputFile"] = outputFile
            outputFile.writerow(self.lo.layoutRecords[record]["csvHeader"])
        
        self.processData()

    def processData(self):
        recordCounter = 0
        while True:
            recordCounter += 1
            if recordCounter % 1000 == 0:
                print (recordCounter)
            # if recordCounter == 4772: # For debug
            #     print ("in 4772")
            record = ""
            if self.lo.multiRecord:
                # identify record type
                dataBytes = self.getBytes(self.lo.multiRecordMaxKeyFieldPostion, processed=False)
                if not dataBytes:
                    print("File conversion completed with", recordCounter - 1, "records.")
                    break
                recordMatch = False
                for record in self.lo.layoutRecords:
                    kf = self.lo.layoutRecords[record]["keyField"]
                    if "scale" in kf:
                        scale = kf["scale"]
                    else:
                        scale = None
                    kfValue = self.dc.convert(dataBytes[(kf["position"]-kf["bytesize"]):(kf["position"] + 1)], kf["type"], kf["size"], scale)
                    if kf["keyfieldvalue"] == kfValue:
                        recordMatch = True
                        break
                if not recordMatch:
                    raise ValueError("Invalid data, keyfieldvalue didn't match")
            else:
                dataBytes = self.getBytes(10, processed=False)
                if not dataBytes:
                    print("File conversion completed with", recordCounter - 1, "records.")
                    break
                record = list(self.lo.layoutRecords.keys())[0]
            dataValue = self.processDataLayoutGroup(self.lo.layoutRecords[record]["layout"])
            parent_id = ""
            if ("parentlayout" in self.lo.layoutRecords[record]):
                parentLayout = self.lo.layoutRecords[record]["parentlayout"]
                parent_id = str(self.lo.layoutRecords[parentLayout]["lastRecordId"])

            dataValueStr = [str(recordCounter), str(parent_id)]  + dataValue
            outFile = self.lo.layoutRecords[record]["outputFile"]
            outFile.writerow(dataValueStr)
            self.lo.layoutRecords[record]["lastRecordId"] = recordCounter
                
    def processDataLayoutGroup(self, layout):
        dataValue = []
        for field in layout:

            if "repeat" in field:
                for repeatcounter in range(field["repeat"]):
                    dv = self.processDataLayoutGroup(field["repeatgroup"])
                    dataValue.extend(dv)
            else:
                #if field["name"] == "WL-TOP-PER" or field["name"] == "EXC-14B2-APP-NO":
                #    print("field " + field["name"])
                #    print("")
                scale = None
                if "scale" in field:
                    scale = field["scale"]
                dataBytes = self.getBytes(field["bytesize"])
                dv = self.dc.convert(dataBytes, field["type"], field["size"], scale)
                #print(field["name"], field["size"], field["type"],scale, "------", dv,"|", dataBytes.hex())
                dataValue.append(dv)
        return dataValue

    def getBytes(self, count, processed=True):
        if len(self.inputFileBytes) < self.inputFileBytesPosition + count:
            readBytes = self.inputFile.read(131072) # Reading 128 KB, Should be greater than the maximum field length
            # print("Read Bytes Length", len(readBytes))
            self.inputFileBytes = self.inputFileBytes[self.inputFileBytesPosition:] + readBytes
            self.inputFileBytesPosition = 0
            self.bytesReadCount += 1
            if self.bytesReadCount % 8 == 0:
                print(self.bytesReadCount/8, "MB processed")
        if (len(self.inputFileBytes) - self.inputFileBytesPosition) < count: # Not enough bytes to return requested size
            if processed:
                raise Exception("EOF reached")
            else:
                return ""
        readBytes = self.inputFileBytes[self.inputFileBytesPosition:(self.inputFileBytesPosition + count)]
        if processed:
            self.inputFileBytesPosition += count
        return readBytes
