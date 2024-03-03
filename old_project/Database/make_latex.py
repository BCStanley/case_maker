import sqlite3
from sqlite3 import Error
import sys

# These functions are the core "writing" / "ammending" functions for the text file.

def open_up_document(openmatter, texpath):
    file = open(texpath, "w")
    file.write(openmatter)
    file.close()


def close_up_document(textpath):
    file = open(textpath, "a")
    file.write("\n\\end{document}")
    file.close()


def insert_into_document(textpath, string):
    file = open(textpath, "a")
    file.write(string)
    file.close()

OPEN = """
\\documentclass[twoside]{article}

\\usepackage{verbatim}
\\usepackage{longtable}
\\usepackage{hyperref}
\\hypersetup{
    colorlinks=false,
    linkcolor=blue,
    filecolor=magenta,
    urlcolor=cyan,
    bookmarks=true,
    hidelinks=true,
}

% 1. Sets the font
\\usepackage{fontspec}
\\setmainfont{Charter}
\\renewcommand{\\baselinestretch}{1.25}

%2. Sets the page size, etc.

\\usepackage{geometry}
\\geometry{
a4paper,
left = 20mm,
right = 20mm,
top = 20mm,
bottom = 20mm,
}

\\usepackage{titlesec}
\\titleformat{\\section}
  {\\normalfont\\normalsize\\bfseries\\scshape}{\\thesection}{1em}{}
\\titleformat{\\subsection}
  {\\normalfont\\normalsize\itshape}{\\thesubsection}{1em}{}
\\titleformat{\\subsubsection}
  {\\normalfont\\normalsize}{\\thesubsubsection}{1em}{}

\\def \\Title{Table of Conflict of Laws Cases}
\\def \\Author{Benedict Stanley}

\\title{\\Title}
\\author{\\Author}
\\date{\\today}

\\usepackage{fancyhdr}
\\pagestyle{fancy}
\\fancyhf{}
\\fancyhead{}
\\fancyhead[L]{}
\\fancyhead[R]{}
\\fancyhead[C]{}

\\fancyfoot[L]{\\Title}
\\fancyfoot[R]{\\thepage}
\\renewcommand{\\headrulewidth}{0pt}
\\renewcommand{\\footrulewidth}{0pt}


\\usepackage{tocloft}

\\addtolength{\\cftsecnumwidth}{2pt}
\\addtolength{\\cftsubsecnumwidth}{5pt}
\\addtolength{\\cftsubsubsecnumwidth}{9pt}

\\begin{document}

\\maketitle

\\tableofcontents
"""

# These functions generate the main "dict" with the text information based on the information given in the data_path.

def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection


def make_cases_dict(data_path):
    # Step 1: obtain all of the cases.
    temp_connection = create_connection(data_path)
    cur = temp_connection.cursor()
    cur.execute("SELECT * FROM cases ORDER BY year;")
    rows = cur.fetchall()
    return_dict = dict()
    for case in rows:
        # Get all the relevant data.
        id = case[0]
        name = case[1].replace("&", "\\&")
        year = case[2]
        nom_cit = case[3].replace("&", "\\&")
        er_cit = case[4].replace("&", "\\&")
        court = case[5].replace("&", "\\&")
        link = case[6]
        comment = case[7].replace("&", "\\&")
        # This is a temporary dictionary, which simply goes as a sub-dictionary into the main one.
        temp_dict = dict()
        # Make the "string" which is to be used as the return-value.
        if er_cit == "None":
            title_string = "\\textit{" + name + "} (" + str(year) + ") " +  nom_cit
        elif nom_cit == "None":
            title_string = "\\textit{" + name + "} [" + str(year) + "] " +  er_cit
        else:
            title_string = "\\textit{" + name + "} (" + str(year) + ") " + nom_cit + ", " +  er_cit
        temp_dict["Name"] = title_string
        temp_dict["Comment"] = comment
        temp_dict["Court"] = court
        temp_dict["Link"] = link
        return_dict[id] = temp_dict
    return return_dict

