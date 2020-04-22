# EBCDIC to CSV

Project to convert mainframe EBCDIC, dBase and also ASCII files to CSV file.

Two main files are
1. ebcdic2csv.py - Script to convert mainframe EBCDIC file and also ASCII file to CSV file.
2. dbf2csv.py - Script to convert mainframe dBase file to CSV file.

Refer the above two files for runing instructions.

Note:
This project was initially written to convert the research datasets, to csv, available at
https://www.rrc.state.tx.us/about-us/resource-center/research/data-sets-available-for-download/
This mainly contains mainframe EBCDIC files, ASCII files, dbase files. Since this can be used for
any similar datasets, I have released this code for free use. 

## Requirements
1. Install and run scripts on python 3.8 or above.
2. Install the python libraries as below
        pip install -r . \requirements.txt

## EBCDIC to CSV, ASCII to CSV
Use this script to convert mainframe EBCDIC file and also ASCII  file to CSV file.
Usage: 

`python ebcdic2csv.py <configuration file location for layout format> <data file> [<encoding>]`

<encoding>: "cp037" for EBCDIC 
            no encoding for ASCII

This outputs CSV files named the "<data file><record name in configuration file>.csv"
The configuration is specified in JSON format. Refer to configuration_file.txt for specification of the configuration file.

e.g.
```
python ebcdic2csv.py "data\gas_ebcdic_layout.json" "data\gsf001l.ebc" "cp037"

python ebcdic2csv.py "data\oil_gas_well_api_layout.json" "data\maf016.cc001"
```


Note:
data\gsf001l.ebc was downloaded from ftp://ftpe.rrc.texas.gov/shgled/gsf001l.ebc.gz
data\maf016.cc001 was downloaded from ftp://ftpe.rrc.texas.gov/shpapima/2020-04-18/maf016.cc001

## Configuration File

For converting the EBCDIC and ASCII files the script need to told about 
the field details such as field name, field size, field type, and field scale for decimal type.
This information also known as COBOL copy book information is passed to the script as JSON configuration file.

Below are the possible field types in mainframe format and its corresponding COBOL Representation
| Layout Type | COBOL Representation |
| integer | PIC S9 to S9(19) COMP	(singed integer size 1 to 19) |
| uinteger | PIC 9 to 9(20) COMP (unsigned integer size 1 to 20) |
| string | PIC X(n) (string with size n) |
| packedDecimal - PIC S9(p)V9(s) COMP-3 |
| decimal | PIC S9(p)V9(s) |

For packedDecimal and decimal
| p | number of digits to the left of decimal point |
| s | number of digits to the right of decimal point |

Refer to https://www.tutorialspoint.com/cobol/cobol_data_types.htm for more details on the COBOL datatypes.

Configuration files are represented in JSON format to specify the layout structure of the EBCDIC. 
Refer to the example configuration files 
"data\gas_ebcdic_layout.json" and "data\oil_gas_well_api_layout.json" in the data folder.

Below is the description for each attributes in the configuration file.

| Attribute Name | Description |
| description | Specifies the summary of this configuration file. description is optional |
| layouts | Specifies each of the record types in the data file |
| layoutrecord | Record name. This is used in csv name so should be using alphabets and numbers only |
| layout | Record structure details. Each of the fields are specified |
| name | field name |
| type | field type |
| size | field size |
| scale | field scale for decimal and packedDecimal types |
| repeatgroup | Specifies the fields that are repeated number of times |
| repeat | number of times the repeatgroup fields are repeated |
| keyfieldvalue | Specifies that the current field is used to identify the record type or layout type in the data file. This is mandatory only if the data file contains more than one record or layout. If the given value matches field value, then that record/layout type is used for that record |
| parentlayout | specifies this record type is a subrecord of another record. The value of this attribute should match an existing "layoutrecord" name |

Apart from the fields specified in the layout, the below two fields are added to the csv file.
1. id - Unique incremental record for each record in the data file.
2. parentid - Specifies the record id of parent record, specified in the "payrentlayout"

json_helper.xlsx can be used to quickly convert the structure details into JSON snippets 

Below is the sample conversion of the configuation in https://www.rrc.state.tx.us/media/1255/gsa020k.pdf

```
{
    "description": "Gas Ledger",
    "layouts": [
        {
            "layoutrecord": "fieldrecord",
            "layout": [
				{ "name": "REC-CODE", "type": "uinteger", "size": 1, "keyfieldvalue": "1" },
				{ "name": "FLD-CODE-DIST-NO", "type": "uinteger", "size": 2 },
				{ "name": "FLD-CODE-DIST-SFX", "type": "string", "size": 1 },
                ....
				{ "name": "FILLER3", "type": "string", "size": 16 },
				{
					"repeat": 14,
					"repeatgroup": [
					{ "name": "FLD-DATE", "type": "uinteger", "size": 6 },
                    ....
					{ "name": "FILLER4", "type": "string", "size": 43 }
					]
				},
				{ "name": "FILLER5", "type": "string", "size": 390 }
			]
        },
        {
			"layoutrecord": "wellrecord",
			"parentlayout": "fieldrecord",
            "layout": [
				{ "name": "W-REC-CODE", "type": "uinteger", "size": 1, "keyfieldvalue": "5" },
				{ "name": "W-DIST-NO", "type": "uinteger", "size": 2 },
                ....
				{ "name": "FILLER3", "type": "string", "size": 180 }
			]
        }
    ]
}
```


## DBF to CSV

Use this script to convert mainframe dBase file to CSV file.
Usage: 

`python dbf2csv.py <dbf file.dbf>`

This outputs CSV files named the "<dbf file>.csv"

e.g.
`python dbf2csv.py "data\pipe001l.dbf"`

Note: 
data\pipe001l.dbf was downloaded from  ftp://ftpe.rrc.texas.gov/shpipeln/Pipelines/pipeline001.zip