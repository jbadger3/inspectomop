"""
Person related OMOP data queries.

Adapted from: https://github.com/OHDSI/OMOP-Queries
"""

from sqlalchemy import select as _select, join as _join,\
    union as _union, union_all as _union_all, \
    distinct as _distinct, between as  _between, alias as _alias, \
    and_ as _and_, or_ as _or_, literal_column as _literal_column, func as _func

def patient_counts_by_gender(inspector, person_ids=None, return_columns=None):
    """
    Returns patient counts grouped by gender for the database or alternativily, for a supplied list of person_ids.

    Parameters
    ----------
    person_ids : list of int, optional
        list of person_ids [int].  If None (default), get the gender distribution for all individuals in the person table
    inspector : inspectomop.inspector.Inspector
    return_columns : list of str, optional
        - optional subset of columns to return from the query
        - columns : ['gender_concept_id','gender','count']

    Returns
    -------
    results : inspectomop.results.Results

    Notes
    -----
    Original SQL

    PE03: Number of patients grouped by gender::

        SELECT
            person.GENDER_CONCEPT_ID,
            concept.CONCEPT_NAME AS gender_name,
            COUNT(person.person_ID) AS num_persons_count
        FROM
            person
        INNER JOIN
            concept ON person.GENDER_CONCEPT_ID = concept.CONCEPT_ID
        GROUP BY
            person.GENDER_CONCEPT_ID, concept.CONCEPT_NAME;
    """
    c = _alias(inspector.tables['concept'], 'c')
    p = _alias(inspector.tables['person'], 'p')
    columns = [p.c.gender_concept_id,c.c.concept_name.label('gender'),_func.count(p.c.gender_concept_id).label('count')]
    if return_columns:
        columns = [col for col in columns if col.name in return_columns]
    if not person_ids:
        statement = _select(columns).\
                    where(p.c.gender_concept_id == c.c.concept_id).\
                    group_by(p.c.gender_concept_id)
    else:
        statement = _select(columns).\
                    where(_and_(\
                        p.c.gender_concept_id == c.c.concept_id,\
                        p.c.person_id.in_(person_ids))).\
                    group_by(p.c.gender_concept_id)

    return inspector.execute(statement)

def patient_counts_by_year_of_birth(inspector, person_ids=None, return_columns=None):
    """
    Returns patient counts grouped by year of birth for the database or alternativily, for a supplied list of person_ids.

    Parameters
    ----------
    person_ids : list of int, optional
        list of person_ids [int].  If None (default), get the gender distribution for all individuals in the person table
    inspector : inspectomop.inspector.Inspector
    return_columns : list of str, optional
        - optional subset of columns to return from the query
        - columns : ['year_of_birth', 'count']

    Returns
    -------
    results : inspectomop.results.Results


    Notes
    -----
    Original SQL

    PE06: Number of patients grouped by year of birth::

        SELECT
            year_of_birth,
            COUNT(person_id) AS Num_Persons_count
        FROM
            person
        GROUP BY
            year_of_birth
        ORDER BY
            year_of_birth;
    """
    p = _alias(inspector.tables['person'], 'p')
    columns = [p.c.year_of_birth,_func.count(p.c.year_of_birth).label('count')]
    if return_columns:
        columns = [col for col in columns if col.name in return_columns]
    if not person_ids:
        statement = _select(columns).\
                    group_by(p.c.year_of_birth).\
                    order_by(p.c.year_of_birth)
    else:
        statement = _select(columns).\
                    where(\
                        p.c.person_id.in_(person_ids)).\
                    group_by(p.c.year_of_birth).\
                    order_by(p.c.year_of_birth)
    return inspector.execute(statement)

def patient_counts_by_residence_state(inspector, person_ids=None, return_columns=None):
    """
    Returns patient counts grouped by state for the database or alternativily, for a supplied list of person_ids.

    Parameters
    ----------
    person_ids : list of int, optional
        list of person_ids [int].  If None (default), get the gender distribution for all individuals in the person table
    inspector : inspectomop.inspector.Inspector
    return_columns : list of str, optional
        - optional subset of columns to return from the query
        - columns : ['state', 'count']

    Returns
    -------
    results : inspectomop.results.Results

    Notes
    -----
    Original SQL

    PE07: Number of patients grouped by residence state location::

        SELECT
            NVL( state, 'XX' ) AS state_abbr,
            count(\*) as Num_Persons_count
        FROM
            person
        LEFT OUTER JOIN
            location USING( location_id )
        GROUP BY
            NVL( state, 'XX' )
        ORDER BY 1;
    """
    p = _alias(inspector.tables['person'], 'p')
    l = _alias(inspector.tables['location'], 'l')
    j = _join(p, l, p.c.location_id == l.c.location_id)
    columns = [j.c.l_state,_func.count(j.c.l_state).label('count')]
    if return_columns:
        columns = [col for col in columns if col.name in return_columns]
    if not person_ids:
        statement = _select(columns).\
                    select_from(j).\
                    group_by(j.c.l_state).\
                    order_by(j.c.l_state)
    else:
        statement = _select(columns).\
                    select_from(j).\
                    where(\
                        j.c.p_person_id.in_(person_ids)).\
                    group_by(j.c.l_state).\
                    order_by(j.c.l_state)
    return inspector.execute(statement)

