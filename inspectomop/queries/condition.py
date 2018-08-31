"""
Condition related OMOP data queries.

Addapted from: https://github.com/OHDSI/OMOP-Queries
"""

from sqlalchemy import select as _select, join as _join,\
    union as _union, union_all as _union_all, \
    distinct as _distinct, between as  _between, alias as _alias, \
    and_ as _and_, or_ as _or_, literal_column as _literal_column, func as _func

def condition_concepts_for_condition_name(condition_name, inspector,return_columns=None):
    """
    Get standard concepts for a given condition/keyword.

    Parameters
    ----------
    ingredient_names : str


    inspector : inspectomop.Inspector object

    return_columns : list of strings representing the columns to return from the query
        *see Returns section below for full list


    Returns
    -------
    out : inspectomop.Results

    return_columns:

    Original SQL
    ------------
    C02: Find a condition by keyword

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
        col_list = ['concept_id', 'ingredient_name']
        columns = list(filter(lambda x: x in col_list, return_columns))
    statement = _select(columns)\
                .select_from(j2)\
                .where(_and_(\
                _or_(c.vocabulary_id.in_(vocab_ids), _func.lower(c.concept_class_id)==concept_class_id),\
                c.concept_class_id != None,\
                _or_(_func.lower(c.concept_name).ilike('%{}%'.format(condition_name.lower())),\
                    _func.lower(cs.concept_synonym_name).ilike('%{}%'.format(condition_name.lower())))))\
                .distinct()
    return inspector.execute(statement)
