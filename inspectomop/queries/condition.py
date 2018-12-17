# Condition related OMOP data queries.
# Adapted from: https://github.com/OHDSI/OMOP-Queries

from sqlalchemy import select as _select, join as _join,\
    union as _union, union_all as _union_all, \
    distinct as _distinct, between as  _between, alias as _alias, \
    and_ as _and_, or_ as _or_, literal_column as _literal_column, func as _func

def condition_concept_for_concept_id(concept_id, inspector,return_columns=None):
    """
    Retrieves the condition concept for a condition_concept_id.

    Parameters
    ----------
    concept_id : int
    inspector : inspectomop.inspector.Inspector
    return_columns : list of str, optional
        - optional subset of columns to return from the query
        - columns : ['concept_id', 'concept_name', 'concept_code', 'concept_class_id', 'vocabulary_id', 'vocabulary_name']

    Returns
    -------
    results : inspectomop.results.Results
        a cursor-like object with methods such as fetchone(), fetchmany() etc.

    See Also
    --------
    inspectomop.queries.general.concepts_for_concept_ids

    Notes
    -----
    Original SQL

    C01: Find condition by concept ID::

        SELECT
            C.concept_id Condition_concept_id,
            C.concept_name Condition_concept_name,
            C.concept_code Condition_concept_code,
            C.concept_class_id Condition_concept_class,
            C.vocabulary_id Condition_concept_vocab_ID,
            V.vocabulary_name Condition_concept_vocab_name,
            CASE C.vocabulary_id
                WHEN 'SNOMED' THEN CASE lower(C.concept_class_id)
                WHEN 'clinical finding' THEN 'Yes' ELSE 'No' END
                WHEN 'MedDRA' THEN 'Yes'
                ELSE 'No'
            END Is_Disease_Concept_flag
        FROM
            concept C,
            vocabulary V
        WHERE
            C.concept_id = 192671 AND
            C.vocabulary_id = V.vocabulary_id AND
            sysdate BETWEEN valid_start_date AND valid_end_date;
    """
    c = _alias(inspector.tables['concept'], 'c')
    v = _alias(inspector.tables['vocabulary'], 'v')
    domain_id = 'Condition'
    standard_concept = 'S'
    columns = [c.c.concept_id, c.c.concept_name, c.c.concept_code, c.c.concept_class_id,\
        c.c.vocabulary_id, v.c.vocabulary_name]
    if return_columns:
        columns = [col for col in columns if col.name in return_columns]
    statement = _select(columns)\
                .where(_and_(\
                    c.c.concept_id == concept_id,\
                    c.c.vocabulary_id == v.c.vocabulary_id,\
                    c.c.domain_id == domain_id,\
                    c.c.standard_concept == standard_concept))
    return inspector.execute(statement)


