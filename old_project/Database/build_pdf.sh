#!/usr/bin/bash

DATANAME=$"case_database.db"
TEXNAME=$"list_of_cases.tex"
PDFNAME=$"list_of_cases.pdf"

python3 make_latex.py $DATANAME $TEXNAME

mkdir "output"

cp $TEXNAME "output"

(cd "output"; xelatex $TEXNAME)
(cd "output"; xelatex $TEXNAME)

(cd "output"; mv $PDFNAME ..)

rm -rf "output"
