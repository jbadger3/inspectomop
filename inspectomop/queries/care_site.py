"""
Care site related OMOP data queries.
====================================

Adapted from: https://github.com/OHDSI/OMOP-Queries
"""

from sqlalchemy import select as _select, join as _join,\
    union as _union, union_all as _union_all, \
    distinct as _distinct, between as  _between, alias as _alias, \
    and_ as _and_, or_ as _or_, literal_column as _literal_column, func as _func

def facility_counts_by_type(inspector, return_columns=None):
    """
    Returns facility counts by type in the OMOP CDM i.e. # Inpatient Hospitals, Offices, etc.

    Parameters
    ----------
    inspector : inspectomop.inspector.Inspector
    return_columns : list of str, optional
        - optional subset of columns to return from the query
        - columns : ['place_of_service', 'place_of_service_concept_id', 'facility_count']

    Returns
    -------
    results : inspectomop.results.Results
        a cursor-like object with methods such as fetchone(), fetchmany() etc.

    Notes
    -----
    Original SQL

    CS01: Care site place of service counts::

        SELECT
            cs.place_of_service_concept_id,
            count(1) places_of_service_count
        FROM care_site cs
        GROUP BY
            cs.place_of_service_concept_id
        ORDER BY 1;
    """

    c = _alias(inspector.tables['concept'],'c')
    cs = _alias(inspector.tables['care_site'], 'cs')
    columns = [c.c.concept_name.label('place_of_service'), cs.c.place_of_service_concept_id, _func.count(cs.c.place_of_service_concept_id).label('facility_count')]
    if return_columns:
        columns = [col for col in columns if col.name in return_columns]
    statement = _select(columns).\
                where(c.c.concept_id == cs.c.place_of_service_concept_id).\
                group_by(cs.c.place_of_service_concept_id)
    return inspector.execute(statement)

def patient_counts_by_care_site_type(inspector, return_columns=None):
    """
    Returns pateints counts by facility type.

    Parameters
    ----------
    inspector : inspectomop.inspector.Inspector
    return_columns : list of str, optional
        - optional subset of columns to return from the query
        - columns : ['place_of_service', 'place_of_service_concept_id', 'patient_count']

    Returns
    -------
    results : inspectomop.results.Results

    Notes
    -----
    Original SQL

    CS02: Patient count per care site place of service::

        SELECT
            cs.place_of_service_concept_id,
            count(1) num_patients
        FROM
            care_site cs,
            person p
        WHERE
            p.care_site_id = cs.care_site_id
        GROUP BY
            cs.place_of_service_concept_id
        ORDER BY 1;
    """

    c = _alias(inspector.tables['concept'],'c')
    cs = _alias(inspector.tables['care_site'], 'cs')
    p = _alias(inspector.tables['person'], 'p')
    columns = [c.c.concept_name.label('place_of_service'), cs.c.place_of_service_concept_id, _func.count(cs.c.place_of_service_concept_id).label('patient_count')]
    if return_columns:
        columns = [col for col in columns if col.name in return_columns]
    statement = _select(columns).\
                where(_and_(\
                    p.c.care_site_id == cs.c.care_site_id)).\
                group_by(cs.c.place_of_service_concept_id)
    return inspector.execute(statement)