def condition_concepts_for_keyword(keyword, inspector, return_columns=None):
    """
    Retrieves standard concepts for a condition/keyword.

    Parameters
    ----------
    keyword : str
    inspector : inspectomop.inspector.Inspector
    return_columns : list of str, optional
        - optional subset of columns to return from the query
        - columns : ['concept_id', 'concept_name', 'concept_code', 'concept_class_id', 'vocabulary_id']

    Returns
    -------
    results : inspectomop.results.Results
        a cursor-like object with methods such as fetchone(), fetchmany() etc.

    Notes
    -----
    Original SQL

    C02: Find a condition by keyword::

        SELECT
            T.Entity_Concept_Id,
            T.Entity_Name,
            T.Entity_Code,
            T.Entity_Type,
            T.Entity_concept_class,
            T.Entity_vocabulary_id,
            T.Entity_vocabulary_name
        FROM (
            SELECT
                C.concept_id Entity_Concept_Id,
                C.concept_name Entity_Name,
                C.CONCEPT_CODE Entity_Code,
                'Concept' Entity_Type,
                C.concept_class_id Entity_concept_class,
                C.vocabulary_id Entity_vocabulary_id,
                V.vocabulary_name Entity_vocabulary_name,
                NULL Entity_Mapping_Type,
                C.valid_start_date,
                C.valid_end_date
            FROM concept C
            JOIN vocabulary V ON C.vocabulary_id = V.vocabulary_id
            LEFT JOIN concept_synonym S ON C.concept_id = S.concept_id
                WHERE
                    (C.vocabulary_id IN ('SNOMED', 'MedDRA') OR LOWER(C.concept_class_id) = 'clinical finding' ) AND
                    C.concept_class_id IS NOT NULL AND
                    ( LOWER(C.concept_name) like '%myocardial infarction%' OR
                    LOWER(S.concept_synonym_name) like '%myocardial infarction%' )
            ) T
        WHERE sysdate BETWEEN valid_start_date AND valid_end_date
        ORDER BY 6,2;
    """
    c = inspector.tables['concept']
    cs = inspector.tables['concept_synonym']
    v = inspector.tables['vocabulary']

    vocab_ids = ['SNOMED', 'MedDRA']
    concept_class_id = 'clinical_finding'
    columns = [c.concept_id, c.concept_name, c.concept_code,c.concept_class_id,v.vocabulary_id]
    j = _join(c, v, c.vocabulary_id == v.vocabulary_id)
    j2 = _join(j, cs, c.concept_id == cs.concept_id, isouter=True)
    if return_columns:
        columns = [col for col in columns if col.name in return_columns]
    statement = _select(columns)\
                .select_from(j2)\
                .where(_and_(\
                _or_(c.vocabulary_id.in_(vocab_ids), _func.lower(c.concept_class_id)==concept_class_id),\
                c.concept_class_id != None,\
                _or_(_func.lower(c.concept_name).ilike('%{}%'.format(keyword.lower())),\
                    _func.lower(cs.concept_synonym_name).ilike('%{}%'.format(keyword.lower())))))\
                .distinct()
    return inspector.execute(statement)

def condition_concepts_for_source_codes(source_codes, inspector,return_columns=None):
    """
    Retrieves standard condition concepts for source codes.  Ex ICD-9-CM --> SNOMED-CT

    Parameters
    ----------
    source_codes : list of str
        a list of source code strings.  Ex ICD-9-CM ['250.00','250.01']
    inspector : inspectomop.inspector.Inspector
    return_columns : list of str, optional
        - optional subset of columns to return from the query
        - columns : ['source_code', 'source_concept_name',\
                'source_vocab_id', 'source_vocab_name',\
                'source_domain_id','target_concept_id',\
                'target_concept_name', 'target_concept_code',\
                'target_concept_class_id','target_vocab_id', \
                'target_vocab_name']

    Returns
    -------
    results : inspectomop.results.Results
        a cursor-like object with methods such as fetchone(), fetchmany() etc.

    Notes
    -----
    Original SQL

    C05: Translate a source code to condition concepts::

        set search_path to full_201612_omop_v5;
        SELECT DISTINCT
            c1.concept_code,
            c1.concept_name,
            c1.vocabulary_id source_vocabulary_id,
            VS.vocabulary_name source_vocabulary_description,
            C1.domain_id,
            C2.concept_id target_concept_id,
            C2.concept_name target_Concept_Name,
            C2.concept_code target_Concept_Code,
            C2.concept_class_id target_Concept_Class,
            C2.vocabulary_id target_Concept_Vocab_ID,
            VT.vocabulary_name target_Concept_Vocab_Name
        FROM
            concept_relationship cr,
            concept c1,
            concept c2,
            vocabulary VS,
            vocabulary VT
        WHERE
            cr.concept_id_1 = c1.concept_id AND
            cr.relationship_id = 'Maps to' AND
            cr.concept_id_2 = c2.concept_id AND
            c1.vocabulary_id = VS.vocabulary_id AND
            c1.domain_id = 'Condition' AND
            c2.vocabulary_id = VT.vocabulary_id AND
            c1.concept_code IN ('070.0') AND
            c2.vocabulary_id ='SNOMED' AND
            sysdate BETWEEN c1.valid_start_date AND c1.valid_end_date;
    """
    c1 = _alias(inspector.tables['concept'],'c1')
    c2 = _alias(inspector.tables['concept'], 'c2')
    cr = _alias(inspector.tables['concept_relationship'], 'cr')
    vs = _alias(inspector.tables['vocabulary'], 'vs')
    vt = _alias(inspector.tables['vocabulary'], 'vt')

    vocab_id = 'SNOMED'
    domain_id = 'Condition'
    relationship_id = 'Maps to'

    columns = [c1.c.concept_code.label('source_code'), c1.c.concept_name.label('source_concept_name'),\
            c1.c.vocabulary_id.label('source_vocab_id'), vs.c.vocabulary_name.label('source_vocab_name'),\
            c1.c.domain_id.label('source_domain_id'),c2.c.concept_id.label('target_concept_id'),\
            c2.c.concept_name.label('target_concept_name'), c2.c.concept_code.label('target_concept_code'),\
            c2.c.concept_class_id.label('target_concept_class_id'), c2.c.vocabulary_id.label('target_vocab_id'), \
            vt.c.vocabulary_name.label('target_vocab_name')]

    if return_columns:
        columns = [col for col in columns if col.name in return_columns]

    statement = _select(columns)\
                .where(_and_(\
                    cr.c.concept_id_1 == c1.c.concept_id,\
                    cr.c.relationship_id == relationship_id,\
                    cr.c.concept_id_2 == c2.c.concept_id,\
                    c1.c.vocabulary_id == vs.c.vocabulary_id,\
                    c1.c.domain_id == domain_id,\
                    c2.c.vocabulary_id == vt.c.vocabulary_id,\
                    c1.c.concept_code.in_(source_codes),\
                    c2.c.vocabulary_id == vocab_id))\
                .distinct()
    return inspector.execute(statement)