# These functions are the various ones used for obtaing the data from the database.

# This function obtains the "subjects" tags.

def obtain_subject_tags_as_string(data_path, id):
    temp_connection = create_connection(data_path)
    cur = temp_connection.cursor()
    cur.execute("SELECT subjectsId FROM subjectsCrossref WHERE caseID=" + str(id) + ";")
    rows = cur.fetchall()
    string = ""
    x = 0
    for row in rows:
        cur.execute("SELECT name FROM subjects WHERE id=" + str(row[0]) + ";")
        raw_name = (cur.fetchone())[0]
        raw_name = str(raw_name)
        raw_name = raw_name.replace("_", " ")
        if x < len(rows)-1:
            string = string + raw_name + "---"
        else:
            string = string + raw_name
        x = x + 1
    return string

def obtain_legal_area_as_string(data_path, id):
    temp_connection = create_connection(data_path)
    cur = temp_connection.cursor()
    cur.execute("SELECT leal_area_id FROM legalAreaCrossref WHERE caseID=" + str(id) + ";")
    rows = cur.fetchall()
    string = ""
    x = 0
    for row in rows:
        cur.execute("SELECT name FROM legalArea WHERE legal_area_id=" + str(row[0]) + ";")
        raw_name = (cur.fetchone())[0]
        raw_name = str(raw_name)
        raw_name = raw_name.replace("_", " ")
        if x < len(rows)-1:
            string = string + raw_name + "---"
        else:
            string = string + raw_name
        x = x + 1
    return string


def obtain_cited_in_as_string(data_path, id):
    temp_connection = create_connection(data_path)
    cur = temp_connection.cursor()
    cur.execute("SELECT authorID, comment FROM authorsCrossref WHERE caseID=" + str(id) + ";")
    rows = cur.fetchall()
    string = ""
    x = 0
    for row in rows:
        author_id = row[0]
        comment = row[1]
        comment = str(comment)
        comment = comment.strip()
        cur.execute("SELECT name from authors WHERE authorID=" + str(author_id) + ";")
        author_name = (cur.fetchone()[0])
        author_name = str(author_name)
        author_name = author_name.replace("_", " ")
        comment = comment.replace("_", " ")
        if x < len(rows)-1:
            string = string + author_name + " (" + comment + "); "
        else:
            string = string + author_name + " (" + comment + ")"
        x = x +1
    return string

def obtain_authors_as_string(data_path, id):
    temp_connection = create_connection(data_path)
    cur = temp_connection.cursor()
    cur.execute("SELECT author_cited FROM citingCrossref WHERE caseID=" + str(id) + ";")
    rows = cur.fetchall()
    string = ""
    x = 0
    for row in rows:
        cur.execute("SELECT name from citing WHERE author_citing_id=" + str(row[0]) + ";")
        author_name = cur.fetchone()
        author_name = author_name[0]
        author_name = str(author_name)
        author_name = author_name.replace("_", "")
        if x < len(rows)-1:
            string = string + author_name + ", "
        else:
            string = string + author_name + "."
        x = x+1
    return string

def obtain_key_terms_as_string(data_path, id):
    temp_connection = create_connection(data_path)
    cur = temp_connection.cursor()
    cur.execute("SELECT term_id FROM termsCrossref WHERE caseID=" + str(id) + ";")
    rows = cur.fetchall()
    string = ""
    x = 0
    for row in rows:
        cur.execute("SELECT name from terms WHERE term_id=" + str(row[0]) + ";")
        term_name = cur.fetchone()
        term_name = term_name[0]
        term_name = str(term_name)
        term_name = term_name.replace("_", "")
        if x < len(rows)-1:
            string = string + term_name + ", "
        else:
            string = string + term_name
        x = x+1
    return string

