.. technical:

Technical Notes
===============

.. contents::
    :local:

=========
CTE Trees
=========

See PostgreSQL WITH queries: http://www.postgresql.org/docs/devel/static/queries-with.html

And the PostgreSQL wiki on CTE: http://wiki.postgresql.org/wiki/CTEReadme


============
Custom Query
============

The custom query compiler generates the following SQL::

 WITH RECURSIVE {cte} (
           "{depth}", "{path}", "{ordering}", "{pk}") AS (

    SELECT 1 AS depth,
           array[{pk_path}] AS {path},
           {order} AS {ordering},
           T."{pk}"
     FROM  {db_table} T
     WHERE T."{parent}" IS NULL

     UNION ALL

    SELECT {cte}.{depth} + 1 AS {depth},
           {cte}.{path} || {pk_path},
           {cte}.{ordering} || {order},
           T."{pk}"
     FROM  {db_table} T
     JOIN  {cte} ON T."{parent}" = {cte}."{pk}")

where the variables are obtained from the CTE Node parameters.

=====================
Custom Query Compiler
=====================

The compiler constructs the ad hoc variables which will be used in the SELECT
query, synthesizes the WHERE clause, as well as the order-by parameter, and then
uses the Query's 'add_extra' method. The table 'cte' is added, as well as an
'ExtraWhere' node which ensures that the primary key of the 'cte' table matches
the primary key of the model's table. If the CTE recursion is to be started from
an offset Node, then an ExtraWhere is also added ensuring that all Nodes which
are to be returned contain the primary key of the offset Node in their
materialized 'path' virtual field (hence the offset Node is also included
itself, which means descendant lookups must explicitly exclude it).

In order to allow Django model fields and corresponding columns for the virtual
fields 'depth', 'path', and 'ordering', appropriate prefixing is ensured for
all queries involving the CTE compiler. So, for example, assuming the CTE Node
model features an integer field 'order', specifying that ordering should be
descending breadth first search (but ascending for siblings), you would write:

 order_by('-depth', 'order')

and the compiler would translate this to ['-"cte".depth', 'order'] because the
'depth' field is provided by the CTE query but the 'order' field is provided by
the SELECT query.

PostgreSQL array type is used in order to materialize the 'path' and the
'ordering' virtual fields; automatic casting is done by the compiler so primary
keys and fields contributing to the order can be more 'exotic', such as a UUID
primary key, converting VARCHAR to TEXT, and so on.

===========
Performance
===========

There is no straightforward way to compare the performance of CTE trees with
alternatives (such as Django-treebeard or Django-mptt) because actively-managed
tree structures perform multiple SQL queries for certain operations, as well as
perform many operations in the application layer. Therefore, performance
comparison will make sense depending on your application and the kinds of
operations it performs on trees.

Generally, each SQL query involving a node Model will create the recursive CTE
temporary table, even if the virtual fields are not selected (deferred).

Note that INSERT and UPDATE operations are not affected at all from the CTE
compiler, and thus impose no overhead.


=======
Testing
=======

Use the cte_tree_test Django dummy application and module. By default, it uses
a localhost database 'dummy' with user 'dummy' and password 'dummy'.
