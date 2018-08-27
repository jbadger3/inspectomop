from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy import Date, DateTime, String, Integer, Float

def _concept(metadata):
    Table('concept', metadata,
            Column('concept_id', Integer,primary_key=True),
            Column('concept_name', String(255)),
            Column('domain_id', String(20), ForeignKey('domain.domain_id')),
            Column('vocabulary_id', String(20), ForeignKey('vocabulary.vocabulary_id')),
            Column('concept_class_id', String(20)),
            Column('standard_concept', String(1)),
            Column('concept_code', String(50)),
            Column('valid_start_date',Date),
            Column('valid_end_date',Date),
            Column('invalid_reason',String(1)),
            extend_existing=True
        )

def _vocabulary(metadata):
    Table('vocabulary', metadata,
            Column('vocabulary_id', String(20), primary_key=True),
            Column('vocabulary_name', String(255)),
            Column('vocabulary_reference', String(255)),
            Column('vocabulary_version', String(255)),
            Column('vocabulary_concept_id', Integer, ForeignKey('concept.concept_id')),
            extend_existing=True
            )

def _domain(metadata):
    Table('domain', metadata,
            Column('domain_id', String(20), primary_key=True),
            Column('domain_name', String(255)),
            Column('domain_concept_id', Integer, ForeignKey('concept.concept_id')),
            extend_existing=True
        )

def _concept_class(metadata):
    Table('concept_class', metadata,
            Column('concept_class_id', String(20), primary_key=True),
            Column('concept_class_name', String(255)),
            Column('concept_class_concept_id', Integer, ForeignKey('concept.concept_id')),
            extend_existing=True
        )

def _concept_relationship(metadata):
    Table('concept_relationship', metadata,
            Column('concept_id_1', Integer, ForeignKey('concept.concept_id'),primary_key=True),
            Column('concept_id_2', Integer, ForeignKey('concept.concept_id'),primary_key=True),
            Column('relationship_id', String(20)),
            Column('valid_start_date', Date),
            Column('valid_end_date', Date),
            Column('invalid_reason', String(1)),
            extend_existing=True
        )

def _relationship(metadata):
    Table('relationship', metadata,
            Column('relationship_id', String(20),primary_key=True),
            Column('relationship_name', String(255)),
            Column('is_hierarchical', String(1)),
            Column('defines_ancestry', String(1)),
            Column('reverse_relationship_id', String(20)),
            Column('relationship_concept_id', Integer, ForeignKey('concept.concept_id')),
            extend_existing=True
        )

def _concept_synonym(metadata):
    Table('concept_synonym', metadata,
            Column('concept_id', Integer,ForeignKey('concept.concept_id'),primary_key=True),
            Column('concept_synonym_name', String(1000),primary_key=True),
            Column('language_concept_id', Integer,ForeignKey('concept.concept_id')),
            extend_existing=True
        )

def _concept_ancestor(metadata):
    Table('concept_ancestor', metadata,
            Column('ancestor_concept_id', Integer,ForeignKey('concept.concept_id'),primary_key=True),
            Column('descendant_concept_id', Integer,ForeignKey('concept.concept_id'),primary_key=True),
            Column('min_levels_of_separation', Integer),
            Column('max_levels_of_separation', Integer),
            extend_existing=True
        )

def _source_to_concept_map(metadata):
    Table('source_to_concept_map', metadata,
            Column('source_code', String(50),primary_key=True),
            Column('source_concept_id', Integer,ForeignKey('concept.concept_id')),
            Column('source_vocabulary_id', String(20), ForeignKey('vocabulary.vocabulary_id')),
            Column('source_code_description', String(255)),
            Column('target_concept_id', Integer, ForeignKey('concept.concept_id')),
            Column('target_vocabulary_id', String(20), ForeignKey('vocabulary.vocabulary_id')),
            Column('valid_start_date', Date),
            Column('valid_end_date', Date),
            Column('invalid_reason',String(1)),
            extend_existing=True
        )

def _drug_strength(metadata):
    Table('drug_strength', metadata,
            Column('drug_concept_id', Integer,ForeignKey('concept.concept_id'),primary_key=True),
            Column('ingredient_concept_id', Integer, ForeignKey('concept.concept_id'),primary_key=True),
            Column('amount_value', Float),
            Column('amount_unit_concept_id', Integer, ForeignKey('concept.concept_id')),
            Column('numerator_value', Float),
            Column('numerator_unit_concept_id', Integer, ForeignKey('concept.concept_id')),
            Column('denominator_value', Float),
            Column('denominator_unit_concept_id', Integer, ForeignKey('concept.concept_id')),
            Column('box_size', Integer),
            Column('valid_start_date', Date),
            Column('valid_end_date', Date),
            Column('invalid_reason', String(1)),
            extend_existing = True
        )