def obtain_subject_id_list_as_string(data_path, list):
    string = str(list)
    string = string.replace("[", "")
    string = string.replace("]", "")
    temp_connection = create_connection(data_path)
    cur = temp_connection.cursor()
    cur.execute("SELECT id FROM subjects WHERE name in(" + string + ");")
    ids = cur.fetchall()
    return_string = ""
    x = 0
    for id in ids:
        if x < len(ids)-1:
            return_string = return_string + str(id[0]) + ", "
        else:
            return_string = return_string + str(id[0])
        x = x+1
    return return_string

def obtain_cite_in_id_list_as_string(data_path, list):
    string = str(list)
    string = string.replace("[", "")
    string = string.replace("]", "")
    temp_connection = create_connection(data_path)
    cur = temp_connection.cursor()
    cur.execute("SELECT authorID FROM authors WHERE name in(" + string + ");")
    ids = cur.fetchall()
    return_string = ""
    x = 0
    for id in ids:
        if x < len(ids)-1:
            return_string = return_string + str(id[0]) + ", "
        else:
            return_string = return_string + str(id[0])
        x = x+1
    return return_string

def obtain_legal_area_id_list_as_string(data_path, list):
    string = str(list)
    string = string.replace("[", "")
    string = string.replace("]", "")
    temp_connection = create_connection(data_path)
    cur = temp_connection.cursor()
    cur.execute("SELECT legal_area_id FROM legalArea WHERE name in(" + string + ");")
    ids = cur.fetchall()
    return_string = ""
    x = 0
    for id in ids:
        if x < len(ids)-1:
            return_string = return_string + str(id[0]) + ", "
        else:
            return_string = return_string + str(id[0])
        x = x+1
    return return_string

def obtain_authors_list_as_string(data_path, list):
    string = str(list)
    string = string.replace("[", "")
    string = string.replace("]", "")
    temp_connection = create_connection(data_path)
    cur = temp_connection.cursor()
    cur.execute("SELECT author_citing_id FROM citing WHERE name in(" + string + ");")
    ids = cur.fetchall()
    return_string = ""
    x = 0
    for id in ids:
        if x < len(ids)-1:
            return_string = return_string + str(id[0]) + ", "
        else:
            return_string = return_string + str(id[0])
        x = x+1
    return return_string

def obtain_terms_list_as_string(data_path, list):
    string = str(list)
    string = string.replace("[", "")
    string = string.replace("]", "")
    temp_connection = create_connection(data_path)
    cur = temp_connection.cursor()
    cur.execute("SELECT term_id FROM terms WHERE name in(" + string + ");")
    ids = cur.fetchall()
    return_string = ""
    x = 0
    for id in ids:
        if x < len(ids)-1:
            return_string = return_string + str(id[0]) + ", "
        else:
            return_string = return_string + str(id[0])
        x = x+1
    return return_string


# These classes and functions help produce the whole list of cases at the end.

