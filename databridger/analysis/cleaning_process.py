"""Description of the Cleaning / Inspection Process that should be mimicked

Load data
---------

- Load data

- Convert columns to datatime if the format matches


Identify columns
----------------

- Print table sizes

- Identify keys (primary/foreign)
    - Option 1: by suffix _id
        easiest way to identify key columns if naming is consistent
    - Option 2: by overlap ratio==1
        finds all relationships
        cannot identify which key is primary and which is foreign
        problem with missing key entries
    - Option 3: by name
        find similar or equal names between tables

- Identify columns as:
    - keys
    - temporal
    - numeric
    - text
    - categorical

- Calculate summaries


Inspection
----------

Potential issues for **key columns**:

- duplicated values
    Reason: is foreign key
    Solution: set(foreign key) must be subset of a set(key) in a different table

- one key is unique in multiple tables
    Further Check: check if tables can be merged


"""