def patient_counts_by_zip_code(inspector, person_ids=None, return_columns=None):
    """
    Returns patient counts grouped by zip code for the database or alternativily, for a supplied list of person_ids.

    Parameters
    ----------
    person_ids : list of int, optional
        list of person_ids [int].  If None (default), get the gender distribution for all individuals in the person table
    inspector : inspectomop.inspector.Inspector
    return_columns : list of str, optional
        - optional subset of columns to return from the query
        - columns : ['state','zip_code', 'count']

    Returns
    -------
    results : inspectomop.results.Results

    Notes
    -----
    Original SQL

    PE08: Number of patients grouped by zip code of residence::

        SELECT
            state,
            NVL( zip, '9999999' ) AS zip,
            count(\*) Num_Persons_count
        FROM
            person
        LEFT OUTER JOIN
            location
        USING( location_id )
        GROUP BY
            state,
            NVL( zip, '9999999' )
        ORDER BY 1, 2;
    """
    p = _alias(inspector.tables['person'], 'p')
    l = _alias(inspector.tables['location'], 'l')
    j = _join(p, l, p.c.location_id == l.c.location_id)
    columns = [j.c.l_state,j.c.l_zip,_func.count(j.c.l_zip).label('count')]
    if return_columns:
        columns = [col for col in columns if col.name in return_columns]
    if not person_ids:
        statement = _select(columns).\
                    select_from(j).\
                    group_by(j.c.l_state,j.c.l_zip).\
                    order_by(j.c.l_state, j.c.l_zip)
    else:
        statement = _select(columns).\
                    select_from(j).\
                    where(\
                        j.c.p_person_id.in_(person_ids)).\
                    group_by(j.c.l_state, j.c.l_zip).\
                    order_by(j.c.l_state, j.c.l_zip)
    return inspector.execute(statement)

def patient_counts_by_year_of_birth_and_gender(inspector, person_ids=None, return_columns=None):
    """
    Returns patient counts stratified by year of birth and gender for the database or alternativily, for a supplied list of person_ids.

    Parameters
    ----------
    person_ids : list of int, optional
        list of person_ids [int].  If None (default), get the gender distribution for all individuals in the person table
    inspector : inspectomop.inspector.Inspector
    return_columns : list of str, optional
        - optional subset of columns to return from the query
        - columns : ['gender_concept_id','gender','year_of_birth', 'count']

    Returns
    -------
    results : inspectomop.results.Results


    Notes
    -----
    Original SQL

    PE09: Number of patients by gender, stratified by year of birth::

        SELECT
            gender_concept_id,
            c.concept_name AS gender_name,
            year_of_birth,
            COUNT(p.person_id) AS num_persons
        FROM
            person p
        INNER JOIN
            concept c ON p.gender_concept_id = c.concept_id
        GROUP BY
            gender_concept_id,
            c.concept_name,
            year_of_birth
        ORDER BY
            concept_name,
            year_of_birth;
    """
    p = _alias(inspector.tables['person'], 'p')
    c = _alias(inspector.tables['concept'], 'c')
    columns = [c.c.concept_id, c.c.concept_name.label('gender'),p.c.year_of_birth,_func.count(p.c.year_of_birth).label('count')]
    if return_columns:
        columns = [col for col in columns if col.name in return_columns]
    if not person_ids:
        statement = _select(columns).\
                    where(c.c.concept_id == p.c.gender_concept_id).\
                    group_by(p.c.year_of_birth, c.c.concept_name).\
                    order_by(p.c.year_of_birth, c.c.concept_name)
    else:
        statement = _select(columns).\
                    where(_and_(\
                        p.c.person_id.in_(person_ids),\
                        c.c.concept_id == p.c.gender_concept_id)).\
                    group_by(p.c.year_of_birth, c.c.concept_name).\
                    order_by(p.c.year_of_birth, c.c.concept_name)
    return inspector.execute(statement)
