class Table:

    def __init__(
            self,
            title: str,
            fields: dict,
    ):
        self.title: str = title
        self.fields: dict = fields

    @property
    def creation_query(self) -> str:
        """
        This property is the SQL script that would be executed for the creation of any table, given its contents.
        :return: str, of SQL (including line breaks) which *should* work to produce any table in question.
        """
        nl: str = ",\n"
        string: str = f"""CREATE TABLE IF NOT EXISTS {self.title} (
        {nl.join([" ".join([field, self.fields[field]]) for field in self.fields])}
        );
        """
        return string

    def insert_query(self, entries: dict) -> str:
        """
        A method of the Table(), which produces the SQL script for adding the information given.
        :param entries: the information in question, which must be entered as a dict {"name": name...} ect.
        All the required keys must be given. However, non-needed information is ignored, and will not raise and error.
        :return: An SQL script with line breaks, e.g. "INSERT INTO [table]..."
        """
        forbid: str = "INTEGER PRIMARY KEY AUTOINCREMENT"
        try:
            string: str = f"""
            INSERT INTO {self.title} ({", ".join([field for field in self.fields if self.fields[field] != forbid])}) VALUES
            ({", ".join([entries[field] for field in self.fields if self.fields[field] != forbid])});
            """
            return string
        except KeyError as e:
            print(f"Failed to create query for {self.title}. Entry {e} missing.")


class DatabaseStructure:

    def __init__(
            self,
            cases_table=Table(title="cases", fields={
                "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
                "name": "TEXT NOT NULL UNIQUE",
                "year": "INTEGER",
                "nom_cite": "TEXT",
                "er_cite": "TEXT",
                "court": "TEXT",
                "link": "TEXT",
                "comment": "TEXT"}
                              ),
            subject_table=Table(
                title="subjects", fields={
                    "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
                    "name": "TEXT"}
            ),
            authors_table=Table(
                title="authors", fields={
                    "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
                    "name": "TEXT"}
            ),
            cite_in_table=Table(
                title="cited_in", fields={
                    "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
                    "name": "TEXT NOT NULL UNIQUE"}
            ),
            area_table=Table(
                title="areas", fields={
                    "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
                    "name": "TEXT NOT NULL UNIQUE"}
            ),
            special_terms_table=Table(
                title="special_terms", fields={
                    "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
                    "name": "TEXT NOT NULL UNIQUE"}
            )
    ):
        self.cases_table = cases_table
        self.subject_table = subject_table
        self.subject_crossref_table = Table(
            title="subjects_crossref", fields={
                "subject_id": f"INTEGER REFERENCES {self.subject_table.title}({next(iter(self.subject_table.fields))})",
                "case_id": f"INTEGER REFERENCES {self.cases_table.title}({next(iter(self.cases_table.fields))})"}
        )
        self.authors_table = authors_table
        self.authors_crossref_table = Table(
            title="authors_crossref", fields={
                "author_id": f"INTEGER REFERENCES {self.authors_table.title}({next(iter(self.authors_table.fields))})",
                "case_id": f"INTEGER REFERENCES {self.cases_table.title}({next(iter(self.cases_table.fields))})"}
        )
        self.cite_in_table = cite_in_table
        self.cite_in_crossref_table = Table(
            title="cite_in_crossref", fields={
                "person_id": f"INTEGER REFERENCES {self.cite_in_table.title}({next(iter(self.cite_in_table.fields))})",
                "case_id": f"INTEGER REFERENCES {self.cases_table.title}({next(iter(self.cases_table.fields))})",
                "comment": "TEXT"}
        )
        self.area_table = area_table
        self.area_crossref_table = Table(
            title="area_crossref", fields={
                "area_id": f"INTEGER REFERENCES {self.area_table.title}({next(iter(self.area_table.fields))})",
                "case_id": f"INTEGER REFERENCES {self.cases_table.title}({next(iter(self.cases_table.fields))})"}
        )
        self.special_terms_table = special_terms_table
        self.special_terms_crossref_table = Table(
            title="special_terms_crossref", fields={
                "term_id": f"INTEGER REFERENCES {self.special_terms_table.title}({next(iter(self.special_terms_table.fields))})",
                "case_id": f"INTEGER REFERENCES {self.cases_table.title}({next(iter(self.cases_table.fields))})"}
        )

    def __iter__(self):
        return iter([self.cases_table,
                     self.subject_table,
                     self.authors_table,
                     self.cite_in_table,
                     self.area_table,
                     self.special_terms_table,
                     self.subject_crossref_table,
                     self.authors_crossref_table,
                     self.cite_in_crossref_table,
                     self.area_crossref_table,
                     self.special_terms_crossref_table])

