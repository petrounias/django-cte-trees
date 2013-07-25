Django CTE Trees
================

Django Adjacency-List trees using PostgreSQL Common Table Expressions (CTE). Its
aim is to completely hide the management of tree structure.

Version 1.0.0 beta 2

Documentation: http://django-cte-trees.readthedocs.com/

Django Package: https://www.djangopackages.com/packages/p/django-cte-trees/

Overview
========

Although handling tree structure in a transparent way is a desirable
characteristic for many applications, the currently **known limitations** of
including CTE (see below) will be a show-stopper for many other applications.
Unless you know beforehand that these limitations will not affect your
application, this module is **not suitable** for you, and you should use an
actively managed tree structure (such as django-mptt
https://github.com/django-mptt/django-mptt/ or django-treebeard
http://code.tabo.pe/django-treebeard/ ).


*Characteristics*

- **Simple**: inheriting from an abstract node model is sufficient to obtain
  tree functionality for any Model.

- **Seamless**: does not use RawQuerySet, so queries using CTE can be combined
  with normal Django queries, and won't confuse the SQLCompiler or other
  QuerySets, including using multiple databases.

- **Self-contained**: tree nodes can be manipulated without worrying about
  maintaining tree structure in the database.

- **Single query**: all tree traversal operations can be performed through a
  single query, including children, siblings, ancestors, roots, and descendants.

- **Powerful ordering**: supports (a subset of) normal Django ordering as well
  as ordering on tree structure information, including depth and path, in DFS
  and BFS orders.

- **Multiple delete semantics**: supports Pharaoh, Grandmother, and Monarchy
  deletion patterns.

- **Code**: unit tests, code coverage, documentation, comments.


*Known limitations*

- **Virtual fields not usable in external queries**: it is not yet possible to
  use the virtual fields which describe the tree structure (depth, path, and
  ordering information) in queries other than directly on the CTE Nodes.
  Consequently, you cannot order on these fields any Model other than the CTE
  Nodes themselves. See the technical notes for details.

- **Cannot merge queries with OR**: because CTE relies on custom WHERE clauses
  added through extra, the bitwise OR operator cannot be used with query
  composition.

- **Cannot use new Nodes without loading**: immediately after creating a CTE
  Node, it must be read from the database if you need to use its tree structure
  (depth, path, and ordering information).

- **Cannot order descending**: you cannot order on structure fields (depth,
  path) or additional normal fields combined with structure fields in descending
  order.

Prerequisites
=============

Core:

- PostgreSQL >= 8.4
- Python >= 2.4
- psycopg2 >= 2.4
- Django >= 1.2


Obtaining
=========

- Author's website for the project: http://www.petrounias.org/software/django-cte-trees/

- Git repository on GitHub: https://github.com/petrounias/django-cte-trees/

- Mercurial repository on BitBucket: http://www.bitbucket.org/petrounias/django-cte-trees/


Installation
============

Via setup tools::

    python setup.py install

Via pip and pypi::

    pip install django-cte-trees


Include the cte_tree module as an application in your Django project through the
INSTALLED_APPS list in your settings::

    INSTALLED_APPS = (
        ...,
        'cte_tree',
        ...,
    )


Release Notes
=============

- v0.9.0 @ 3 May 2011 Initial public release.

- v0.9.1 @ 19 November 2011 Added is_branch utility method to CTENode Model.

- v0.9.2 @ 3 March 2012 Introduced structural operations for representing trees
  as dictionaries, traversing attributes and structure (visitor pattern), and
  'drilldown' facility based on attribute path filtering. Added documentation
  and removed whitespace.

- v1.0.0, 17 July 2013 Beta version 1; cleaned up package and comments, updated
  pypi data, added documentation, and updated Django multiple database support
  for compatibility with latest version.

- v1.0.0, 27 July 2013 Beta version 2; several optimisations to reduce compiled
  query size; fixed an issue with descendants where the offset node was returned
  as the first descendant; introduced support for CTE table prefixing on virtual
  fields when used in ordering; introduced support for UPDATE queries; added
  documentation for ordering, further technical notes, and advanced usage.


Development Status
==================

Actively developed and maintained since 2011. Currently used in production in
proprietary projects by the author and his team, as well as other third parties.


Future Work
===========

- Abstract models for sibling ordering semantics (integer total and partial
  orders, and lexicographic string orders) [high priority, easy task].
- Support for dynamic specification of traversal and ordering [normal priority,
  hard task].
- Support other databases (which feature CTE in some way) [low priority, normal
  difficulty task].


Contributors
============

Written and maintained by Alexis Petrounias < http://www.petrounias.org/ >


License
=======

Released under the OSI-approved BSD license.

Copyright (c) 2011 - 2013 Alexis Petrounias < www.petrounias.org >,
all rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this list
of conditions and the following disclaimer.

Redistributions in binary form must reproduce the above copyright notice, this
list of conditions and the following disclaimer in the documentation and/or
other materials provided with the distribution.

Neither the name of the author nor the names of its contributors may be used to
endorse or promote products derived from this software without specific prior
written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
