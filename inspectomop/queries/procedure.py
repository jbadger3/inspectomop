"""
Procedure related OMOP data queries.

Adapted from: https://github.com/OHDSI/OMOP-Queries
"""
from sqlalchemy import select as _select, join as _join,\
    union as _union, union_all as _union_all, \
    distinct as _distinct, between as  _between, alias as _alias, \
    and_ as _and_, or_ as _or_, literal_column as _literal_column, func as _func


def procedure_concepts_for_keyword(keyword, inspector,return_columns=None):
    """
    Search for all concepts in the procedure domain (includes SNOMED-CT procedures, ICD9 procedures, CPT procedures and HCPCS procedures)
    for a given keyword.

    Parameters
    ----------
    keyword : str
        e.x. 'artery bypass'
    inspector : inspectomop.inspector.Inspector
    return_columns : list of str, optional
        - optional subset of columns to return from the query
        - columns : ['concept_id', 'concept_name', 'concept_code', 'concept_class_id', 'vocabulary_id', 'vocabulary_name']

    Returns
    -------
    results : inspectomop.results.Results

    Notes
    -----
    Original SQL

    P02: Find a procedure from a keyword::

        SELECT C.concept_id         Entity_Concept_Id,
               C.concept_name       Entity_Name,
               C.concept_code       Entity_Code,
               'Concept'            Entity_Type,
               C.concept_class_id      Entity_concept_class_id,
               C.vocabulary_id      Entity_vocabulary_id,
               V.vocabulary_name    Entity_vocabulary_name
        FROM
            concept   C
        INNER JOIN
            vocabulary V ON C.vocabulary_id = V.vocabulary_id
        LEFT OUTER JOIN
            concept_synonym S ON C.concept_id = S.concept_id
        WHERE
            (C.vocabulary_id IN ('ICD9Proc', 'CPT4', 'HCPCS') OR LOWER(C.concept_class_id) = 'procedure') AND
            C.concept_class_id IS NOT NULL AND
            C.standard_concept = 'S' AND
            (REGEXP_INSTR(LOWER(C.concept_name), LOWER('artery bypass')) > 0 OR
            REGEXP_INSTR(LOWER(S.concept_synonym_name), LOWER('artery bypass')) > 0) AND
            sysdate BETWEEN C.valid_start_date AND C.valid_end_date;
    """
    c = _alias(inspector.tables['concept'], 'c')
    v = _alias(inspector.tables['vocabulary'], 'v')
    s = _alias(inspector.tables['concept_synonym'])

    vocab_ids = ['SNOMED', 'ICD9Proc', 'ICD10PCS', 'CPT4', 'HCPCS']
    standard_concept = 'S'
    concept_domain = 'Procedure'
    j = _join(c, s, c.c.concept_id == s.c.concept_id)
    s1 = _select([c.c.concept_id,c.c.concept_name,c.c.concept_code,\
        c.c.concept_class_id, c.c.vocabulary_id, v.c.vocabulary_name]).\
        select_from(j).\
        where(_and_(\
            c.c.vocabulary_id.in_(vocab_ids),\
            c.c.concept_class_id != None,\
            c.c.domain_id == concept_domain,\
            c.c.standard_concept == standard_concept,\
        - seec.c.vocabulary_id == v.c.vocabulary_id))

    columns = [s1.c.concept_id,s1.c.concept_name,s1.c.concept_code, s1.c.concept_class_id, s1.c.vocabulary_id,s1.c.vocabulary_name]

    if return_columns:
        columns = [col for col in columns if col.name in return_columns]
    statement = _select(columns).select_from(s1).\
        where(\
            _func.lower(s1.c.concept_name).ilike('%{}%'.format(keyword.lower())))

    return inspector.execute(statement)
