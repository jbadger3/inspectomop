"""
General OMOP data queries.

Addapted from: https://github.com/OHDSI/OMOP-Queries
"""

from sqlalchemy import select as _select, join as _join,\
    union as _union, union_all as _union_all, \
    distinct as _distinct, between as  _between, alias as _alias, \
    and_ as _and_, or_ as _or_, literal_column as _literal_column
import datetime as _datetime

__all__ = ['concepts_for_concept_ids','synonyms_for_concept_ids','related_concepts_for_concept_id']

def concepts_for_concept_ids(concept_ids, inspector,return_columns=None):
    """
    Returns concept information for a list of concept_ids

    Parameters
    ----------
    concept_ids : iterable list, pandas.Series, or 1D numpy.array
        list of concept_ids to query on

    inspector : inspectomop.Inspector object

    return_columns : list of strings specifying columns to return
        *see Returns section below for complete list

    Returns
    -------
    out : inspectomop.Results

    Return Columns: ['concept_id', 'concept_name', 'concept_code', 'concept_class_id',\
        'standard_concept', 'vocabulary_id', 'vocabulary_name']

    Original SQL
    ------------
    https://github.com/OHDSI/OMOP-Queries

    G01: Find concept by concept ID

    SELECT C.concept_id, C.concept_name, C.concept_code, C.concept_class_id,
        C.standard_concept, C.vocabulary_id, V.vocabulary_name
    FROM concept C, vocabulary V
    WHERE C.concept_id = 192671
    AND C.vocabulary_id = V.vocabulary_id
    AND sysdate BETWEEN valid_start_date
    AND valid_end_date;
    """
    concept = inspector.tables['concept']
    vocabulary = inspector.tables['vocabulary']
    columns = [concept.concept_id, concept.concept_name, concept.concept_code, concept.concept_class_id, concept.standard_concept, concept.vocabulary_id, vocabulary.vocabulary_name]
    if return_columns:
        col_names = ['concept_id', 'concept_name', 'concept_code', 'concept_class_id',\
            'standard_concept', 'vocabulary_id', 'vocabulary_name']
        columns = list(filter(lambda x: x in col_names, return_columns))

    statement = _select(columns).where(concept.concept_id.in_(list(concept_ids))).where(concept.vocabulary_id == vocabulary.vocabulary_id)

    return inspector.execute(statement)


def synonyms_for_concept_ids(concept_ids, inspector,return_columns=None):
    """
    Returns concept information for a list of concept_ids

    Parameters
    ----------
    concept_ids : iterable list, pandas.Series, or 1D numpy.array
        list of concept_ids to query on

    inspector : inspectomop.Inspector object

    return_columns : list of table.column attributes
        if specfied, only returns the specified columns in the results


    Returns
    -------
    out : inspectomop.Results

    Return Columns: ['concept_id', 'concept_synonym_name']

    Original SQL
    ------------
    G04: Find synonyms for a given concept ID

    SELECT C.concept_id, S.concept_synonym_name
    FROM concept C, concept_synonym S, vocabulary V
    WHERE C.concept_id = 192671
    AND C.concept_id = S.concept_id
    AND C.vocabulary_id = V.vocabulary_id
    AND sysdate BETWEEN C.valid_start_date AND C.valid_end_date;
    """

    concept = inspector.tables['concept']
    concept_synonym = inspector.tables['concept_synonym']
    vocabulary = inspector.tables['vocabulary']
    columns = [concept.concept_id, concept_synonym.concept_synonym_name]
    if return_columns:
        col_names = ['concept_id', 'concept_synonym_name']
        columns = list(filter(lambda x: x in col_names, return_columns))
    statement = _select(columns).where(concept.concept_id.in_(list(concept_ids))).where(concept.concept_id == concept_synonym.concept_id).where(concept.vocabulary_id==vocabulary.vocabulary_id)
    return inspector.execute(statement)

