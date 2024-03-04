from __future__ import annotations

import re
from typing import Optional
from openpyxl.cell import Cell
import sqlite3
from sqlite3 import Error


class Case:
    def __init__(
            self,
            name: str,
            court: str,
            year: Optional[int] = None,
            related_cases: Optional[list[str]] = None,
            nom_cite: Optional[str] = None,
            er_cite: Optional[str] = None,
            comment: Optional[str] = None,
            link: Optional[str] = None,
            area_tags: Optional[list[str]] = None,
            subject_tags: Optional[list[str]] = None,
            cite_in_tags: Optional[dict] = None,
            authors: Optional[list[str]] = None,
            special_terms: Optional[list[str]] = None
    ):
        self.name = name
        self.year = year
        self.link = link
        self.court = court
        self.er_cite = er_cite
        self.nom_cite = nom_cite
        self.comment = comment
        self.area_tags = area_tags
        self.subject_tags = subject_tags
        self.cite_in_tags = cite_in_tags
        self.authors = authors
        self.special_terms = special_terms
        self.related_cases = related_cases

    def display(self):
        print(self.display_name)

    @property
    def display_name(self) -> str:
        return f'{self.name} ({self.year}) {self.nom_cite}, {self.er_cite}'

    @property
    def display_area_tags(self) -> str:
        return ', '.join(self.area_tags)

    @property
    def display_subject_tags(self) -> str:
        return ', '.join(self.subject_tags)

    @property
    def display_author(self) -> str:
        return ', '.join(self.authors)

    @property
    def display_special_terms(self) -> str:
        return ', '.join(self.special_terms)

    @property
    def display_cite_ins(self) -> str:
        return '; '.join([f'{person} ({comment})' for person, comment in self.cite_in_tags.items()])

    @staticmethod
    def from_excel(row: tuple) -> Case:
        def get_str_value(cell: Cell) -> str | None:
            return cell.value.strip() if cell.value else None

        def get_year(cell: Cell) -> int | None:
            if isinstance((date := cell.value), int):
                return date
            else:
                raise Exception(f'Error! Date at row {cell.row} is of type {type(date)}!')

        def get_underscore_list(cell: Cell) -> list[str] | None:
            if input_str := cell.value:
                return [item.replace('_', ' ') for item in input_str.split()]

        def get_cite_ins(cell) -> dict | None:
            def get_items(input_str: str) -> tuple[str, str]:
                pattern = re.compile(r'^([^[]+)\[([^]]+)\]$')
                match = pattern.match(input_str)
                if match:
                    return match.group(1), match.group(2)
                else:
                    print('No match found.')

            if cell.value:
                input_strings = cell.value.strip().split('; ')
                out_dict = dict()
                for input_str in input_strings:
                    person, comment = get_items(input_str)
                    out_dict.update({person: comment})
                return out_dict

        def get_comma_list(cell: Cell) -> list[str] | None:
            if input_str := cell.value:
                return input_str.strip().split(', ')

        return Case(
            name=get_str_value(row[0]),
            year=get_year(row[1]),
            nom_cite=get_str_value(row[2]),
            er_cite=get_str_value(row[3]),
            court=get_str_value(row[4]),
            subject_tags=get_underscore_list(row[5]),
            authors=get_underscore_list(row[6]),
            related_cases=get_comma_list(row[7]),
            cite_in_tags=get_cite_ins(row[8]),
            comment=get_str_value(row[9]),
            area_tags=get_underscore_list(row[10]),
            link=get_str_value(row[11]),
            special_terms=get_comma_list(row[12])
        )


class Casebook:

    def __init__(
            self,
            sql_path: str,
            cases: list[Case] = [],
    ):
        self.cases = cases
        self.sql_path = sql_path
        try:
            self.sql_connection: Optional[sqlite3.Connection] = sqlite3.connect(self.sql_path)
            print(f"Connection to {self.sql_path} successful")
        except Error as e:
            print(f"The error {e} occurred")
            self.sql_connection = None

    @property
    def display_casebook_info(self) -> str:
        """Gives a basic display of the key information about the Casebook object.
        :return: str, number of cases [number], SQL database [path].
        """
        pass

    @staticmethod
    def new_casebook_from_xl(sql_path: str, xl_path: str) -> Casebook:
        """ Create a new Casebook with a .db file of the path, sql_path.
        Enter new data into that casebook (and likewise the .db file) from the xl_path. 
        :param sql_path: a str object, a path to a blank or non-existent .db file. 
        :param xl_path: a str object, a path to a .xlsx file containing the relevant data. 
        :return: a Casebook object, with cases generated from .xlsx file (using Case.from_excel() for each row), and a
        sql connection object generated from sql_path. 
        """
        pass

    @staticmethod
    def new_casebook_from_sql(sql_path: str) -> Casebook:
        """ Create a new Casebook with a .db file of the path, sql_path.
        The data is read from the sql file itself, which already contains the relevant data.
        :param sql_path: a str object, a path to a .db file containing relevant data.
        :return: a Casebook object, with cases generated from the .db file and an sql connection object (sql_path).
        """
        pass

    def update_casebook_from_xl(self, xl_path):
        """
        Updates the Casebook object with data given from a .xlsx file, at xl_path.
        :param xl_path: a str object, a path to a .xlsx file containing the relevant data.
        :return: self, the Casebook object is itself updated.
        """
        pass


