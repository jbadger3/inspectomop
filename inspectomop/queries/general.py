"""
General OMOP data queries.
==========================

Adapted from: https://github.com/OHDSI/OMOP-Queries
"""

from sqlalchemy import select as _select, join as _join,\
    union as _union, union_all as _union_all, \
    distinct as _distinct, between as  _between, alias as _alias, \
    and_ as _and_, or_ as _or_, literal_column as _literal_column

def concepts_for_concept_ids(concept_ids, inspector,return_columns=None):
    """
    Returns concept information for a list of concept_ids

    Parameters
    ----------
    concept_ids : list of int
    inspector : inspectomop.inspector.Inspector
    return_columns : list of str, optional
        - optional subset of columns to return from the query
        - columns : ['concept_id', 'concept_name', 'concept_code', 'concept_class_id', 'standard_concept', 'vocabulary_id', 'vocabulary_name']

    Returns
    -------
    results : inspectomop.results.Results

    Notes
    -----
    Original SQL

    G01: Find concept by concept ID::

        SELECT
            C.concept_id,
            C.concept_name,
            C.concept_code,
            C.concept_class_id,
            C.standard_concept,
            C.vocabulary_id,
            V.vocabulary_name
        FROM
            concept C,
            vocabulary V
        WHERE
            C.concept_id = 192671 AND
            C.vocabulary_id = V.vocabulary_id AND
            sysdate BETWEEN valid_start_date AND valid_end_date;
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
    concept_ids : list of int
    inspector : inspectomop.inspector.Inspector
    return_columns : list of str, optional
        - optional subset of columns to return from the query
        - columns : ['concept_id', 'concept_synonym_name']

    Returns
    -------
    results : inspectomop.results.Results

    Notes
    -----
    Original SQL

    G04: Find synonyms for a given concept ID::

        SELECT
            C.concept_id,
            S.concept_synonym_name
        FROM
            concept C,
            concept_synonym S,
            vocabulary V
        WHERE
            C.concept_id = 192671 AND
            C.concept_id = S.concept_id AND
            C.vocabulary_id = V.vocabulary_id AND
            sysdate BETWEEN C.valid_start_date AND C.valid_end_date;
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

def standard_vocab_for_source_code(source_code, source_vocab_id, inspector,return_columns=None):
    """
    Convert source code to all mapped standard vocabulary concepts.

    Parameters
    ----------
    source_codes : str
        alphanumeric source_code to query on e.g ICD-9 '250.00'
    source_vocab_id : str
        - vocabulary_id from the vocabulary table e.g 'ICD9CM'
        - see https://github.com/OHDSI/CommonDataModel/wiki/VOCABULARY for a full list
    inspector : inspectomop.inspector.Inspector
    return_columns : list of str, optional
        - optional subset of columns to return from the query
        - columns : ['domain_id', 'concept_id', 'concept_name', 'concept_code', 'concept_class_id', 'vocabulary_id', 'target_concept_domain']

    Returns
    -------
    results : inspectomop.results.Results

    Notes
    -----
    Original SQL

    G05: Translate a code from a source to a standard vocabulary::

        SELECT DISTINCT
            c1.domain_id,
            c2.concept_id         as Concept_Id,
            c2.concept_name       as Concept_Name,
            c2.concept_code       as Concept_Code,
            c2.concept_class_id   as Concept_Class,
            c2.vocabulary_id      as Concept_Vocabulary_ID,
            c2.domain_id          as Target_concept_Domain
        FROM
            concept_relationship cr
        JOIN
            concept c1 ON c1.concept_id = cr.concept_id_1
        JOIN
            concept c2 ON c2.concept_id = cr.concept_id_2
        WHERE
            cr.relationship_id = 'Maps to' AND
            c1.concept_code IN ('070.0') AND
            c1.vocabulary_id = 'ICD9CM' AND
            sysdate BETWEEN cr.valid_start_date AND cr.valid_end_date;
    """

    c1 = _alias(inspector.tables['concept'],'c1')
    c2 = _alias(inspector.tables['concept'], 'c2')
    cr = _alias(inspector.tables['concept_relationship'] ,'cr')

    columns = [c1.c.domain_id, c2.c.concept_id, \
        c2.c.concept_name, c2.c.concept_code, c2.c.concept_class_id,\
        c2.c.vocabulary_id, c2.c.domain_id.label('target_concept_domain')]

    if return_columns:
        columns = [col for col in columns if col.name in return_columns]

    j1 = _join(cr,c1,  c1.c.concept_id == cr.c.concept_id_1)
    j2 = _join(j1,c2, c2.c.concept_id == cr.c.concept_id_2)
    relationship_id = 'Maps to'
    statement = _select(columns).\
                distinct().\
                select_from(j2).\
                where(_and_(\
                    cr.c.relationship_id == relationship_id,\
                    c1.c.concept_code == source_code,\
                    c1.c.vocabulary_id == source_vocab_id))
    return inspector.execute(statement)


def related_concepts_for_concept_id(concept_id, inspector,return_columns=None):
    """
    Find all concepts related to a concept_id.

    Parameters
    ----------
    concept_id : int
        concept_id of interest from the concept table
    inspector : inspectomop.inspector.Inspector
    return_columns : list of str, optional
        - optional subset of columns to return from the query
        - columns : ['relationship_polarity','relationship_id', 'relationship_name', 'concept_id', 'concept_name', 'concept_code', 'concept_class_id', 'vocabulary_id', 'vocabulary_name']

    Returns
    -------
    results : inspectomop.results.Results

    Notes
    -----
    Original SQL

    G07: Find concepts that have a relationship with a given concept::

        SELECT
            'Relates to' relationship_polarity,
            CR.relationship_ID,
            RT.relationship_name,
            D.concept_Id concept_id,
            D.concept_Name concept_name,
            D.concept_Code concept_code,
            D.concept_class_id concept_class_id,
            D.vocabulary_id concept_vocab_ID,
            VS.vocabulary_name concept_vocab_name
        FROM
            concept_relationship CR,
            concept A,
            concept D,
            vocabulary VA,
            vocabulary VS,
            relationship RT
        WHERE
            CR.concept_id_1 = A.concept_id AND
            A.vocabulary_id = VA.vocabulary_id AND
            CR.concept_id_2 = D.concept_id AND
            D.vocabulary_id = VS.vocabulary_id AND
            CR.relationship_id = RT.relationship_ID AND
            A.concept_id = 192671 AND
            sysdate BETWEEN CR.valid_start_date AND CR.valid_end_date
        UNION ALL
        SELECT
            'Is related by' relationship_polarity,
            CR.relationship_ID,
            RT.relationship_name,
            A.concept_Id concept_id,
            A.concept_name concept_name,
            A.concept_code concept_code,
            A.concept_class_id concept_class_id,
            A.vocabulary_id concept_vocab_ID,
            VA.Vocabulary_Name concept_vocab_name
        FROM
            concept_relationship CR,
            concept A,
            concept D,
            vocabulary VA,
            vocabulary VS,
            relationship RT
        WHERE
            CR.concept_id_1 = A.concept_id AND
            A.vocabulary_id = VA.vocabulary_id AND
            CR.concept_id_2 = D.concept_id AND
            D.vocabulary_id = VS.vocabulary_id AND
            CR.relationship_id = RT.relationship_ID AND
            D.concept_id = 192671 AND
            sysdate BETWEEN CR.valid_start_date AND CR.valid_end_date;
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
        columns = [col for col in columns if col.name in return_columns]
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

