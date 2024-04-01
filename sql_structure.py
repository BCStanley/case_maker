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

    def insert_query(self, entries: dict) -> str | None:
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
            return None

    def update_query(self, entries: dict, condition: tuple) -> str | None:
        """
        A method of Table(), which produces the SQL script for updating the data given.
        :param entries: a dict object, in the form {column: row} for what the entries are to be changed to.
        The method will check to ensure that the columns being changed are those of the table itself, and raise an
        error if not.
        :param condition: a tuple, e.g. ("id", 6) for identifying what entries to change. This means that only one
        condition can be given, though this is fine for my purposes.
        :return: a str, which is the sql text to be executed.
        """

        def entries_text(values: dict) -> list:
            """
            This function within the method is used for parsing the various alterations that are proposed.
            It ensures that the relevant columns are those actually within the table, and makes the required syntax
            changes for strings by adding quote marks.
            :param values: this is the entries dict.
            :return: a list object, of each of the alterations needed, e.g. "year = 1650"
            """
            s: list = []
            for key, item in values.items():
                assert key in self.fields.keys(), f"the field {key} is not in {self.title}"  # Test if column in table.
                if type(item) == str:  # Add quotation marks if the entry is a string.
                    item = f"\"{item}\""
                else:
                    pass
                s.append(f"{key} = {item}")  # Produce the relevant line.
            return s

        string = f"""
        UPDATE {self.title} 
        SET {", ".join(entries_text(entries))}
        WHERE {condition[0]} = {condition[1]};
        """
        return string


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


class SelectionQuery:

    def __init__(
            self,
            search_table: Table,
            selections: list[str],
            conditions: dict,
            ):
        self.search_table = search_table
        self.selections = selections
        self.conditions = conditions

        for field in self.selections:
            assert field in self.search_table.fields.keys() or "*", f"The value {field} is not in {self.search_table.title}."
        for condition in self.conditions:
            assert condition in self.search_table.fields, f"The value {condition} is not in {self.search_table.title}."

    @property
    def sql_text(self) -> str:

        def condition_line(key: str, entry: list) -> str | None:
            """
            A function called within the sql_text property, for producing one line of SQL tex conditions based on the
            type of search value (=, in, or between) and the values being compared.
            :param key: a str, either "=", "in" or "between."
            :param entry: a list of str objects, what is being looked for.
            :return: a str, which is a line of SQL for producing the sql query.
            """
            if "TEXT" in self.search_table.fields[key]:
                value = f"\"{str(entry[1])}\""
            else:
                value = entry[1]
            if entry[0] == "=":
                return f"{key} {entry[0]} {value}"
            elif entry[0] == "in":
                return f"{key} {entry[0]}({value})"
            elif entry[0] == "between":
                entries = value.split(", ")
                return f"{key} {entry[0]} {entries[0]} AND {entries[1]}"
            else:
                return None

        if self.conditions:
            string = f"""SELECT {", ".join([item for item in self.selections])} from {self.search_table.title} where 
            {" AND ".join(condition_line(field, self.conditions[field]) for field in self.conditions)}
            """
        else:
            string = f"""SELECT {", ".join([item for item in self.selections])} from {self.search_table.title}
            """
        return string

    @property
    def full_sql_text(self) -> str:
        return f"{self.sql_text};"

