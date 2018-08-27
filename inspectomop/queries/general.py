"""
General OMOP data queries.

Addapted from: https://github.com/OHDSI/OMOP-Queries
"""

from sqlalchemy import select, join, distinct, between, alias, and_, or_
import datetime as _datetime

__all__ = ['concepts_for_concept_ids','synonyms_for_concept_ids']

def concepts_for_concept_ids(concept_ids, inspector,return_columns=None):
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

    Return Columns: [concept.concept_id, concept.concept_name,concept.concept_code,
        concept.class_id, concept.standard_concept, vocabulary.vocabulary_id,
        vocabulary.vocabulary_name]

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
        columns = list(filter(lambda x: x in columns, return_columns))

    statement = select(columns).where(concept.concept_id.in_(list(concept_ids))).where(concept.vocabulary_id == vocabulary.vocabulary_id)

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

    Return Columns: [concept.concept_id, concept.concept_name, concept.class_id,
                    vocabulary.vocabulary_id, vocabulary.vocabulary_name]

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
        columns = list(filter(lambda x: x in columns, return_columns))
    statement = select(columns).where(concept.concept_id.in_(list(concept_ids))).where(concept.concept_id == concept_synonym.concept_id).where(concept.vocabulary_id==vocabulary.vocabulary_id)
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

    Return Columns: [concept.concept_id, concept.concept_name,concept.concept_code, concept.class_id,
                    vocabulary.vocabulary_id, concept.domain_id]

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

    c1 = alias(inspector.tables['concept'],'c1')
    c2 = alias(inspector.tables['concept'], 'c2')
    cr = alias(inspector.tables['concept_relationship'] ,'cr')

    columns = [c1.c.domain_id, c2.c.concept_id, \
        c2.c.concept_id, c2.c.concept_name, \
        c2.c.concept_code, c2.c.concept_class_id,\
        c2.c.vocabulary_id, c2.c.domain_id]

    if return_columns:
        columns = list(filter(lambda x: x in columns, return_columns))


    j1 = join(cr,c1,  c1.c.concept_id == cr.c.concept_id_1)
    j2 = join(j1,c2, c2.c.concept_id == cr.c.concept_id_2)
    todays_date = _datetime.date.isoform
    relationship_id = 'Maps to'
    statement = select(columns).distinct().select_from(j2).where(and_(cr.c.relationship_id==relationship_id,c1.c.concept_code == source_code,c1.c.vocabulary_id == source_vocab_id))
    return inspector.execute(statement)
