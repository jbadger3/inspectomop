inspectomop.connection.Connection
=================================

.. currentmodule:: inspectomop.connection

.. autoclass:: Connection

   
   .. automethod:: __init__

   
   .. rubric:: Methods

   .. autosummary::
   
      ~Connection.__init__
      ~Connection.begin
      ~Connection.begin_nested
      ~Connection.begin_twophase
      ~Connection.close
      ~Connection.commit
      ~Connection.commit_prepared
      ~Connection.detach
      ~Connection.exec_driver_sql
      ~Connection.execute
      ~Connection.execution_options
      ~Connection.get_execution_options
      ~Connection.get_isolation_level
      ~Connection.get_nested_transaction
      ~Connection.get_transaction
      ~Connection.in_nested_transaction
      ~Connection.in_transaction
      ~Connection.invalidate
      ~Connection.recover_twophase
      ~Connection.rollback
      ~Connection.rollback_prepared
      ~Connection.scalar
      ~Connection.scalars
      ~Connection.schema_for_object
   
   

   
   
   .. rubric:: Attributes

   .. autosummary::
   
      ~Connection.closed
      ~Connection.connection
      ~Connection.default_isolation_level
      ~Connection.dispatch
      ~Connection.info
      ~Connection.invalidated
      ~Connection.should_close_with_result
      ~Connection.dialect
   
   