def standard_vocab_for_source_code(source_code,source_vocab_id, inspector,return_columns=None):
    """
    Convert source codes to all mapped standard vocabulary concepts.

    Parameters
    ----------
    source_codes : string
        alphanumeric source_codes to query on e.g ICD-9 ['250.00','250.01']

    source_vocab_id : string
        vocabulary_id from the vocabulary table e.g 'ICD9CM'
            see https://github.com/OHDSI/CommonDataModel/wiki/VOCABULARY for a full list

    inspector : inspectomop.Inspector object

    return_columns : list of table.column attributes
        if specfied, only returns the specified columns in the results


    Returns
    -------
    out : inspectomop.Results

    Return Columns: ['domain_id', 'concept_id', \
         'concept_name', \
        'concept_code', 'concept_class_id',\
        'vocabulary_id', 'target_concept_domain']

    Original SQL
    ------------
    G05: Translate a code from a source to a standard vocabulary.

    SELECT DISTINCT\
        c1.domain_id,
        c2.concept_id         as Concept_Id,
        c2.concept_name       as Concept_Name,
        c2.concept_code       as Concept_Code,
        c2.concept_class_id   as Concept_Class,
        c2.vocabulary_id      as Concept_Vocabulary_ID,
        c2.domain_id          as Target_concept_Domain
    FROM concept_relationship cr
    JOIN concept c1 ON c1.concept_id = cr.concept_id_1
    JOIN concept c2 ON c2.concept_id = cr.concept_id_2
    WHERE cr.relationship_id = 'Maps to'
    AND c1.concept_code IN ('070.0')
    AND c1.vocabulary_id = 'ICD9CM'
    AND sysdate BETWEEN cr.valid_start_date AND cr.valid_end_date;
    """

    c1 = _alias(inspector.tables['concept'],'c1')
    c2 = _alias(inspector.tables['concept'], 'c2')
    cr = _alias(inspector.tables['concept_relationship'] ,'cr')

    columns = [c1.c.domain_id, c2.c.concept_id, \
        c2.c.concept_name, c2.c.concept_code, c2.c.concept_class_id,\
        c2.c.vocabulary_id, c2.c.domain_id.label('target_concept_domain')]

    if return_columns:
        col_names = ['domain_id', 'concept_id', \
             'concept_name', \
            'concept_code', 'concept_class_id',\
            'vocabulary_id', 'target_concept_domain']
        columns = list(filter(lambda x: x in col_names, return_columns))


    j1 = _join(cr,c1,  c1.c.concept_id == cr.c.concept_id_1)
    j2 = _join(j1,c2, c2.c.concept_id == cr.c.concept_id_2)
    todays_date = _datetime.date.isoform
    relationship_id = 'Maps to'
    statement = _select(columns).distinct().select_from(j2).where(_and_(cr.c.relationship_id==relationship_id,c1.c.concept_code == source_code,c1.c.vocabulary_id == source_vocab_id))
    return inspector.execute(statement)

def concepts_and_descendants_for_source_code(source_code,source_vocab_id, inspector):
    """
    TODO

    Find all concepts that are direct maps of a source code and all descendants of those concepts.

    Parameters
    ----------
    source_codes : string
        alphanumeric source_codes to query on e.g ICD-9 ['250.00','250.01']

    source_vocab_id : string
        vocabulary_id from the vocabulary table e.g 'ICD9CM'
            see https://github.com/OHDSI/CommonDataModel/wiki/VOCABULARY for a full list

    inspector : inspectomop.Inspector object

    return_columns : list of table.column attributes
        if specfied, only returns the specified columns in the results

    Returns
    -------
    out : inspectomop.Results

    Return Columns:

    Original SQL
    ------------
    G06: Find concepts and their descendants that are covered by a given source code

    WITH dm AS ( -- collect direct maps
    SELECT  c1.concept_code as source_code,
            c1.vocabulary_id,
            c1.domain_id,
            c2.concept_id        as target_concept_id,
            c2.concept_name      as target_concept_name,
            c2.concept_code      as target_concept_code,
            c2.concept_class_id  as target_concept_class,
            c2.vocabulary_id     as target_concept_vocab_id,
            'Direct map'         as target_Type
    FROM  concept_relationship cr
    JOIN concept c1 ON cr.concept_id_1 = c1.concept_id
    JOIN concept c2 ON cr.concept_id_2 = c2.concept_id
    WHERE   cr.relationship_id = 'Maps to'
    AND     c1.concept_code IN ('410.0')
    AND     c1.vocabulary_id = 'ICD9CM'
    AND     sysdate BETWEEN cr.valid_start_date AND cr.valid_end_date)
    SELECT dm.source_code,
           dm.vocabulary_id,
           dm.domain_id,
           dc.concept_id        AS        target_concept_id,
           dc.concept_name        AS target_concept_name,
           dc.concept_code AS target_concept_code,
           dc.concept_class_id AS target_concept_class,
           dc.vocabulary_id AS target_concept_vocab_id,
        'Descendant of direct map' as target_Type
    FROM concept_ancestor ca -- collect descendants which includes ancestor itself
    JOIN dm ON ca.ancestor_concept_id = dm.target_concept_id
    JOIN concept dc ON ca.descendant_concept_id = dc.concept_id
    WHERE dc.standard_concept = 'S';
    """