def source_codes_for_concept_ids(concept_ids, inspector,return_columns=None):
    """
    Retreives source condition concepts for OMOP concept_ids.  i.e SNOMED-CT --> ICD-9-CM, ICD-10-CM

    Parameters
    ----------
    source_code : list of int
        integer list of concept_ids to translate
    inspector : inspectomop.inspector.Inspector
    return_columns : list of str, optional
        - optional subset of columns to return from the query
        - columns : ['concept_id','concept_code', 'concept_name',\
                'vocab_id', 'vocab_name',\
                'domain_id','source_concept_id',\
                'source_concept_name', 'source_concept_code',\
                'source_concept_class_id','source_vocab_id', \
                'source_vocab_name']

    Returns
    -------
    results : inspectomop.results.Results
        a cursor-like object with methods such as fetchone(), fetchmany() etc.

    Notes
    -----
    Original SQL

    C06: Translate a given condition to source codes::

        set search_path to full_201612_omop_v5;
        SELECT DISTINCT
            c1.concept_code,
            c1.concept_name,
            c1.vocabulary_id source_vocabulary_id,
            VS.vocabulary_name source_vocabulary_description,
            C1.domain_id,
            C2.concept_id target_concept_id,
            C2.concept_name target_Concept_Name,
            C2.concept_code target_Concept_Code,
            C2.concept_class_id target_Concept_Class,
            C2.vocabulary_id target_Concept_Vocab_ID,
            VT.vocabulary_name target_Concept_Vocab_Name
        FROM
            concept_relationship cr,
            concept c1,
            concept c2,
            vocabulary VS,
            vocabulary VT
        WHERE
            cr.concept_id_1 = c1.concept_id AND
            cr.relationship_id = 'Maps to' AND
            cr.concept_id_2 = c2.concept_id AND
            c1.vocabulary_id = VS.vocabulary_id AND
            c1.domain_id = 'Condition' AND
            c2.vocabulary_id = VT.vocabulary_id AND
            c1.concept_id = 312327 AND
            c1.vocabulary_id = 'SNOMED' AND
            sysdate BETWEEN c2.valid_start_date AND c2.valid_end_date;
    """
    c1 = _alias(inspector.tables['concept'],'c1')
    c2 = _alias(inspector.tables['concept'], 'c2')
    cr = _alias(inspector.tables['concept_relationship'], 'cr')
    vs = _alias(inspector.tables['vocabulary'], 'vs')
    vt = _alias(inspector.tables['vocabulary'], 'vt')

    vocab_id = 'SNOMED'
    domain_id = 'Condition'
    relationship_id = 'Maps to'

    columns = [c1.c.concept_id.label('concept_id'), c1.c.concept_code.label('concept_code'), c1.c.concept_name.label('concept_name'),\
            c1.c.vocabulary_id.label('vocab_id'), vs.c.vocabulary_name.label('vocab_name'),\
            c1.c.domain_id.label('domain_id'),c2.c.concept_id.label('source_concept_id'),\
            c2.c.concept_name.label('source_concept_name'), c2.c.concept_code.label('source_concept_code'),\
            c2.c.concept_class_id.label('source_concept_class_id'), c2.c.vocabulary_id.label('source_vocab_id'), \
            vt.c.vocabulary_name.label('source_vocab_name')]

    if return_columns:
        columns = [col for col in columns if col.name in return_columns]

    statement = _select(columns)\
                .where(_and_(\
                    cr.c.concept_id_1 == c1.c.concept_id,\
                    cr.c.relationship_id == relationship_id,\
                    cr.c.concept_id_2 == c2.c.concept_id,\
                    c1.c.vocabulary_id == vs.c.vocabulary_id,\
                    c1.c.domain_id == domain_id,\
                    c2.c.vocabulary_id == vt.c.vocabulary_id,\
                    c1.c.concept_id.in_(concept_ids),\
                    c2.c.vocabulary_id == vocab_id))\
                .distinct()
    return inspector.execute(statement)