def _cohort_definition(metadata):
    Table('cohort_definition', metadata,
        Column('cohort_definition_id', Integer, primary_key=True),
        Column('cohort_definition_name', String(255)),
        Column('cohort_definition_description', String()),
        Column('definition_type_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('cohort_definition_syntax', String),
        Column('subject_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('cohort_initiation_date', Date),
        extend_existing = True
    )

def _attribute_definition(metadata):
    Table('attribute_definition', metadata,
        Column('attribute_definition_id', Integer, primary_key=True),
        Column('attribute_name', String(255)),
        Column('attribute_description', String),
        Column('attribute_type_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('attribute_syntax', String),
        extend_existing = True
    )

def _cdm_source(metadata):
    Table('cdm_source', metadata,
        Column('cdm_source_name', String(255), primary_key=True),
        Column('cdm_source_abbreviation', String(25)),
        Column('cdm_holder', String(255)),
        Column('source_description', String),
        Column('source_documentation_reference', String(255)),
        Column('cdm_etl_reference', String(255)),
        Column('source_release_date', Date),
        Column('cdm_release_date', Date),
        Column('cdm_version', String(10)),
        Column('vocabulary_version', String(20)),
        extend_existing = True
    )



def _metadata(metadata):
    Table('metadata', metadata,
        Column('metadata_concept_id', Integer, ForeignKey('concept.concept_id'), primary_key=True),
        Column('metadata_type_concept_id', Integer, ForeignKey('concept.concept_id'), primary_key=True),
        Column('name', String(250)),
        Column('value_as_string', String),
        Column('value_as_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('metadata_date', Date),
        Column('metadata_datetime', DateTime),
        extend_existing = True
        )

def _person(metadata):
    Table('person', metadata,
        Column('person_id', Integer, primary_key=True),
        Column('gender_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('year_of_birth', Integer),
        Column('month_of_birth', Integer),
        Column('day_of_birth', Integer),
        Column('birth_datetime', DateTime),
        Column('race_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('ethnicity_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('location_id', Integer, ForeignKey('location.location_id')),
        Column('provider_id', Integer, ForeignKey('provider.provider_id')),
        Column('care_site_id', Integer, ForeignKey('care_site.care_site_id')),
        Column('person_source_value', String(50)),
        Column('gender_source_value', String(50)),
        Column('gender_source_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('race_source_value', String(50)),
        Column('race_source_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('ethnicity_source_value', String(50)),
        Column('ethnicity_source_concept_id', Integer, ForeignKey('concept.concept_ids')),
        extend_existing = True
    )

def _observation_period(metadata):
    Table('observation_period', metadata,
        Column('observation_period_id', Integer, primary_key = True),
        Column('person_id', Integer, ForeignKey('person.person_id')),
        Column('observation_period_start_date', Date),
        Column('observation_period_end_date', Date),
        Column('period_type_concept_id', Integer, ForeignKey('concpet.concept_id')),
        extend_existing = True
    )

def _specimen(metadata):
    Table('specimen', metadata,
        Column('specimen_id', Integer, primary_key = True),
        Column('person_id', Integer, ForeignKey('person.person_id')),
        Column('specimen_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('specimen_type_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('specimen_date', Date),
        Column('specimen_datetime', DateTime),
        Column('quanity', Float),
        Column('unit_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('anatomic_site_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('disease_status_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('specimen_source_id', String(50)),
        Column('specimen_source_value', String(50)),
        Column('unit_source_value', String(50)),
        Column('anatomic_site_source_value', String(50)),
        Column('disease_status_source_value', String(50)),
        extend_existing = True
    )

def _death(metadata):
    Table('death', metadata,
            Column('person_id', Integer, primary_key=True),
            Column('death_date', Date),
            Column('death_datetime', DateTime),
            Column('death_type_concept_id', Integer, ForeignKey('concept.concept_id')),
            Column('cause_concept_id', Integer, ForeignKey('concept.concept_id')),
            Column('cause_source_value', String(50)),
            Column('cause_source_concept_id', Integer, ForeignKey('concept.concept_id')),
            extend_existing=True
        )

def _visit_occurrence(metadata):
    Table('visit_occurrence', metadata,
        Column('visit_occurrence_id', Integer, primary_key = True),
        Column('person_id', Integer, ForeignKey('person.person_id')),
        Column('visit_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('visit_start_date', Date),
        Column('visit_start_datetime', DateTime),
        Column('visit_end_date', Date),
        Column('visit_end_datetime', DateTime),
        Column('visit_type_concpet_id', Integer, ForeignKey('concept.concept_id')),
        Column('provider_id', Integer, ForeignKey('provider.provider_id')),
        Column('care_site_id', Integer, ForeignKey('care_site.care_site_id')),
        Column('visit_source_value', String(50)),
        Column('visit_source_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('admitting_source_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('admitting_soure_value', String(50)),
        Column('discharge_to_concpet_id', Integer, ForeignKey('concept.concept_id')),
        Column('discharge_to_source_value', String(50)),
        Column('preceding_visit_occurrence_id',Integer, ForeignKey('visit_occurrence.visit_occurrence_id')),
        extend_existing = True
    )

def _visit_detail(metadata):
    Table('visit_detail', metadata,
        Column('visit_detail_id', Integer, primary_key=True),
        Column('person_id', Integer, ForeignKey('person.person_id')),
        Column('visit_detail_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('visit_detail_start_date', Date),
        Column('visit_detail_start_datetime', DateTime),
        Column('visit_detail_end_date', Date),
        Column('visit_detail_end_datetime', DateTime),
        Column('visit_detail_type_concpet_id', Integer, ForeignKey('concept.concept_id')),
        Column('provider_id', Integer, ForeignKey('provider.provider_id')),
        Column('care_site_id', Integer, ForeignKey('care_site.care_site_id')),
        Column('visit_detail_source_value', String(50)),
        Column('visit_detail_source_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('admitting_source_value', String(50)),
        Column('admitting_source_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('discharge_to_source_value', String(50)),
        Column('discharge_to_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('preceding_visit_detail_id', Integer, ForeignKey('visit_detail.visit_detail_id')),
        Column('visit_detail_parent_id', Integer, ForeignKey('visit_detail.visit_detail_id')),
        Column('visit_occurrence_id', Integer, ForeignKey('visit_occurrence.visit_occurrence_id')),
        extend_existing = True
    )

def _procedure_occurrence(metadata):
    Table('procedure_occurrence', metadata,
        Column('procedure_occurrence_id', Integer, primary_key = True),
        Column('person_id', Integer, ForeignKey('person.person_id')),
        Column('procedure_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('procedure_date', Date),
        Column('procedure_datetime', DateTime),
        Column('procedure_type_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('modifier_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('quantity', Integer),
        Column('provider_id', Integer, ForeignKey('provider.provider_id')),
        Column('visit_occurrence_id', Integer, ForeignKey('visit_occurrence.visit_occurrence_id')),
        Column('visit_detail_id', Integer, ForeignKey('visit_detail.visit_detail_id')),
        Column('procedure_source_value', String(50)),
        Column('procedure_source_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('modifier_source_value', String(50)),
        extend_existing = True
    )

def _drug_exposure(metadata):
    Table('drug_exposure', metadata,
        Column('drug_exposure_id', Integer, primary_key = True),
        Column('person_id', Integer, ForeignKey('person.person_id')),
        Column('drug_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('drug_exposure_start_date', Date),
        Column('drug_exposure_start_datetime', DateTime),
        Column('drug_exposure_end_date', Date),
        Column('drug_exposure_end_datetime', DateTime),
        Column('verbatim_end_date', Date),
        Column('drug_type_concpet_id', Integer, ForeignKey('concept.concept_id')),
        Column('stop_reason', String(50)),
        Column('refills', Integer),
        Column('quantity', Float),
        Column('days_supply', Integer),
        Column('sig', String),
        Column('route_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('lot_number', String(50)),
        Column('provider_id', Integer, ForeignKey('provider.provider_id')),
        Column('visit_occurrence_id', Integer, ForeignKey('visit_occurrence.visit_occurrence_id')),
        Column('visit_detail_id', Integer, ForeignKey('visit_detail.visit_detail_id')),
        Column('drug_source_value', String(50)),
        Column('drug_source_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('route_source_value', String(50)),
        Column('dose_unit_source_value', String(50)),
        extend_existing = True
    )

def _device_exposure(metadata):
    Table('device_exposure', metadata,
        Column('device_exposure_id', Integer, primary_key = True),
        Column('person_id', Integer, ForeignKey('person.person_id')),
        Column('device_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('device_exposure_start_date', Date),
        Column('device_exposure_start_datetime', DateTime),
        Column('device_exposure_end_date', Date),
        Column('device_exposure_end_datetime', DateTime),
        Column('device_type_concpet_id', Integer, ForeignKey('concept.concept_id')),
        Column('unique_device_id', String(50)),
        Column('quantiy', Integer),
        Column('provider_id', Integer, ForeignKey('provider.provider_id')),
        Column('visit_occurrence_id', Integer, ForeignKey('visit_occurrence.visit_occurrence_id')),
        Column('visit_detail_id', Integer, ForeignKey('visit_detail.visit_detail_id')),
        Column('device_source_value', String(50)),
        Column('device_source_concept_id', Integer, ForeignKey('concept.concept_id')),
        extend_existing = True
    )

def _condition_occurrence(metadata):
    Table('condition_occurrence', metadata,
        Column('condition_occurrence_id', Integer, primary_key = True),
        Column('person_id', Integer, ForeignKey('person.person_id')),
        Column('condition_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('condition_start_date', Date),
        Column('condition_start_datetime', DateTime),
        Column('condition_end_date', Date),
        Column('condition_end_datetime', DateTime),
        Column('condition_type_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('stop_reason', String(20)),
        Column('provider_id', Integer, ForeignKey('provider.provider_id')),
        Column('visit_occurrence_id', Integer, ForeignKey('visit_occurrence.visit_occurrence_id')),
        Column('visit_detail_id', Integer, ForeignKey('visit_detail.visit_detail_id')),
        Column('condition_source_value', String(50)),
        Column('condition_source_concpet_id', Integer, ForeignKey('concept.concept_id')),
        Column('condition_status_source_value', String(50)),
        Column('condition_status_concpet_id', Integer, ForeignKey('concpet.concept_id')),
        extend_existing = True
    )

def _measurement(metadata):
    Table('measurement', metadata,
        Column('measurement_id', Integer, primary_key = True),
        Column('person_id', Integer, ForeignKey('person.person_id')),
        Column('measurement_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('measurement_date', Date),
        Column('measurement_datetime', DateTime),
        Column('measurement_time', String(10)),
        Column('measurement_type_concpet_id', Integer, ForeignKey('concept.concept_id')),
        Column('operator_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('value_as_number', Float),
        Column('value_as_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('unit_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('range_low', Float),
        Column('range_high', Float),
        Column('provider_id', Integer, ForeignKey('provider.provider_id')),
        Column('visit_occurrence_id', Integer, ForeignKey('visit_occurrence.visit_occurrence_id')),
        Column('visit_detail_id', Integer, ForeignKey('visit_detail.visit_detail_id')),
        Column('measurement_source_value', String(50)),
        Column('measurement_source_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('unit_source_value', String(50)),
        Column('value_source_value', String(50)),
        extend_existing = True
    )

def _note(metadata):
    Table('note', metadata,
        Column('note_id', Integer, primary_key = True),
        Column('person_id', Integer, ForeignKey('person.person_id')),
        Column('note_date', Date),
        Column('note_datetime', DateTime),
        Column('note_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('note_class_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('note_title', String(250)),
        Column('note_text', String),
        Column('encoding_concpet_id', Integer, ForeignKey('concept.concept_id')),
        Column('language_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('provider_id', Integer, ForeignKey('provider.provider_id')),
        Column('visit_occurrence_id', Integer, ForeignKey('visit_occurrence.visit_occurrence_id')),
        Column('visit_detail_id', Integer, ForeignKey('visit_detail.visit_detail_id')),
        Column('note_source_value', String(50)),
        extend_existing = True
    )

def _note_nlp(metadata):
    Table('note_nlp', metadata,
        Column('note_nlp_id', Integer, primary_key = True),
        Column('note_id', Integer, ForeignKey('note.note_id')),
        Column('section_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('snippet', String(250)),
        Column('offset', String(50)),
        Column('lexical_variant', String(250)),
        Column('note_nlp_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('note_nlp_source_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('nlp_system', String(250)),
        Column('nlp_date', Date),
        Column('nlp_datetime', DateTime),
        Column('term_exists', String(1)),
        Column('term_temporal', String(50)),
        Column('term_modifiers', String(2000)),
        extend_existing = True
    )

def _observation(metadata):
    Table('observation', metadata,
        Column('observation_id', Integer, primary_key = True),
        Column('person_id', Integer, ForeignKey('person.person_id')),
        Column('observation_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('observation_date', Date),
        Column('observation_datetime', DateTime),
        Column('observation_type_concpet_id', Integer, ForeignKey('concept.concpet_id')),
        Column('value_as_number', Float),
        Column('value_as_string', String(60)),
        Column('value_as_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('qualifier_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('unit_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('provider_id', Integer, ForeignKey('provider.provider_id')),
        Column('visit_occurrence_id', Integer, ForeignKey('visit_occurrence.visit_occurrence_id')),
        Column('visit_detail_id', Integer, ForeignKey('visit_detail.visit_detail_id')),
        Column('observation_source_value', String(50)),
        Column('observation_source_concpet_id', Integer, ForeignKey('concept.concept_id')),
        Column('unit_source_value', String(50)),
        Column('qualifier_source_value', String(50)),
        extend_existing = True
    )

def _fact_relationship(metadata):
    Table('fact_relationship', metadata,
        Column('domain_concept_id_1', Integer, ForeignKey('concept.concept_id')),
        Column('fact_id_1', Integer, primary_key = True),
        Column('domain_concept_id_2', Integer, ForeignKey('concept.concpet_id')),
        Column('fact_id_2', Integer, primary_key = True),
        Column('relationship_concept_id', Integer, ForeignKey('concept.concept_id')),
        extend_existing = True
    )

def _location(metadata):
    Table('location', metadata,
        Column('location_id', Integer, primary_key = True),
        Column('address_1', String(50)),
        Column('address_2', String(50)),
        Column('city', String(50)),
        Column('state', String(2)),
        Column('zip', String(9)),
        Column('country', String(20)),
        Column('location_source_value', String(50)),
        extend_existing = True
    )

def _care_site(metadata):
    Table('care_site', metadata,
        Column('care_site_id', Integer, primary_key = True),
        Column('care_site_name', String(255)),
        Column('place_of_service_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('location_id', Integer, ForeignKey('location.location_id')),
        Column('care_site_source_value', String(50)),
        Column('place_of_service_source_value', String(50)),
        extend_existing = True
    )

def _provider(metadata):
    Table('provider', metadata,
        Column('provider_id', Integer, primary_key = True),
        Column('provider_name', String(255)),
        Column('npi', String(20)),
        Column('dea', String(20)),
        Column('specialty_concept_id', Integer, ForeignKey('concpet.concept_id')),
        Column('care_site_id', Integer, ForeignKey('care_site.care_site_id')),
        Column('year_of_birth', Integer),
        Column('gender_concpet_id', ForeignKey('concept.concept_id')),
        Column('provider_source_value',String(50)),
        Column('specialty_source_value', String(50)),
        Column('specialty_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('gender_source_value', String(50)),
        Column('gender_source_concept_id', Integer, ForeignKey('concpet.concept_id')),
        extend_existing = True
    )

def _payer_plan_period(metadata):
    Table('payer_plan_period', metadata,
        Column('payer_plan_period_id', Integer, primary_key = True),
        Column('person_id', Integer, ForeignKey('person.person_id')),
        Column('payer_plan_period_start_date', Date),
        Column('payer_plan_period_end_date', Date),
        Column('payer_plan_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('payer_source_value', String(50)),
        Column('payer_source_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('plan_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('plan_source_value', String(50)),
        Column('plan_source_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('sponsor_concpet_id', Integer, ForeignKey('concept.concept_id')),
        Column('spnosor_source_value', String(50)),
        Column('sponsor_source_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('family_source_value', String(50)),
        Column('stop_reason_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('stop_reason_source_value', String(50)),
        Column('stop_reason_source_concept_id', Integer, ForeignKey('concept.concept_id')),
        extend_existing = True
    )

def _cost(metadata):
    Table('cost', metadata,
        Column('cost_id', Integer, primary_key = True),
        Column('cost_event_id', Integer),
        Column('cost_domain_id', String(20)),
        Column('cost_type_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('currency_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('total_charge', Float),
        Column('total_cost', Float),
        Column('total_paid', Float),
        Column('paid_by_provider', Float),
        Column('paid_by_patient', Float),
        Column('paid_patient_copay', Float),
        Column('paid_patient_coinsurance', Float),
        Column('paid_patient_deductible', Float),
        Column('paid_by_primary', Float),
        Column('paid_ingredient_cost', Float),
        Column('paid_dispensing_fee', Float),
        Column('payer_plan_period_id', Integer, ForeignKey('payer_plan_period.payer_plan_period_id')),
        Column('amount_allowed', Float),
        Column('revenue_code_source_value', String(50)),
        Column('drg_concept_id', Integer, ForeignKey('drg.drg_concept_id')),
        Column('drg_source_value', String(3)),
        extend_existing = True
    )

def _cohort(metadata):
    Table('cohort', metadata,
        Column('cohort_definition_id', Integer, ForeignKey('cohort_definition.cohort_definition_id'), primary_key = True),
        Column('subject_id', Integer, primary_key = True),
        Column('cohort_start_date', Date),
        Column('cohort_end_date', Date),
        extend_existing = True
    )

def _cohort_attribute(metadata):
    Table('cohort_attribute', metadata,
        Column('cohort_definition_id', Integer, ForeignKey('cohort_definition.cohort_definition_id'), primary_key = True),
        Column('subject_id', Integer, primary_key = True),
        Column('cohort_start_date', Date),
        Column('cohort_end_date', Date),
        Column('attribute_definition_id', Integer, ForeignKey('attribute_definition.attribute_definition_id')),
        Column('value_as_number', Float),
        Column('value_as_concept_id', Integer, ForeignKey('concept.concept_id')),
        extend_existing = True
    )

def _drug_era(metadata):
    Table('drug_era', metadata,
        Column('drug_era_id', Integer, primary_key = True),
        Column('person_id', Integer, ForeignKey('person.person_id')),
        Column('drug_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('drug_era_start_date', Date),
        Column('drug_era_end_date', Date),
        Column('drug_exposure_count', Integer),
        Column('gap_days', Integer),
        extend_existing = True
    )

def _dose_era(metadata):
    Table('dose_era', metadata,
        Column('dose_era_id', Integer, primary_key = True),
        Column('person_id', Integer, ForeignKey('person.person_id')),
        Column('drug_concpet_id', Integer, ForeignKey('concpet.concept_id')),
        Column('unit_concept_id', Integer, ForeignKey('concept.concpet_id')),
        Column('dose_value', Float),
        Column('dose_era_start_date', Date),
        Column('dose_era_end_date', Date),
        extend_existing = True
    )

def _condition_era(metadata):
    Table('condition_era', metadata,
        Column('condition_era_id', Integer, primary_key = True),
        Column('person_id', Integer, ForeignKey('person.person_id')),
        Column('condtion_concept_id', Integer, ForeignKey('concept.concept_id')),
        Column('condition_era_start_date', Date),
        Column('condition_era_end_date', Date),
        Column('condition_occurrence_count', Integer),
        extend_existing = True
    )

def _table_definitions():
    """returns a dictionary of functions to generate metadata for the OMOP CDM v5.3.1"""
    return {'concept':_concept,'vocabulary':_vocabulary,'domain':_domain,\
        'concept_class':_concept_class,'concept_relationship':_concept_relationship,\
        'relationship':_relationship, 'concept_synonym':_concept_synonym, \
        'concept_ancestor':_concept_ancestor, 'source_to_concept_map':_source_to_concept_map, \
        'drug_strength':_drug_strength,'cohort_definition':_cohort_definition, \
        'attribute_definition':_attribute_definition, 'cdm_source':_cdm_source, \
        'metadata':_metadata, 'person':_person, 'observation_period':_observation_period, \
        'specimen':_specimen, 'death':_death, 'visit_occurrence':_visit_occurrence, \
        'visit_detail':_visit_detail, 'procedure_occurrence':_procedure_occurrence, \
        'drug_exposure':_drug_exposure, 'device_exposure':_device_exposure, \
        'condition_occurrence':_condition_occurrence, 'measurement':_measurement, \
        'note':_note, 'note_nlp':_note_nlp, 'observation':_observation, \
        'fact_relationship': _fact_relationship, 'location':_location, \
        'care_site':_care_site, 'provider':_provider, 'payer_plan_period':_payer_plan_period, \
        'cost':_cost,'cohort':_cohort, 'cohort_attribute':_cohort_attribute, 'drug_era':_drug_era, \
        'dose_era':_dose_era, 'condition_era':_condition_era}