def ancestors_for_concept_id(concept_id, inspector,return_columns=None):
    """
    Find all ancestor concepts for a concept_id.

    Parameters
    ----------
    concept_id : int
        concept_id of interest from the concept table
    inspector : inspectomop.inspector.Inspector
    return_columns : list of str, optional
        - optional subset of columns to return from the query
        - columns : ['ancestor_concept_id', 'ancestor_concept_name', 'ancestor_concept_code', 'ancestor_concept_class_id', 'vocabulary_id', 'min_levels_of_separation', 'max_levels_of_separation']

    Returns
    -------
    results : inspectomop.results.Results

    Notes
    -----
    Original SQL

    G08: Find ancestors for a given concept::

        SELECT
            C.concept_id as ancestor_concept_id,
            C.concept_name as ancestor_concept_name,
            C.concept_code as ancestor_concept_code,
            C.concept_class_id as ancestor_concept_class_id,
            C.vocabulary_id,
            VA.vocabulary_name,
            A.min_levels_of_separation,
            A.max_levels_of_separation
        FROM
            concept_ancestor A,
            concept C,
            vocabulary VA
        WHERE
            A.ancestor_concept_id = C.concept_id AND
            C.vocabulary_id = VA.vocabulary_id AND A.ancestor_concept_id<>A.descendant_concept_id AND A.descendant_concept_id = 192671 AND
            sysdate BETWEEN valid_start_date AND valid_end_date
        ORDER BY 5,7;
"""
    a = _alias(inspector.tables['concept_ancestor'],'a')
    c = _alias(inspector.tables['concept'],'c')
    va = _alias(inspector.tables['vocabulary'], 'va')

    columns = [c.c.concept_id.label('ancestor_concept_id'), c.c.concept_name.label('ancestor_concept_name'), c.c.concept_code.label('ancestor_concept_code'), c.c.concept_class_id.label('ancestor_concept_class_id'),\
               c.c.vocabulary_id, va.c.vocabulary_name, a.c.min_levels_of_separation, \
               a.c.max_levels_of_separation]
    if return_columns:
        columns = [col for col in columns if col.name in return_columns]
    statement = _select(columns).\
                where(_and_(\
                    a.c.ancestor_concept_id == c.c.concept_id,\
                    c.c.vocabulary_id == va.c.vocabulary_id, \
                    a.c.ancestor_concept_id != a.c.descendant_concept_id, \
                    a.c.descendant_concept_id == concept_id)). \
                    order_by(c.c.vocabulary_id, a.c.min_levels_of_separation)

    return inspector.execute(statement)