def pathogen_concept_for_keyword(keyword, inspector,return_columns=None):
    """
    Retrieves pathogen concepts based on a keyword with 'Organsim' as the concept_class_id.

    Parameters
    ----------
    keyword : str
        search string.  ex 'Helicobacter Pylori'
    inspector : inspectomop.inspector.Inspector
    return_columns : list of str, optional
        - optional subset of columns to return from the query
        - columns : ['concept_id', 'concept_name', 'concept_code',\
                'concept_class_id', 'standard_concept', 'vocabulary_id', 'vocabulary_name']

    Returns
    -------
    results : inspectomop.results.Results
        a cursor-like object with methods such as fetchone(), fetchmany() etc.

    See Also
    --------
    disease_causing_agents_for_keyword, conditions_caused_by_pathogen_or_causative_agent_concept_id

    Notes
    -----
    Original SQL

    C07: Find a pathogen by keyword::

        SELECT
            C.concept_id Pathogen_Concept_ID,
            C.concept_name Pathogen_Concept_Name,
            C.concept_code Pathogen_concept_code,
            C.concept_class_id Pathogen_concept_class,
            C.standard_concept Pathogen_Standard_Concept,
            C.vocabulary_id Pathogen_Concept_Vocab_ID,
            V.vocabulary_name Pathogen_Concept_Vocab_Name
        FROM
            concept C,
            vocabulary V
        WHERE
            LOWER(C.concept_class_id) = 'organism' AND
            LOWER(C.concept_name) like '%trypanosoma%' AND
            C.vocabulary_id = V.vocabulary_id AND
            sysdate BETWEEN C.valid_start_date AND C.valid_end_date;
    """
    c = _alias(inspector.tables['concept'],'c')
    v = _alias(inspector.tables['vocabulary'], 'v')

    vocab_id = 'SNOMED'
    concept_class_id = 'Organism'

    columns = [c.c.concept_id,c.c.concept_name, c.c.concept_code,\
            c.c.concept_class_id, c.c.standard_concept, c.c.vocabulary_id, v.c.vocabulary_name]
    if return_columns:
        columns = [col for col in columns if col.name in return_columns]
    statement = _select(columns)\
                .where(_and_(\
                    c.c.concept_class_id == concept_class_id,\
                    _func.lower(c.c.concept_name).ilike('%{}%'.format(keyword.lower())),\
                    c.c.vocabulary_id == v.c.vocabulary_id))
    return inspector.execute(statement)

