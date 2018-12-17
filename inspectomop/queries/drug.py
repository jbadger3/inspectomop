"""
Drug related OMOP data queries.
===============================

Adapted from: https://github.com/OHDSI/OMOP-Queries
"""

from sqlalchemy import select as _select, join as _join,\
    union as _union, union_all as _union_all, \
    distinct as _distinct, between as  _between, alias as _alias, \
    and_ as _and_, or_ as _or_, literal_column as _literal_column, func as _func


def ingredients_for_drug_concept_ids(concept_ids, inspector, return_columns=None):
    """
    Get ingredients for brand or generic drug concept_ids.

    Parameters
    ----------
    concept_id : list of int
        concept_ids corresponding to brand or generic drug concept_ids
    inspector : inspectomop.inspector.Inspector
    return_columns : list of str, optional
        - optional subset of columns to return from the query
        - columns : ['drug_concept_id', 'drug_name', 'drug_concept_code', 'drug_concept_class', 'ingredient_concept_id', 'ingredient_name', 'ingredient_concept_code', 'ingredient_concept_class']

    Returns
    -------
    results : inspectomop.results.Results

    Notes
    -----
    Original SQL

    D03: Find ingredients of a drug::
        SELECT
            D.Concept_Id         drug_concept_id,
            D.Concept_Name       drug_name,
            D.Concept_Code       drug_concept_code,
            D.Concept_Class_id   drug_concept_class,
            A.Concept_Id         ingredient_concept_id,
            A.Concept_Name       ingredient_name,
            A.Concept_Code       ingredient_concept_code,
            A.Concept_Class_id   ingredient_concept_class
        FROM
            full_201706_omop_v5.concept_ancestor CA,
            full_201706_omop_v5.concept A,
            full_201706_omop_v5.concept D
        WHERE
            CA.descendant_concept_id = D.concept_id
            AND CA.ancestor_concept_id = A.concept_id
            AND LOWER(A.concept_class_id) = 'ingredient'
            AND sysdate BETWEEN A.VALID_START_DATE AND A.VALID_END_DATE
            AND sysdate BETWEEN D.VALID_START_DATE AND D.VALID_END_DATE
            AND CA.descendant_concept_id IN (939355, 19102189, 19033566)
    """

    a = _alias(inspector.tables['concept'],'a')
    d = _alias(inspector.tables['concept'], 'd')
    ca = _alias(inspector.tables['concept_ancestor'] ,'ca')
    columns = [d.c.concept_id.label('drug_concept_id'), d.c.concept_id.label('drug_name'), d.c.concept_code.label('drug_concept_code'), d.c.concept_class_id.label('drug_concept_class'), a.c.concept_id.label('ingredient_concept_id'), a.c.concept_name.label('ingredient_name'), a.c.concept_code.label('ingredient_concept_code'), a.c.concept_class_id.label('ingredient_concept_class')]
    if return_columns:
        columns = [col for col in columns if col.name in return_columns]
    statement = _select(columns).\
                where(_and_(\
                    ca.c.descendant_concept_id == d.c.concept_id,\
                    ca.c.ancestor_concept_id == a.c.concept_id,\
                    a.c.concept_class_id == 'Ingredient',\
                    ca.c.descendant_concept_id.in_(concept_ids)))
    return inspector.execute(statement)



def drug_concepts_for_ingredient_concept_id(concept_id, inspector,return_columns=None):
    """
    Get all drugs that contain a given ingredient.

    Parameters
    ----------
    concept_id : int
        concept_id corresponding to a drug ingredient
    inspector : inspectomop.inspector.Inspector
    return_columns : list of str, optional
        - optional subset of columns to return from the query
        - columns : ['ingredient_concept_id', 'ingredient_name', \
            'ingredient_concept_code', 'ingredient_concept_class_id', \
            'drug_concept_id', 'drug_name','drug_concept_code', \
            'drug_concept_class_id']

    Returns
    -------
    results : inspectomop.results.Results

    Notes
    -----
    Original SQL

    D04: Find drugs by ingredient::

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
        columns = [col for col in columns if col.name in return_columns]
    statement = _select(columns).where(_and_(ca.c.ancestor_concept_id==a.c.concept_id,\
        ca.c.descendant_concept_id == d.c.concept_id, ca.c.ancestor_concept_id == concept_id))
    return inspector.execute(statement)


def ingredient_concept_ids_for_ingredient_names(ingredient_names, inspector,return_columns=None):
    """
    Get concept_ids for a list of ingredients.

    Parameters
    ----------
    ingredient_names : list of str
    inspector : inspectomop.inspector.Inspector
    return_columns : list of str, optional
        - optional subset of columns to return from the query
        - columns : ['ingredient_name', 'concept_id']

    Returns
    -------
    results : inspectomop.results.Results

    Notes
    -----
    Original SQL::

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
        columns = [col for col in columns if col.name in return_columns]
    statement = _select(columns).\
                where(_and_(\
                    concept.vocabulary_id == vocab_id,\
                    concept.concept_class_id == concept_class_id,\
                    _func.lower(concept.concept_name).in_(map(str.lower,ingredient_names))))
    return inspector.execute(statement)