def descendants_for_concept_id(concept_id, inspector,return_columns=None):
    """
    Find all descendant concepts for a concept_id.

    Parameters
    ----------
    concept_id : int
        concept_id of interest from the concept table
    inspector : inspectomop.inspector.Inspector
    return_columns : list of str, optional
        - optional subset of columns to return from the query
        - columns : ['descendant_concept_id', 'descendant_concept_name', 'descendant_concept_code', 'descendant_concept_class_id', 'vocabulary_id', 'min_levels_of_separation', 'max_levels_of_separation']

    Returns
    -------
    results : inspectomop.results.Results

    Notes
    -----
    Original SQL

    G09: Find descendants for a given concept::

        SELECT
            C.concept_id as ancestor_concept_id,
            C.concept_name as ancestor_concept_name,
            C.concept_code as ancestor_concept_code,
            C.concept_class_id as ancestor_concept_class_id,
            C.vocabulary_id,
            VA.vocabulary_name,
            A.min_levels_of_separation,
            A.max_levels_of_separation
        FROM
            concept_ancestor A,
            concept C,
            vocabulary VA
        WHERE
            A.ancestor_concept_id = C.concept_id AND
            C.vocabulary_id = VA.vocabulary_id AND A.ancestor_concept_id<>A.descendant_concept_id AND A.descendant_concept_id = 192671 AND
            sysdate BETWEEN valid_start_date AND valid_end_date
        ORDER BY 5,7;
"""
    a = _alias(inspector.tables['concept_ancestor'],'a')
    c = _alias(inspector.tables['concept'],'c')
    va = _alias(inspector.tables['vocabulary'], 'va')

    columns = [c.c.concept_id.label('descendant_concept_id'), c.c.concept_name.label('descendant_concept_name'), c.c.concept_code.label('descendant_concept_code'), c.c.concept_class_id.label('descendant_concept_class_id'),\
               c.c.vocabulary_id, va.c.vocabulary_name, a.c.min_levels_of_separation, \
               a.c.max_levels_of_separation]
    if return_columns:
        columns = [col for col in columns if col.name in return_columns]
    statement = _select(columns).\
                where(_and_(\
                    a.c.descendant_concept_id == c.c.concept_id,\
                    c.c.vocabulary_id == va.c.vocabulary_id, \
                    a.c.ancestor_concept_id != a.c.descendant_concept_id, \
                    a.c.ancestor_concept_id == concept_id)). \
                    order_by(c.c.vocabulary_id, a.c.min_levels_of_separation)
    return inspector.execute(statement)