def disease_causing_agents_for_keyword(keyword, inspector,return_columns=None):
    """
    Retrieves disease causing agents by keyword.  The concept_class_id can be any of: 'Pharmaceutical / biologic product',\
    'Physical object', 'Special concept', 'Event', 'Physical force', or 'Substance'.

    Results of queries from `disease_causing_agents_for_keyword()` and `pathogen_concept_for_keyword()`\
    can be used to search for conditions caused by the offending pathogens/agents using \
    `conditions_caused_by_pathogen_or_causative_agent_concept_id()`

    Parameters
    ----------
    keyword : str
        search string.  ex 'Radiation'
    inspector : inspectomop.inspector.Inspector
    return_columns : list of str, optional
        - optional subset of columns to return from the query
        - columns : ['concept_id', 'concept_name', 'concept_code',\
                'concept_class_id', 'standard_concept', 'vocabulary_id', 'vocabulary_name']

    Returns
    -------
    results : inspectomop.results.Results
        a cursor-like object with methods such as fetchone(), fetchmany() etc.

    See Also
    --------
    pathogen_concept_for_keyword, conditions_caused_by_pathogen_or_causative_agent_concept_id

    Notes
    -----
    Original SQL

    C08: Find a disease causing agent by keyword::

        SELECT
            C.concept_id Agent_Concept_ID,
            C.concept_name Agent_Concept_Name,
            C.concept_code Agent_concept_code,
            C.concept_class_id Agent_concept_class,
            C.standard_concept Agent_Standard_Concept,
            C.vocabulary_id Agent_Concept_Vocab_ID,
            V.vocabulary_name Agent_Concept_Vocab_Name
        FROM
            concept C,
            vocabulary V
        WHERE
            LOWER(C.concept_class_id) in ('pharmaceutical / biologic product','physical object','special concept','event', 'physical force','substance') AND
            LOWER(C.concept_name) like '%radiation%' AND
            C.vocabulary_id = V.vocabulary_id AND
        sysdate BETWEEN C.valid_start_date AND C.valid_end_date;
    """
    c = _alias(inspector.tables['concept'],'c')
    v = _alias(inspector.tables['vocabulary'], 'v')

    concept_class_ids = ['pharmaceutical / biologic product','physical object',
                                'special concept','event', 'physical force','substance']

    columns = [c.c.concept_id,c.c.concept_name, c.c.concept_code,\
            c.c.concept_class_id, c.c.standard_concept, c.c.vocabulary_id, v.c.vocabulary_name]
    if return_columns:
        columns = [col for col in columns if col.name in return_columns]
    statement = _select(columns)\
                .where(_and_(\
                    _func.lower(c.c.concept_class_id).in_(concept_class_ids),\
                    _func.lower(c.c.concept_name).ilike('%{}%'.format(keyword.lower())),\
                    c.c.vocabulary_id == v.c.vocabulary_id))
    return inspector.execute(statement)