def drug_classes_for_drug_concept_id(concept_id, inspector,return_columns=None):
    """
    Returns drug classes for drug or ingredient concept_ids.

    Parameters
    ----------
    concept_id : int
    inspector : inspectomop.inspector.Inspector
    return_columns : list of str, optional
        - optional subset of columns to return from the query
        - columns : ['concept_id','concept_name','concept_code','concept_class_id', 'vocabulary_id', 'vocabulary_name']

    Returns
    -------
    results : inspectomop.results.Results

    Notes
    -----
    Original SQL

    D08: Find drug classes for a drug or ingredient::

        SELECT
            c1.concept_id                Class_Concept_Id,
            c1.concept_name              Class_Name,
            c1.concept_code              Class_Code,
            c1.concept_class_id          Classification,
            c1.vocabulary_id             Class_vocabulary_id,
            v1.vocabulary_name           Class_vocabulary_name,
            ca.min_levels_of_separation  Levels_of_Separation
        FROM
            concept_ancestor             ca,
            concept                      c1,
            vocabulary                   v1
        WHERE
            ca.ancestor_concept_id = c1.concept_id
            AND    c1.vocabulary_id IN ('NDFRT', 'ETC', 'ATC', 'VA Class')
            AND    c1.concept_class_id IN ('ATC','VA Class','Mechanism of Action','Chemical Structure','ETC','Physiologic Effect')
            AND    c1.vocabulary_id = v1.vocabulary_id
            AND    ca.descendant_concept_id = 1545999
            AND    sysdate BETWEEN c1.valid_start_date AND c1.valid_end_date;
    """
    c  = _alias(inspector.tables['concept'],'c')
    v = _alias(inspector.tables['vocabulary'], 'v')
    ca = _alias(inspector.tables['concept_ancestor'] ,'ca')

    columns = [c.c.concept_id, c.c.concept_name, c.c.concept_code, c.c.concept_class_id, v.c.vocabulary_name, ca.c.min_levels_of_separation]
    if return_columns:
        columns = [col for col in columns if col.name in return_columns]
    statement = _select(columns).\
                where(_and_(\
                    ca.c.ancestor_concept_id == c.c.concept_id,\
                    c.c.vocabulary_id.in_(['ATC','VA Class','Mechanism of Action','Chemical Structure','ETC','Physiologic Effect']),\
                    c.c.vocabulary_id == v.c.vocabulary_id,\
                    ca.c.descendant_concept_id == concept_id))
    return inspector.execute(statement)

def indications_for_drug_concept_id(concept_id, inspector,return_columns=None):
    """
    Find all indications for a drug given a concept_id.

    Parameters
    ----------
    concept_id : int
    inspector : inspectomop.inspector.Inspector
    return_columns : list of str, optional
        - optional subset of columns to return from the query
        - columns : ['relationship_name','concept_id','concept_name', 'vocabulary_id', 'vocabulary_name']

    Returns
    -------
    results : inspectomop.results.Results

    Notes
    -----
    SQL

    D13: Find indications as condition concepts for a drug::

        select
            a.min_levels_of_separation as a_min,
            an.concept_id as an_id,
            an.concept_name as an_name,
            an.vocabulary_id as an_vocab,
            an.domain_id as an_domain,
            an.concept_class_id as an_class,
            de.concept_id as de_id,
            de.concept_name as de_name,
            de.vocabulary_id as de_vocab,
            de.domain_id as de_domain,
            de.concept_class_id as de_class
        from
            concept an
        join
            concept_ancestor a on a.ancestor_concept_id=an.concept_id
        join
            concept de on de.concept_id=a.descendant_concept_id
        where
            an.concept_class_id in ('Ind / CI', 'Indication') -- One is for NDFRT, the other for FDB Indications
            and de.vocabulary_id in ('RxNorm', 'RxNorm Extension') -- You don't need that if you join directly with DRUG_EXPOSURE
            and lower(an.concept_name) like '%diabetes%'
"""
    c = _alias(inspector.tables['concept'],'c')
    de  = _alias(inspector.tables['concept'],'de')
    an = _alias(inspector.tables['concept'],'an')
    a = _alias(inspector.tables['concept_ancestor'],'a')
    r = _alias(inspector.tables['concept_relationship'],'r')
    j1 = _join(a, an, a.c.ancestor_concept_id == an.c.concept_id)
    j2 = _join(de, j1, de.c.concept_id == a.c.descendant_concept_id)
    j3 = _join(j2, r, r.c.concept_id_1 == an.c.concept_id)
    domain_id = 'Condition'
    j4 = _join(j3, c, _and_(c.c.concept_id == r.c.concept_id_2, c.c.domain_id==domain_id))

    concept_class_ids = ['Ind / CI', 'Indication']
    vocab_ids= ['RxNorm', 'RxNorm Extension']

    columns = [c.c.concept_id.label('c_concept_id'),c.c.concept_name.label('c_concept_name'),a.c.min_levels_of_separation, an.c.concept_id.label('an_concept_id'), an.c.concept_name.label('an_concept_name'), an.c.vocabulary_id.label('an_vocab'), de.c.concept_id.label('de_concept_id'), de.c.concept_name.label('de_concept_name'),de.c.vocabulary_id.label('de_vocab')]
    if return_columns:
        columns = [col for col in columns if col.name in return_columns]
    statement = _select(columns).\
                select_from(j4).where(_and_(an.c.concept_class_id.in_(concept_class_ids), de.c.vocabulary_id.in_(vocab_ids), de.c.concept_id == concept_id))

    return inspector.execute(statement)
