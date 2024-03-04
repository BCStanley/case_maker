# Overview 

`case_maker` is a tool for generating, updating, and querying a databse of cases. 

Cases are entered, for ease, in a basic `.xlsx` file. This is a poor solution, but it works well for now, and has the added benefit of being easily edited by multiple people (e.g., using google docs or similar tools.)

The cases are stored in a database in the `.db` format. SQL can be used to consult the database. 

That database can then be searched, and the output it produced as a `.tex` file. 

Shell scripts manage the whole process. 

## Basic Functionality

# Classes 

The following are the list of the main classes within the code. 

# `Case`

The `Case` class is the basic building-block of the whole program, making up the single unit of an individual case entry. It contains the following: 
1. `name`, which is a `str`, and must be unique.
   * This is how any case is identified, e.g. "Robinson v Bland", "Re Melbourne"... 
2. `year`, which is an `int`.
    * E.g. 1799, 1850... 
3. `court`, which is a `str`. 
    * "KB", "Admiralty," "CP" etc. 
4. `nom_cite` which is a `str` or `None`. 
    * These are used for nominate citations, e.g. "2 Bing 314". 
5. `er_cite` which is a `str` or `None`. 
    * These are used for _English Reports_ citations (e.g. "3 ER 316") _or_; 
    * Ordinary citations, being the type that take square brackets (e.g. "AC 415"). 
    * If a case has an AC, KB, etc. citation --- it should be entered as an `er_cite`. 
6. `comment` which is a `str` or `None`. 
    * A basic string, giving relevant details or outlines of the case. 
7. `link` which is a `str` or `None`. 
   * Typically, this will be a link to `heinonline`, but other platforms and links are available. 
8. `area_tags` which is a `list` of `str` or `None`.
   * These provide the general legal or institutional context (e.g. sale, bill of exchange).
9. `subject_tags` which is a `list` of `str` or `None`.
   * These provide the relevant subject data, what _legal issues_ are involved. 
10. `cite_in_tags` which is a `dict` of `{str: str,...}` or `None`.
   * These authors are usually listed in a form that includes the works involved , e.g. "Story_Ed1" for the First Edition of Story's _Conflict of Laws_. 
   * The entires are stored as a dictionary, {author: what it is cited for}.  
11. `authors` which is a `list` of `str` or `None`.
   * These are the _authors cited by the case_. 
   * These might be cited by counsel or by the bench,or sometimes by the reporter. 
12. `special_terms` which is a`list` of `str` or `None`.
    * Special legal terms, like "_lex loci contractus_" or _privity of contract_ that are used. 

The class also contains the possibility of a `related_cases` entry. This is not used currently. 

### Properties 

### Static Methods 

## `Casebook`