def conditions_caused_by_pathogen_or_causative_agent_concept_id(concept_id, inspector,return_columns=None):
    """
    Retreives all conditions caused by a pathogen or other causative agent concept_id.

    Parameters
    ----------
    concept_id : int
    inspector : inspectomop.inspector.Inspector
    return_columns : list of str, optional
        - optional subset of columns to return from the query
        - columns : ['condition_concept_id', 'condition_name',\
                    'condition_concept_code', 'condition_concept_class_id',\
                    'condition_vocab_id', 'condition_vocab_name',\
                    'causative_agent_concept_id', 'causative_agent_concept_name',\
                    'causative_agent_concept_code', 'causative_agent_concept_class_id',\
                    'causative_agent_vocab_id', 'causative_agent_vocab_name']

    Returns
    -------
    results : inspectomop.results.Results
        a cursor-like object with methods such as fetchone(), fetchmany() etc.

    See Also
    --------
    disease_causing_agents_for_keyword, pathogen_concept_for_keyword

    Notes
    -----
    Original SQL

    C09: Find all SNOMED-CT condition concepts that can be caused by a given pathogen or causative agent::

        SELECT
            A.concept_Id Condition_ID,
            A.concept_Name Condition_name,
            A.concept_Code Condition_code,
            A.concept_Class_id Condition_class,
            A.vocabulary_id Condition_vocab_ID,
            VA.vocabulary_name Condition_vocab_name,
            D.concept_Id Causative_agent_ID,
            D.concept_Name Causative_agent_Name,
            D.concept_Code Causative_agent_Code,
            D.concept_Class_id Causative_agent_Class,
            D.vocabulary_id Causative_agent_vocab_ID,
            VS.vocabulary_name Causative_agent_vocab_name
        FROM
            concept_relationship CR,
            concept A,
            concept D,
            vocabulary VA,
            vocabulary VS
        WHERE
            CR.relationship_ID = 'Has causative agent' AND
            CR.concept_id_1 = A.concept_id AND
            A.vocabulary_id = VA.vocabulary_id AND
            CR.concept_id_2 = D.concept_id AND
            D.concept_id = 4248851 AND
            D.vocabulary_id = VS.vocabulary_id AND
            sysdate BETWEEN CR.valid_start_date AND CR.valid_end_date;
    """
    a = _alias(inspector.tables['concept'],'a')
    d = _alias(inspector.tables['concept'], 'd')
    cr = _alias(inspector.tables['concept_relationship'], 'cr')
    va = _alias(inspector.tables['vocabulary'], 'va')
    vs = _alias(inspector.tables['vocabulary'], 'vs')

    relationship_id = 'Has causative agent'


    columns = [a.c.concept_id.label('condition_concept_id'), a.c.concept_name.label('condition_name'),\
                a.c.concept_code.label('condition_concept_code'), a.c.concept_class_id.label('condition_concept_class_id'),\
                a.c.vocabulary_id.label('condition_vocab_id'), va.c.vocabulary_name.label('condition_vocab_name'),\
                d.c.concept_id.label('causative_agent_concept_id'), d.c.concept_name.label('causative_agent_concept_name'),\
                d.c.concept_code.label('causative_agent_concept_code'), d.c.concept_class_id.label('causative_agent_concept_class_id'),\
                d.c.vocabulary_id.label('causative_agent_vocab_id'), vs.c.vocabulary_name.label('causative_agent_vocab_name')]

    if return_columns:
        columns = [col for col in columns if col.name in return_columns]
    statement = _select(columns)\
                .where(_and_(\
                    cr.c.relationship_id == relationship_id,\
                    cr.c.concept_id_1 == a.c.concept_id,\
                    a.c.vocabulary_id == va.c.vocabulary_id,\
                    cr.c.concept_id_2 == d.c.concept_id,\
                    d.c.concept_id == concept_id,\
                    d.c.vocabulary_id == vs.c.vocabulary_id))
    return inspector.execute(statement)

def anatomical_site_by_keyword(keyword, inspector,return_columns=None):
    """
    Retrieves anitomical site concepts given a keyword.  Results of this query are useful for `condition_concepts_occurring_at_anatomical_site_concept_id`

    Parameters
    ----------
    keyword : str
        search string.  ex 'Epiglottis'
    inspector : inspectomop.inspector.Inspector
    return_columns : list of str, optional
        - optional subset of columns to return from the query
        - columns : ['concept_id', 'concept_name', 'concept_code', 'concept_class_id', 'standard_concept', 'vocabulary_id', 'vocabulary_name']

    Returns
    -------
    results : inspectomop.results.Results
        a cursor-like object with methods such as fetchone(), fetchmany() etc.

    See Also
    --------
    condition_concepts_occurring_at_anatomical_site_concept_id

    Notes
    -----
    Original SQL

    C10: Find an anatomical site by keyword::

        SELECT
            C.concept_id Anatomical_site_ID,
            C.concept_name Anatomical_site_Name,
            C.concept_code Anatomical_site_Code,
            C.concept_class_id Anatomical_site_Class,
            C.standard_concept Anatomical_standard_concept,
            C.vocabulary_id Anatomical_site_Vocab_ID,
            V.vocabulary_name Anatomical_site_Vocab_Name
        FROM
            concept C,
            vocabulary V
        WHERE
            LOWER(C.concept_class_id) = 'body structure' AND
            LOWER(C.concept_name) like '%epiglottis%' AND
            C.vocabulary_id = V.vocabulary_id AND
            sysdate BETWEEN C.valid_start_date AND C.valid_end_date;
    """
    c = _alias(inspector.tables['concept'],'c')
    v = _alias(inspector.tables['vocabulary'], 'v')

    concept_class_id = 'Body Structure'

    columns = [c.c.concept_id, c.c.concept_name, c.c.concept_code, c.c.concept_class_id,\
                c.c.standard_concept, c.c.vocabulary_id, v.c.vocabulary_name]
    if return_columns:
        columns = [col for col in columns if col.name in return_columns]
    statement = _select(columns)\
                .where(_and_(\
                    c.c.concept_class_id == concept_class_id,\
                    _func.lower(c.c.concept_name).ilike('%{}%'.format(keyword.lower())),\
                    c.c.vocabulary_id == v.c.vocabulary_id))
    return inspector.execute(statement)

