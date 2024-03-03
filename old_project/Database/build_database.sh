#!/usr/bin/bash

DATANAME=$"case_database.db"
TEXNAME=$"list_of_cases.tex"
PDFNAME=$"list_of_cases.pdf"
BACKUP=$"backup_data"
SPREADSHEET=$"Input.xlsx"
DATE=$(date '+%d_%m_%Y_%H:%M:%S')
BACKUPNAME=$BACKUP"/case_database_$DATE.db"

cp -u $DATANAME $BACKUPNAME

echo $BACKUPNAME

python3 ReadCase.py $SPREADSHEET $DATANAME 0

python3 make_latex.py $DATANAME $TEXNAME

mkdir "output"

cp $TEXNAME "output"

(cd "output"; xelatex $TEXNAME)
(cd "output"; xelatex $TEXNAME)

(cd "output"; mv $PDFNAME ..)

rm -rf "output"

find $BACKUP -mtime +10 -type f -delete
