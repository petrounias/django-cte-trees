.. technical:

Technical Notes
============================================

*Coming soon.*


.. contents::
    :local:

=============================
CTE Trees
=============================

*Coming soon.*


=============================
Custom QuerySet
=============================

*Coming soon.*


=============================
Custom SQL Compiler
=============================

*Coming soon.*



=============================
Performance
=============================

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