def condition_concepts_occurring_at_anatomical_site_concept_id(concept_id, inspector,return_columns=None):
    """
    Retrieves condition concepts that occur at a given anatomical site.  Input concept_id should be a concept of
    class 'Body Structure'

    Parameters
    ----------
    concept_id : int
    inspector : inspectomop.inspector.Inspector
    return_columns : list of str, optional
        - optional subset of columns to return from the query
        - columns : ['cond_concept_id', 'cond_concept_name',\
                    'cond_concept_code', 'cond_concept_class_id',\
                    'cond_vocab_id', 'cond_vocab_name',\
                    'anat_site_concept_id','anat_site_concept_name',\
                    'anat_site_concept_code', 'anat_site_concept_class_id',\
                    'anat_site_vocab_id', 'anat_site_vocab_name']

    Returns
    -------
    results : inspectomop.results.Results
        a cursor-like object with methods such as fetchone(), fetchmany() etc.

    See Also
    --------
    anatomical_site_by_keyword

    Notes
    -----
    Original SQL

    C11: Find all SNOMED-CT condition concepts that are occurring at an anatomical site::

        SELECT
            A.concept_Id Condition_ID,
            A.concept_Name Condition_name,
            A.concept_Code Condition_code,
            A.concept_Class_id Condition_class,
            A.vocabulary_id Condition_vocab_ID,
            VA.vocabulary_name Condition_vocab_name,
            D.concept_Id Anatomical_site_ID,
            D.concept_Name Anatomical_site_Name,
            D.concept_Code Anatomical_site_Code,
            D.concept_Class_id Anatomical_site_Class,
            D.vocabulary_id Anatomical_site_vocab_ID,
            VS.vocabulary_name Anatomical_site_vocab_name
        FROM
            concept_relationship CR,
            concept A,
            concept D,
            vocabulary VA,
            vocabulary VS
        WHERE
            CR.relationship_ID = 'Has finding site' AND
            CR.concept_id_1 = A.concept_id AND
            A.vocabulary_id = VA.vocabulary_id AND
            CR.concept_id_2 = D.concept_id AND
            D.concept_id = 4103720 --input AND
            D.vocabulary_id = VS.vocabulary_id AND
            sysdate BETWEEN CR.valid_start_date AND CR.valid_end_date;
    """
    a = _alias(inspector.tables['concept'],'a')
    d = _alias(inspector.tables['concept'],'d')
    cr = _alias(inspector.tables['concept_relationship'], 'cr')
    va = _alias(inspector.tables['vocabulary'], 'va')
    vs = _alias(inspector.tables['vocabulary'], 'vs')

    relationship_id = 'Has finding site'

    columns = [a.c.concept_id.label('cond_concept_id'), a.c.concept_name.label('cond_concept_name'),\
                a.c.concept_code.label('cond_concept_code'), a.c.concept_class_id.label('cond_concept_class_id'),\
                a.c.vocabulary_id.label('cond_vocab_id'), va.c.vocabulary_name.label('cond_vocab_name'),\
                d.c.concept_id.label('anat_site_concept_id'),d.c.concept_name.label('anat_site_concept_name'),\
                d.c.concept_code.label('anat_site_concept_code'), d.c.concept_class_id.label('anat_site_concept_class_id'),\
                d.c.vocabulary_id.label('anat_site_vocab_id'), vs.c.vocabulary_name.label('anat_site_vocab_name')]

    if return_columns:
        columns = [col for col in columns if col.name in return_columns]
    statement = _select(columns)\
                .where(_and_(\
                    cr.c.relationship_id == relationship_id,\
                    cr.c.concept_id_1 == a.c.concept_id,\
                    a.c.vocabulary_id == va.c.vocabulary_id,\
                    cr.c.concept_id_2 == d.c.concept_id,\
                    d.c.concept_id == concept_id,\
                    d.c.vocabulary_id == vs.c.vocabulary_id))
    return inspector.execute(statement)