def parents_for_concept_id(concept_id, inspector,return_columns=None):
    """
    Find all descendant concepts for a concept_id.

    Parameters
    ----------
    concept_id : int
        concept_id of interest from the concept table
    inspector : inspectomop.inspector.Inspector
    return_columns : list of str, optional
        - optional subset of columns to return from the query
        - columns : ['parent_concept_id', 'parent_concept_name', 'parent_concept_code', 'parent_concept_class_id', 'parent_concept_vocabulary_id', 'parent_concept_vocab_name']

    Returns
    -------
    results : inspectomop.results.Results

    Notes
    -----
    Original SQL

    G10: Find parents for a given concept::

        SELECT
            A.concept_id Parent_concept_id,
            A.concept_name Parent_concept_name,
            A.concept_code Parent_concept_code,
            A.concept_class_id Parent_concept_class_id,
            A.vocabulary_id Parent_concept_vocab_ID,
            VA.vocabulary_name Parent_concept_vocab_name
        FROM
            concept_ancestor CA,
            concept A,
            concept D,
            vocabulary VA
        WHERE
            CA.descendant_concept_id = 192671 AND
            CA.min_levels_of_separation = 1 AND
            CA.ancestor_concept_id = A.concept_id AND
            A.vocabulary_id = VA.vocabulary_id AND
            CA.descendant_concept_id = D.concept_id AND
            sysdate BETWEEN A.valid_start_date AND A.valid_end_date;
"""
    ca = _alias(inspector.tables['concept_ancestor'],'ca')
    a = _alias(inspector.tables['concept'],'a')
    d = _alias(inspector.tables['concept'], 'd')
    va = _alias(inspector.tables['vocabulary'], 'va')
    levels_of_sep = 1

    columns = [a.c.concept_id.label('parent_concept_id'), a.c.concept_name.label('parent_concept_name'), a.c.concept_code.label('parent_concept_code'), a.c.concept_class_id.label('parent_concept_class_id'),\
               a.c.vocabulary_id.label('parent_concept_vocabulary_id'), va.c.vocabulary_name.label('parent_concept_vocab_name')]
    if return_columns:
        columns = [col for col in columns if col.name in return_columns]
    statement = _select(columns).\
                where(_and_(\
                    ca.c.descendant_concept_id == concept_id,\
                    ca.c.min_levels_of_separation == levels_of_sep, \
                    ca.c.ancestor_concept_id == a.c.concept_id,\
                    a.c.vocabulary_id == va.c.vocabulary_id,\
                    ca.c.descendant_concept_id == d.c.concept_id))

    return inspector.execute(statement)

def children_for_concept_id(concept_id, inspector,return_columns=None):
    """
    Find all child concepts for a concept_id.

    Parameters
    ----------
    concept_id : int
        concept_id of interest from the concept table
    inspector : inspectomop.inspector.Inspector
    return_columns : list of str, optional
        - optional subset of columns to return from the query
        - columns : ['child_concept_id','child_concept_name', 'child_concept_code', 'child_concept_class_id', 'child_concept_vocabulary_id', 'child_concept_vocab_name']

    Returns
    -------
    results : inspectomop.results.Results

    Notes
    -----
    Original SQL

    G11: Find children for a given concept::

        SELECT
            D.concept_id Child_concept_id,
            D.concept_name Child_concept_name,
            D.concept_code Child_concept_code,
            D.concept_class_id Child_concept_class_id,
            D.vocabulary_id Child_concept_vocab_ID,
            VS.vocabulary_name Child_concept_vocab_name
        FROM
            concept_ancestor CA,
            concept D,
            vocabulary VS
        WHERE
            CA.ancestor_concept_id = 192671 AND
            CA.min_levels_of_separation = 1 AND
            CA.descendant_concept_id = D.concept_id AND
            D.vocabulary_id = VS.vocabulary_id AND
            sysdate BETWEEN D.valid_start_date AND D.valid_end_date;
"""
    ca = _alias(inspector.tables['concept_ancestor'],'ca')
    d = _alias(inspector.tables['concept'], 'd')
    vs = _alias(inspector.tables['vocabulary'], 'vs')
    levels_of_sep = 1

    columns = [d.c.concept_id.label('child_concept_id'), d.c.concept_name.label('child_concept_name'), d.c.concept_code.label('child_concept_code'), d.c.concept_class_id.label('child_concept_class_id'),\
               d.c.vocabulary_id.label('child_concept_vocabulary_id'), vs.c.vocabulary_name.label('child_concept_vocab_name')]
    if return_columns:
        columns = [col for col in columns if col.name in return_columns]
    statement = _select(columns).\
                where(_and_(\
                    ca.c.ancestor_concept_id == concept_id,\
                    ca.c.min_levels_of_separation == levels_of_sep, \
                    ca.c.descendant_concept_id == d.c.concept_id,\
                    d.c.vocabulary_id == vs.c.vocabulary_id))

    return inspector.execute(statement)