class Whole_Cases_Section:

    def __init__ (self, section_name, preamble_text, cases_dict, data_path):
        self.section_name = section_name
        self.preamble_text = preamble_text
        self.cases_dict = cases_dict
        self.data_path = data_path

    def make_case_display(self, given_case, case_id):
        open_title = """
        \\begin{small}
        \\begin{center}
        """
        close_title = """
        \\end{center}
        """
        end_text = """
        \\end{small}\\\\
        \\rule{\\textwidth}{0.5pt}
        """
        subject_display = "\\textit{" + obtain_subject_tags_as_string(self.data_path, case_id) + " (" + obtain_legal_area_as_string(self.data_path, case_id) + ")" + "}\\\\"
        cited_in_display = obtain_cited_in_as_string(self.data_path, case_id)
        if len(cited_in_display) < 3:
            cited_in_display = ""
        else:
            cited_in_display = "\\textit{Cited in: }" + cited_in_display
        authors_display = obtain_authors_as_string(self.data_path, case_id)
        if len(authors_display) < 3:
            authors_display = "No known authors cited."
        else:
            authors_display = "\\textit{Authors refered to: }" + authors_display
        terms_display = obtain_key_terms_as_string(self.data_path, case_id)
        if len(terms_display) < 3:
            terms_display = ""
        else:
            terms_display = " \\textbf{Uses terms: }" + "[\\textit{" + terms_display + "}]. "
        court_display = "\\textbf{" + given_case["Court"] + "}. "
        case_name = "\\href{" + given_case["Link"] + "}{" + given_case["Name"] + "}"
        case_name = case_name + " \label{" + str(case_id) + "} "
        display_text = open_title + case_name + "\\\\ \n" + subject_display + close_title
        display_text = display_text + court_display + terms_display +  given_case["Comment"] + "\\\\" + cited_in_display + "\\\\" + authors_display
        display_text = display_text + end_text
        return display_text

    def produce_cases_text(self):
        return_string = ""
        for case in self.cases_dict:
            case_info = self.cases_dict[case]
            new_string = self.make_case_display(case_info, case)
            return_string = return_string + "\n" + new_string
        return return_string

    def overall_output(self):
        return_string = ""
        line_one = "\\section{" + self.section_name + "}\n"
        line_two = self.preamble_text + "\\\\ \n"
        main_contents = self.produce_cases_text()
        return_string = line_one + line_two + main_contents
        return return_string

# This is a more general-purpose class, which generates any given "section" with a list of cases.

