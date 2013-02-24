#django-cte-trees

Experimental implementation of Adjecency-List trees for Django using PostgreSQL Common Table Expressions (CTE).

## Overview

The primary aim is to completely hide the management of tree structure, as well as explore the issues related to including CTE in the Django ORM, which requires modifying the query construction and SQL generation in a non-obtrusive way.

Although handling tree structure in a transparent way is a desirable characteristic for many applications, the currently known limitations of including CTE (see below) will be a show-stopper for many other applications. Unless you know beforehand that these limitations will not affect your application, this module is not suitable for you, and you should use an actively managed tree structure (such as django-mptt <https://github.com/django-mptt/django-mptt/> or django-treebeard <http://code.tabo.pe/django-treebeard/>).


## Characteristics

Simple: inheriting from an abstract node model is sufficient to obtain tree functionality for any Model.

Seamless: does not use RawQuerySet, so queries using CTE can be combined with normal Django queries, and won't confuse the SQLCompiler or other QuerySets, including using multiple databases.

Self-contained: tree nodes can be manipulated without worrying about maintaining tree structure in the database.

Single query: all tree traversal operations can be performed through a single query, including children, siblings, ancestors, roots, and descendants.

Flexible ordering: supports (a subset of) normal Django ordering as well as ordering on tree structure information, including depth and path, in DFS and BFS orders.

Multiple delete semantics: supports Pharaoh, Grandmother, and Monarchy deletion patterns.

Code: unit tests, coverage, documentation, comments.


## Known limitations

Virtual fields not usable in external queries: it is not yet possible to use the virtual fields which describe the tree structure (depth, path, and ordering information) in queries other than directly on the CTE Nodes. Consequently, you cannot order on these fields any Model other than the CTE Nodes themselves. See the technical notes for details.

Cannot merge queries with OR: because CTE relies on custom WHERE clauses added through extra, the overloaded bitwise OR operator cannot be used with query composition.

Cannot use new Nodes without loading: immediately after creating a CTE Node, it must be read from the database if you need to use its tree structure (depth, path, and ordering information).

Cannot order descending: you cannot order on structure fields (depth, path) or additional normal fields combined with structure fields in descending order.
