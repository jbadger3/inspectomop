.. currentmodule:: inspectomop
.. _api:

API Reference
=============

Inspector
---------
`inspectomop.Inspector`

Constructor
~~~~~~~~~~~

.. currentmodule:: inspectomop.inspector

.. autosummary::
   :toctree: generated/

   Inspector

Attributes
~~~~~~~~~~
.. autosummary::
   :toctree: generated/

   Inspector.connection_url
   Inspector.engine
   Inspector.tables
   Inspector.vocabularies_tables
   Inspector.metadata_tables
   Inspector.clinical_tables
   Inspector.health_system_tables
   Inspector.health_economics_tables
   Inspector.derived_elements_tables

Methods
~~~~~~~
.. autosummary::
   :toctree: generated/

   Inspector.attach_sqlite_db
   Inspector.connect
   Inspector.table_info

Connection
----------
`inspectomop.Connection`

Constructor
~~~~~~~~~~~

.. currentmodule:: inspectomop.connection

.. autosummary::
   :toctree: generated/

   Connection

.. warning::

  Although a public constructor exists, `Connection` objects are meant to be instantiated indirectly from calls to `Inspector.connect()`

Methods
~~~~~~~
.. autosummary::
   :toctree: generated/

   Connection.execute

Results
-------
`inspectomop.Results`

Constructor
~~~~~~~~~~~

.. currentmodule:: inspectomop.results

.. autosummary::
   :toctree: generated/

   Results

.. warning::

  Although a public constructor exists, `Results` objects are meant to be instantiated indirectly from calls to `Connection.execute()`

Methods
~~~~~~~
.. currentmodule:: inspectomop.results
.. autosummary::
   :toctree: generated/

   Results.as_pandas
   Results.as_pandas_chunks

.. _queries:


Queries
-------
`inspectomop.queries`

Care Site
~~~~~~~~~
`inspectomop.queries.care_site`

.. currentmodule:: inspectomop.queries.care_site
.. autosummary::
   :toctree: generated/

   facility_counts_by_type
   patient_counts_by_care_site_type

Condition
~~~~~~~~~
`inspectomop.queries.condition`

.. currentmodule:: inspectomop.queries.condition
.. autosummary::
   :toctree: generated/

   anatomical_site_by_keyword
   condition_concept_for_concept_id
   condition_concepts_for_keyword
   condition_concepts_for_source_codes
   condition_concepts_occurring_at_anatomical_site_concept_id
   conditions_caused_by_pathogen_or_causative_agent_concept_id
   disease_causing_agents_for_keyword
   source_codes_for_concept_ids
   pathogen_concept_for_keyword
   place_of_service_counts_for_condition_concept_id

Drug
~~~~
`inspectomop.queries.drug`

.. currentmodule:: inspectomop.queries.drug
.. autosummary::
   :toctree: generated/

   drug_classes_for_drug_concept_id
   drug_concepts_for_ingredient_concept_id
   indications_for_drug_concept_id
   ingredients_for_drug_concept_ids
   ingredient_concept_ids_for_ingredient_names

General
~~~~~~~
`inspectomop.queries.general`

.. currentmodule:: inspectomop.queries.general
.. autosummary::
  :toctree: generated/

  ancestors_for_concept_id
  children_for_concept_id
  concepts_for_concept_ids
  descendants_for_concept_id
  parents_for_concept_id
  related_concepts_for_concept_id
  siblings_for_concept_id
  synonyms_for_concept_ids
  standard_vocab_for_source_code

Observation
~~~~~~~~~~~
`inspectomop.queries.observation`

.. currentmodule:: inspectomop.queries.observation
.. autosummary::
   :toctree: generated/

   observation_concepts_for_keyword

Payer Plan
~~~~~~~~~~
`inspectomop.queries.payer_plan`

.. currentmodule:: inspectomop.queries.payer_plan
.. autosummary::
   :toctree: generated/

   counts_by_years_of_coverage
   patient_distribution_by_plan_type

Person
~~~~~~
`inspectomop.queries.person`

.. currentmodule:: inspectomop.queries.person
.. autosummary::
   :toctree: generated/

   patient_counts_by_gender
   patient_counts_by_year_of_birth
   patient_counts_by_residence_state
   patient_counts_by_zip_code
   patient_counts_by_year_of_birth_and_gender