class Case_Table:

    def __init__ (self, section_name, section_text, cases_dict, data_path, table_mode=0, subject_list=None, date_bounds=None, cite_in=None, legal_areas=None, terms=None, authors=None, section_type="section"):
        self.section_name = section_name
        self.section_text = section_text
        self.cases_dict = cases_dict
        self.data_path = data_path
        self.table_mode = table_mode
        self.subject_list = subject_list
        self.date_bounds = date_bounds
        self.cite_in = cite_in
        self.legal_areas = legal_areas
        self.terms = terms
        self.authors = authors
        self.section_type = section_type
        if self.subject_list == None:
            self.subject_id_list = None
        else:
            self.subject_id_list = obtain_subject_id_list_as_string(self.data_path, self.subject_list)
        if self.cite_in == None:
            self.cite_in_id_list = None
        else:
            self.cite_in_id_list = obtain_cite_in_id_list_as_string(self.data_path, self.cite_in)
        if self.legal_areas == None:
            self.legal_areas_list = None
        else:
            self.legal_areas_list = obtain_legal_area_id_list_as_string(self.data_path, self.legal_areas)
        if self.terms == None:
            self.terms_list = None
        else:
            self.terms_list = obtain_terms_list_as_string(self.data_path, self.terms)
        if self.authors == None:
            self.authors_list = None
        else:
            self.authors_list = obtain_authors_list_as_string(self.data_path, self.authors)

    def __str__ (self):
        return f"{self.table_mode, self.subject_list, self.date_bounds, self.cite_in, self.legal_areas, self.terms, self.authors}"

    def produce_query_text(self):
        opening_text = "SELECT * from cases WHERE "
        lines_of_conditions = []
        # Sorts out the date bounds.
        if self.date_bounds == None:
            pass
        else:
            lower_bound = self.date_bounds[0]
            upper_bound = self.date_bounds[1]
            # Where there is no lower bound.
            if lower_bound == 0:
                line = "year < " + str(upper_bound)
            # Where there is no upper bound.
            elif upper_bound == 0:
                line = "year>" + str(lower_bound)
            else:
                line = "year>" + str(lower_bound) + " AND \n"
                line = line + "year<" + str(upper_bound)
            lines_of_conditions.append(line)
        if self.subject_list == None:
            pass
        else:
            line = "id in (SELECT CaseID from subjectsCrossref WHERE subjectsId in(" + self.subject_id_list + "))"
            lines_of_conditions.append(line)
        if self.cite_in == None:
            pass
        else:
            line = "id in (SELECT CaseID from authorsCrossref WHERE authorID in(" + self.cite_in_id_list + "))"
            lines_of_conditions.append(line)
        if self.legal_areas == None:
            pass
        else:
            line = "id in (SELECT caseID from legalAreaCrossref WHERE leal_area_id in(" + self.legal_areas_list + "))"
            lines_of_conditions.append(line)
        if self.terms_list == None:
            pass
        else:
            line = "id in (SELECT caseID from termsCrossref WHERE term_id in (" + self.terms_list + "))"
            lines_of_conditions.append(line)
        if self.authors_list == None:
            pass
        else:
            line = "id in (SELECT caseID from citingCrossref WHERE author_cited in (" + self.authors_list + "))"
            lines_of_conditions.append(line)
        # Now to package up the query
        return_string = ""
        x = 0
        for item in lines_of_conditions:
            if x < len(lines_of_conditions)-1:
                return_string = return_string + item + " AND\n"
            else:
                return_string = return_string + item
            x = x+1
        return_string = opening_text + return_string + "\n ORDER BY year;"
        return return_string

    def perform_database_query(self):
        query_text = self.produce_query_text()
        temp_connection = create_connection(self.data_path)
        cur = temp_connection.cursor()
        cur.execute(query_text)
        rows = cur.fetchall()
        return rows

    def produce_table_contents_zero_mode(self):
        return_string = ""
        query_result = self.perform_database_query()
        first_line = "\\begin{longtable}{p{4cm} p{1.7cm} p{2.5cm} p{5cm} p{2.5cm}}\n\\hline\n"
        second_line = "Name & Court & Subject(s) & Comment & Cited By\\\\" + "\n\\hline"
        last_line = "\\end{longtable}"
        table_entries = ""
        for case in query_result:
            case_information = self.cases_dict[case[0]]
            name = case_information["Name"]
            court = "\\small{" + case_information["Court"] + "}"
            comment = "\\small{" + case_information["Comment"] + "}"
            if len(obtain_cited_in_as_string(self.data_path, case[0])) < 2:
                cited_in = " "
            else:
                cited_in = "\\small{" + obtain_cited_in_as_string(self.data_path, case[0]) + "}"
            if len(obtain_subject_tags_as_string(self.data_path, case[0])) < 2:
                subject_tags = " "
            else:
                subject_tags = "\\small{" +  obtain_subject_tags_as_string(self.data_path, case[0]) + "}"
            new_line = name + " & " + court + " & " + subject_tags + " & " + comment + " & " + cited_in + "\\\\ \n"
            table_entries = table_entries + new_line
        return_string = first_line + second_line + table_entries + last_line
        return return_string

    def produce_table_contents_one_mode(self):
        return_string = ""
        query_result = self.perform_database_query()
        first_line = "\\begin{enumerate}\n"
        last_line = "\\end{enumerate}\n"
        table_entries = ""
        for case in query_result:
             case_information = self.cases_dict[case[0]]
             name = case_information["Name"]
             display_name = "\\item{" + name + "}\n"
             table_entries = table_entries + display_name
        return_string = first_line + table_entries + last_line
        return return_string

    def produce_table_contents_two_mode(self):
        return_string = ""
        query_result = self.perform_database_query()
        first_line = "\\begin{enumerate}\n"
        last_line = "\\end{enumerate}\n"
        table_entries = ""
        for case in query_result:
             case_information = self.cases_dict[case[0]]
             name = case_information["Name"]
             terms_display = obtain_key_terms_as_string(self.data_path, case[0])
             terms_display = " [" + terms_display + "]"
             display_name = "\\item{" + name + terms_display + "}\n"
             table_entries = table_entries + display_name
        return_string = first_line + table_entries + last_line
        return return_string

    def produce_table_contents_three_mode(self):
        return_string = ""
        query_result = self.perform_database_query()
        first_line = "\\begin{enumerate}\n"
        last_line = "\\end{enumerate}\n"
        table_entries = ""
        for case in query_result:
             case_information = self.cases_dict[case[0]]
             name = case_information["Name"]
             authors_display = obtain_authors_as_string(self.data_path, case[0])
             authors_display = " [" + authors_display + "]"
             display_name = "\\item{" + name + authors_display + "}\n"
             table_entries = table_entries + display_name
        return_string = first_line + table_entries + last_line
        return return_string

    def produce_table_contents_combined(self):
        if self.table_mode == 0:
            table_contents = self.produce_table_contents_zero_mode()
            return table_contents
        elif self.table_mode == 1:
            table_contents = self.produce_table_contents_one_mode()
            return table_contents
        elif self.table_mode == 2:
            table_contents = self.produce_table_contents_two_mode()
            return table_contents
        elif self.table_mode == 3:
            table_contents = self.produce_table_contents_three_mode()
            return table_contents
        else:
            return "Invalid table type"

    def overall_output(self):
        return_string = ""
        line_one = "\\" + self.section_type + "{" + self.section_name + "}\n"
        line_two = self.section_text + "\\\\ \n"
        main_contents = self.produce_table_contents_combined()
        return_string = line_one + line_two + main_contents
        return return_string