def related_concepts_for_concept_id(concept_id, inspector,return_columns=None):
    """
    Find all concepts related to a concept_id.

    Parameters
    ----------
    concept_id : integer
        concept_id of interest from the concept table

    inspector : inspectomop.Inspector object

    return_columns : list of strings for column names to return
        * see Results below for full list

    Returns
    -------
    out : inspectomop.Results

    Return Columns: ['relationship_polarity','relationship_id', 'relationship_name', \
        'concept_id', 'concept_name', \
        'concept_code', 'concept_class_id',\
        'vocabulary_id', 'vocabulary_name']

    Original SQL
    ------------
    G07: Find concepts that have a relationship with a given concept

    SELECT 'Relates to' relationship_polarity, CR.relationship_ID,
        RT.relationship_name, D.concept_Id concept_id,
        D.concept_Name concept_name, D.concept_Code concept_code,
        D.concept_class_id concept_class_id, D.vocabulary_id concept_vocab_ID,
        VS.vocabulary_name concept_vocab_name
    FROM concept_relationship CR, concept A, concept D,
        vocabulary VA, vocabulary VS, relationship RT
    WHERE CR.concept_id_1 = A.concept_id
    AND A.vocabulary_id = VA.vocabulary_id
    AND CR.concept_id_2 = D.concept_id
    AND D.vocabulary_id = VS.vocabulary_id
    AND CR.relationship_id = RT.relationship_ID
    AND A.concept_id = 192671
    AND sysdate BETWEEN CR.valid_start_date
    AND CR.valid_end_date
    UNION ALL SELECT 'Is related by' relationship_polarity,
        CR.relationship_ID, RT.relationship_name, A.concept_Id concept_id,
        A.concept_name concept_name, A.concept_code concept_code,
        A.concept_class_id concept_class_id, A.vocabulary_id concept_vocab_ID,
        VA.Vocabulary_Name concept_vocab_name
    FROM concept_relationship CR, concept A, concept D, vocabulary VA, vocabulary VS, relationship RT
    WHERE CR.concept_id_1 = A.concept_id
    AND A.vocabulary_id = VA.vocabulary_id
    AND CR.concept_id_2 = D.concept_id
    AND D.vocabulary_id = VS.vocabulary_id
    AND CR.relationship_id = RT.relationship_ID
    AND D.concept_id = 192671
    AND sysdate BETWEEN CR.valid_start_date
    AND CR.valid_end_date;
    """
    cr = _alias(inspector.tables['concept_relationship'],'cr')
    a = _alias(inspector.tables['concept'], 'ca')
    d = _alias(inspector.tables['concept'] ,'cd')
    va = _alias(inspector.tables['vocabulary'], 'va')
    vs = _alias(inspector.tables['vocabulary'], 'vs')
    rt = _alias(inspector.tables['relationship'], 'rt')
    columns = [cr.c.relationship_id, rt.c.relationship_name, \
        d.c.concept_id, d.c.concept_name, \
        d.c.concept_code, d.c.concept_class_id,\
        d.c.vocabulary_id, vs.c.vocabulary_name]
    if return_columns:
        col_names = ['relationship_polarity','relationship_id', 'relationship_name', \
            'concept_id', 'concept_name', \
            'concept_code', 'concept_class_id',\
            'vocabulary_id', 'vocabulary_name']
        columns = list(filter(lambda x: x in col_names, return_columns))
    relates_to = _select([_literal_column("\'Relates to\'").label('relationship_polarity')] + columns).where(_and_(cr.c.concept_id_1 == a.c.concept_id, \
            a.c.vocabulary_id == va.c.vocabulary_id, cr.c.concept_id_2 == d.c.concept_id, \
            d.c.vocabulary_id == vs.c.vocabulary_id, cr.c.relationship_id == rt.c.relationship_id, \
            a.c.concept_id == concept_id))
    related_by = _select([_literal_column("\'Is related by\'").label('relationship_polarity')] + columns).where(_and_(cr.c.concept_id_1 == a.c.concept_id, \
            a.c.vocabulary_id == va.c.vocabulary_id, cr.c.concept_id_2 == d.c.concept_id, \
            d.c.vocabulary_id == vs.c.vocabulary_id, cr.c.relationship_id == rt.c.relationship_id, \
            d.c.concept_id == concept_id))
    statement = _union_all(relates_to,related_by)
    return inspector.execute(statement)
