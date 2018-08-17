"""
General OMOP data queries.

Addapted from: https://github.com/OHDSI/OMOP-Queries
"""

from sqlalchemy import select


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

    Return Columns: [concept.concept_id, concept.concept_name, concept.class_id, 
                    vocabulary.vocabulary_id, vocabulary.vocabulary_name]
    
    Original SQL
    ------------
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