# This is all the important data used to help generate the section names etc.

data = sys.argv[1]

tex_document = sys.argv[2]

overall_cases_section_name = "Chronological List of All Cases"

overall_cases_preamble_text = """
The following is a simple table containing all of the cases, sorted by date. Each entry includes all the relevant obtained information.
"""

cases_dict = make_cases_dict(data)

WholeCases = Whole_Cases_Section(overall_cases_section_name, overall_cases_preamble_text, cases_dict, data)

# Testing Area

open_up_document(OPEN, tex_document)

# The main cases related to contract.

insert_into_document(tex_document, "\n\\section{Choice of Law: Contract}\\\n")

lex_loci_con_preamble_text = """
These are all of the cases I have seen which either (1) seem to resolve issues themselves with reference to the law of the place where the contractual obligation originated, \\textit{or} (2) are cited by others as such. It should be noted that very few of these cases actually make use of the wording “\\textit{lex loci contractus}” within them.
"""

LLContractus = Case_Table("Contract: Resolution in Favour of Place of Contract's Inception", lex_loci_con_preamble_text, cases_dict, data, table_mode=0, subject_list=["Lex_Loci_Contractus", "Application_of_Lex_Loci_Con", "Lex_Loci_Con"], section_type="subsection")

insert_into_document(tex_document, LLContractus.overall_output())

lex_loci_sol_preamble_text = """
The following are the cases that lean the other way from the previous section. These either resolve issues by reference to party \\textit{intention} or \\textit{the loci solutionis}, or are referred to as such.
"""

LLSolInt = Case_Table("Contract: Resolution in Favour of Loci Solutionis or Party Intention", lex_loci_sol_preamble_text, cases_dict, data, table_mode=0, subject_list=["Application_of_Lex_Loci_Sol", "Contract_Intention"], section_type="subsection")

insert_into_document(tex_document, LLSolInt.overall_output())


# Delict related issues.


delict_tort_preamble_text = """
This is a vague list of any and all cases (there are not many of them) pertaining to torts or extra-contractual liability (these terms are obviously slippery) in some way.
"""

delict = Case_Table("Delicts or Torts", delict_tort_preamble_text, cases_dict, data, table_mode=0, subject_list=["Delict"])

insert_into_document(tex_document, delict.overall_output())


# Property related issues

property_preamble_text = """
These are all of the cases that on some level relate to property \\textit{in general} --- without any specific reference to in what way (however passingly).
"""

property_all = Case_Table("Property", property_preamble_text, cases_dict, data, table_mode=0, subject_list=["Property"])

