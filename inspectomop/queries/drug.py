"""
Drug related OMOP data queries.

Addapted from: https://github.com/OHDSI/OMOP-Queries
"""

from sqlalchemy import select as _select, join as _join,\
    union as _union, union_all as _union_all, \
    distinct as _distinct, between as  _between, alias as _alias, \
    and_ as _and_, or_ as _or_, literal_column as _literal_column, func as _func


__all__ = []

def drugs_for_ingredient_concept_id(concept_id, inspector,return_columns=None):
    """
    Get all drugs that contain a given ingredient.

    Parameters
    ----------
    concept_id : int
        concept_id corresponding to a drug ingredient

    inspector : inspectomop.Inspector object

    return_columns : list of strings representing the columns to return from the query
        *see Returns section below for full list


    Returns
    -------
    out : inspectomop.Results

    return_columns: ['ingredient_concept_id', 'ingredient_name', \
        'ingredient_concept_code', 'ingredient_concept_class_id', \
        'drug_concept_id', 'drug_name','drug_concept_code', \
        'drug_concept_class_id']

    Original SQL
    ------------
    D04: Find drugs by ingredient
    SELECT
        A.concept_id Ingredient_concept_id,
        A.concept_Name Ingredient_name,
        A.concept_Code Ingredient_concept_code,
        A.concept_Class_id Ingredient_concept_class,
        D.concept_id Drug_concept_id,
        D.concept_Name Drug_name,
        D.concept_Code Drug_concept_code,
        D.concept_Class_id Drug_concept_class
    FROM
        concept_ancestor CA,
        concept A,
        concept D
    WHERE
        CA.ancestor_concept_id = A.concept_id
        AND CA.descendant_concept_id = D.concept_id
        AND sysdate BETWEEN A.valid_start_date AND A.valid_end_date
        AND sysdate BETWEEN D.valid_start_date AND D.valid_end_date
        AND CA.ancestor_concept_id = 966991;
    """
    
    a = _alias(inspector.tables['concept'],'a')
    d = _alias(inspector.tables['concept'], 'd')
    ca = _alias(inspector.tables['concept_ancestor'] ,'ca')
    columns = [a.c.concept_id.label('ingredient_concept_id'), a.c.concept_name.label('ingredient_name'), \
        a.c.concept_code.label('ingredient_concept_code'), a.c.concept_class_id.label('ingredient_concept_class_id'), \
        d.c.concept_id.label('drug_concept_id'), d.c.concept_name.label('drug_name'),\
        d.c.concept_code.label('drug_concept_code'), d.c.concept_class_id.label('drug_concept_class_id')]
    if return_columns:
        col_list = ['ingredient_concept_id', 'ingredient_name', \
            'ingredient_concept_code', 'ingredient_concept_class_id', \
            'drug_concept_id', 'drug_name','drug_concept_code', \
            'drug_concept_class_id']
        columns = list(filter(lambda x: x in col_list, return_columns))
    statement = _select(columns).where(_and_(ca.c.ancestor_concept_id==a.c.concept_id,\
        ca.c.descendant_concept_id == d.c.concept_id, ca.c.ancestor_concept_id == concept_id))
    return inspector.execute(statement)


def ingredient_concept_ids_for_ingredient_names(ingredient_names, inspector,return_columns=None):
    """
    Get concept_ids for a list of ingredients.

    Parameters
    ----------
    ingredient_names : list
        

    inspector : inspectomop.Inspector object

    return_columns : list of strings representing the columns to return from the query
        *see Returns section below for full list


    Returns
    -------
    out : inspectomop.Results

    return_columns: ['ingredient_name','concept_id']

    Original SQL
    ------------
    SELECT
        concept_id,
        concept_name
    FROM
        concept,
    WHERE
        vocabulary_id = 'RxNorm'
        AND concept_class_id = 'Ingredient'
        AND lower(concept_name) IN ('ingredient_name_1')
    """
    concept = inspector.tables['concept']
    vocab_id = 'RxNorm'
    concept_class_id = 'Ingredient'
    columns = [concept.concept_name.label('ingredient_name'),concept.concept_id]
    if return_columns:
        col_list = ['concept_id', 'ingredient_name']
        columns = list(filter(lambda x: x in col_list, return_columns))
    statement = _select(columns).where(_and_(concept.vocabulary_id == vocab_id, concept.concept_class_id == concept_class_id, _func.lower(concept.concept_name).in_(map(str.lower,ingredient_names))))
    return inspector.execute(statement)