def place_of_service_counts_for_condition_concept_id(condition_concept_id, inspector,return_columns=None):
    """
    Provides counts of conditions stratified by place_of_service (Office, Inpatient Hospital, etc.)

    Parameters
    ----------
    condition_concept_id : int
        concept_id from the conditions table
    inspector : inspectomop.inspector.Inspector
    return_columns : list of str, optional
        - optional subset of columns to return from the query
        - columns : ['condition_concept_id', 'condition_concept_id,'place_of_service_concept_id', 'place_of_service', 'place_freq']

    Returns
    -------
    results : inspectomop.results.Results
        a cursor-like object with methods such as fetchone(), fetchmany() etc.

    Notes
    -----
    SQL Modified from:

    CO04: Count In what place of service where condition diagnoses::

        SELECT
            c.concept_id AS condition_concept_id,
            c.concept_name AS condition_concept_id,
            cs.place_of_service_concept_id AS place_of_service_concept_id,
            c_place.concept_name AS place_of_service,
            count(cs.place_of_service_concept_id) AS place_freq
        FROM
            main.concept AS c, main.concept AS c_place,
            (SELECT
                co.condition_concept_id AS condition_concept_id,
                co.visit_occurrence_id AS s1_visit_id
            FROM
                main.condition_occurrence AS co
            WHERE
                co.condition_concept_id = :condition_concept_id_1
                AND co.visit_occurrence_id IS NOT NULL)
        JOIN
            main.visit_occurrence AS vo
        ON
            s1_visit_id = vo.visit_occurrence_id
        JOIN
            main.care_site AS cs
        ON
            vo.care_site_id = cs.care_site_id
        WHERE
            c_place.concept_id = cs.place_of_service_concept_id
            AND c.concept_id = :concept_id_1
        GROUP BY c.concept_name
    """
    co = _alias(inspector.tables['condition_occurrence'], 'co')
    cs = _alias(inspector.tables['care_site'],'cs')
    vo = _alias(inspector.tables['visit_occurrence'], 'vo')
    c_place = _alias(inspector.tables['concept'], 'c_place')
    c = _alias(inspector.tables['concept'], 'c')

    s1 = _select([co.c.condition_concept_id, co.c.visit_occurrence_id.label('s1_visit_id')]).where(_and_(co.c.condition_concept_id == condition_concept_id, co.c.visit_occurrence_id != None))
    j1 = _join(s1, vo, s1.c.s1_visit_id == vo.c.visit_occurrence_id)
    j2 = _join(j1, cs, j1.c.vo_care_site_id == cs.c.care_site_id)


    columns = [c.c.concept_id.label('condition_concept_id'), c.c.concept_name.label('condition_concept_id'),j2.c.cs_place_of_service_concept_id.label('place_of_service_concept_id'),c_place.c.concept_name.label('place_of_service'), _func.count(j2.c.cs_place_of_service_concept_id).label('place_freq')]

    if return_columns:
        columns = [col for col in columns if col.name in return_columns]

    statement = _select(columns).\
         select_from(j2).\
         where(_and_(c_place.c.concept_id == j2.c.cs_place_of_service_concept_id, c.c.concept_id == condition_concept_id)).group_by(c.c.concept_name)

    return inspector.execute(statement)
