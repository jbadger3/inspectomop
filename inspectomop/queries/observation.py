"""
Observation related OMOP data queries.

Adapted from: https://github.com/OHDSI/OMOP-Queries
"""
from sqlalchemy import select as _select, join as _join,\
    union as _union, union_all as _union_all, \
    distinct as _distinct, between as  _between, alias as _alias, \
    and_ as _and_, or_ as _or_, literal_column as _literal_column, func as _func

def observation_concepts_for_keyword(keyword, inspector,return_columns=None):
    """
    Search for LOINC and UCUM concepts by keyword.

    Parameters
    ----------
    keyword : str
        e.x. 'LDL'
    inspector : inspectomop.inspector.Inspector
    return_columns : list of str, optional
        - optional subset of columns to return from the query
        - columns : ['concept_id','concept_name','concept_code', 'concept_class_id', 'vocabulary_id',
            'vocabulary_name']

    Returns
    -------
    results : inspectomop.results.Results

    Notes
    -----
    Original SQL

    O1: Find a Observation from a keyword::

        SELECT
            T.Entity_Concept_Id,
            T.Entity_Name,
            T.Entity_Code,
            T.Entity_Type,
            T.Entity_concept_class_id,
            T.Entity_vocabulary_id,
            T.Entity_vocabulary_name
        FROM   (
            SELECT
                C.concept_id       Entity_Concept_Id,
                C.concept_name     Entity_Name,
                C.concept_code     Entity_Code,
                'Concept'          Entity_Type,
                C.concept_class_id    Entity_concept_class_id,
                C.vocabulary_id    Entity_vocabulary_id,
                V.vocabulary_name  Entity_vocabulary_name,
                C.valid_start_date,
                C.valid_end_date
            FROM
                concept         C,
                vocabulary      V
            WHERE
                C.vocabulary_id IN ('LOINC', 'UCUM') AND
                C.concept_class_id IS NOT NULL AND
                C.standard_concept = 'S' AND
                C.vocabulary_id = V.vocabulary_id
    	       ) T
    	WHERE
            REGEXP_INSTR(LOWER(REPLACE(REPLACE(T.Entity_Name, ' ', ''), '-', '')),
                LOWER(REPLACE(REPLACE('LDL' , ' ', ''), '-', ''))) > 0 AND
            sysdate BETWEEN T.valid_start_date AND T.valid_end_date
    """

    c = _alias(inspector.tables['concept'], 'c')
    v = _alias(inspector.tables['vocabulary'], 'v')
    vocab_ids = ['LOINC', 'UCUM']
    standard_concept = 'S'
    s1 = _select([c.c.concept_id,c.c.concept_name,c.c.concept_code,\
        c.c.concept_class_id, c.c.vocabulary_id, v.c.vocabulary_name]).\
        where(_and_(\
            c.c.vocabulary_id.in_(vocab_ids),\
            c.c.concept_class_id != None,\
            c.c.standard_concept == standard_concept,\
            c.c.vocabulary_id == v.c.vocabulary_id))

    columns = [s1.c.concept_id,s1.c.concept_name,s1.c.concept_code, s1.c.concept_class_id, s1.c.vocabulary_id,s1.c.vocabulary_name]

    if return_columns:
        columns = [col for col in columns if col.name in return_columns]
    statement = _select(columns).select_from(s1).\
        where(_func.lower(s1.c.concept_name).ilike('%{}%'.format(keyword.lower())))

    return inspector.execute(statement)