insert_into_document(tex_document, property_all.overall_output())

# Real property

real_property_preamble_text = """
These are cases that in some level deal with real property. By in large, they resolve issues with reference to the \\textit{lex rei sitae.}
"""

Real_Property = Case_Table("Real Property (usually lex situs)", real_property_preamble_text, cases_dict, data, table_mode=0, subject_list=["Property_Real", "Property_Real_Extent"], section_type="subsection")


insert_into_document(tex_document, Real_Property.overall_output())


# Movable property and domicile.

moveable_property_preamble_text = """
These are the cases that refer to movable property, and, usually, specifically the application of the law of the domicile being the relevant rule.
"""

Movable_Property = Case_Table("Movable Property (usually domicile)", moveable_property_preamble_text, cases_dict, data, table_mode=0, subject_list=["Property_Domicile"], section_type="subsection")

insert_into_document(tex_document, Movable_Property.overall_output())

# Moving on to particular contexts and fact patterns.

insert_into_document(tex_document, "\n\\section{Particular Contexts}\\\n")

bill_of_exchange_preamble_text = """
The following are all of the cases (in a simple list) related to bills of exchange (on their facts). One will see that there are quite a number of them.
"""

BoE = Case_Table("Bills of Exchange", bill_of_exchange_preamble_text, cases_dict, data, table_mode=1, legal_areas=["Bill_of_Exchange"], section_type="subsection")

insert_into_document(tex_document, BoE.overall_output())

sale_of_goods_preable_text = """
The following are all of the cases (in a simple list) related on some level to sale of goods. A couple of these, it should be noted (problematically) include \\textbf{slaves}.
"""

Sale = Case_Table("Sale of Goods", sale_of_goods_preable_text, cases_dict, data, table_mode=1, legal_areas=["Sale", "Vendor_Purchaser"], section_type="subsection")

insert_into_document(tex_document, Sale.overall_output())

marriage_preable_text = """
These are all of the cases related to marriage on some level.
"""

Marriage = Case_Table("Marriage", marriage_preable_text, cases_dict, data, table_mode=1, legal_areas=["Marriage", "Marriage_Settlement", "Marriage_Contract", "Marriage_Divorce"], section_type="subsection")

insert_into_document(tex_document, Marriage.overall_output())

# Key terms

terms_preable_text = """
These are cases that use certain key terms, such as \\textit{lex situs} or \\textit{lex loci contractus} -- either by counsel (which is the most common) or by the bench itself. Noting when and how these arise is interesting for tracking the absortion of conflict-of-laws terminology in the English cases.
"""

all_terms = ["ius gentium", "lex loci", "comity", "law of nations", "lex loci contractus", "lex fori", "lex loci solutionis", "lex loci rei sitae", "lex domicilii", "lex rei sitae", "domicilum"]

KeyTerms = Case_Table("Cases Using Certain Key Terms", terms_preable_text, cases_dict, data, table_mode=2, terms=all_terms)


insert_into_document(tex_document, KeyTerms.overall_output())

# Certain authors being cited.

authors_preable_text = """
These are all of the cases that themselves show citation to (either by counsel or the bench) some continental writer.
"""

#orig_stdout = sys.stdout
#f = open('out.txt', 'w')
#sys.stdout = f

Authors = Case_Table("Cases Citing Certain Important Writers", authors_preable_text, cases_dict, data, table_mode=3, authors=["Vattel", "Grotius", "Puffendorf", "Bynkerschoek", "Huber", "Voet", "Story", "Burge", "Sanchez", "Gayll", "Boullenois", "Erskine"])

insert_into_document(tex_document, Authors.overall_output())

#sys.stdout = orig_stdout
#f.close()

# Then the final list of all of the cases

insert_into_document(tex_document, "\\newpage")

insert_into_document(tex_document, WholeCases.overall_output())

close_up_document(tex_document)