def siblings_for_concept_id(concept_id, inspector,return_columns=None):
    """
    Find all sibling concepts for a concept_id i.e.(concepts that share common parents).
    This may or may not result in concepts that have a close clinical relationship, especially if
    the query concept_id is already high up in the hierarchy or has multiple parents that diverge in
    their meaning.

    Parameters
    ----------
    concept_id : int
        concept_id of interest from the concept table
    inspector : inspectomop.inspector.Inspector
    return_columns : list of str, optional
        - optional subset of columns to return from the query
        - columns : ['sibling_concept_id', 'sibling_concept_name','sibling_concept_code','sibling_concept_class_id',
            'sibling_concept_vocabulary_id,'parent_concept_id','parent_concept_name']

    Returns
    -------
    results : inspectomop.results.Results

    Notes
    -----
    SQL::

        SELECT
            s.concept_id AS sibling_concept_id,
            s.concept_name AS sibling_concept_name,
            a.concept_id AS parent_concept_id,
            a.concept_name AS parent_concept_name
        FROM
            main.concept AS s,
            main.concept AS a,
            main.concept_ancestor AS ca,
            main.vocabulary AS va,
            main.concept AS d,
            main.concept_ancestor AS ca2
        WHERE
            ca.descendant_concept_id = concept_id AND
            ca.min_levels_of_separation = 1 AND
            ca.ancestor_concept_id = a.concept_id AND
            a.vocabulary_id = va.vocabulary_id AND
            ca.descendant_concept_id = d.concept_id AND
            ca2.ancestor_concept_id = ca.ancestor_concept_id AND
            s.concept_id = ca2.descendant_concept_id
"""
    ca = _alias(inspector.tables['concept_ancestor'],'ca')
    ca2 = _alias(inspector.tables['concept_ancestor'], 'ca2')
    a = _alias(inspector.tables['concept'],'a')
    d = _alias(inspector.tables['concept'], 'd')
    s = _alias(inspector.tables['concept'], 's')
    va = _alias(inspector.tables['vocabulary'], 'va')
    levels_of_sep = 1

    columns = [s.c.concept_id.label('sibling_concept_id'), s.c.concept_name.label('sibling_concept_name'),\
        s.c.concept_code.label('sibling_concept_code'),s.c.concept_class_id.label('sibling_concept_class_id'),\
        s.c.vocabulary_id.label('sibling_concept_vocabulary_id'),a.c.concept_id.label('parent_concept_id'), a.c.concept_name.label('parent_concept_name')]
    if return_columns:
        columns = [col for col in columns if col.name in return_columns]
    statement = _select(columns).\
                where(_and_(\
                    ca.c.descendant_concept_id == concept_id,\
                    ca.c.min_levels_of_separation == levels_of_sep, \
                    ca.c.ancestor_concept_id == a.c.concept_id,\
                    a.c.vocabulary_id == va.c.vocabulary_id,\
                    ca.c.descendant_concept_id == d.c.concept_id,\
                    ca2.c.ancestor_concept_id == ca.c.ancestor_concept_id,\
                    s.c.concept_id == ca2.c.descendant_concept_id)
                    )
    return inspector.execute(statement)
