.. general:

General
============================================

.. contents::
    :local:
  

=============================
Prerequisites
=============================

- Python >= 2.4
- Django >= 1.2
- PostgreSQL >= 8.4
- psycopg2 >= 2.4


Optionally, for migration management:

- South >= 0.7

=============================
Obtaining
=============================

- Author's home page of the project: http://www.petrounias.org/software/django-cte-trees/

- Git repository on GitHub: https://github.com/petrounias/django-cte-trees/

- Mercurial repository on BitBucket: http://www.bitbucket.org/petrounias/django-cte-trees/


=============================
Installation
=============================

Include the cte_tree module as an application in your Django project through the INSTALLED_APPS list in your settings::

    INSTALLED_APPS = (
        ...,
        'cte_tree',
        ...,
    )



=============================
Basic Usage
=============================

Define a Model which inherits from cte_tree.models.CTENode::

    class Category(CTENode):
	
        name = CharField(max_length = 128, null = False)
		
        def __unicode__(self):
            return '%s @ %s' % (self.name, self.depth)
			
The Category Model will now have a *parent* foreign key to *self*, as well as all the tree structure virtual fields (depth, path, ordering) and methods inherited from CTENode, and a custom Manager for performing the custom CTE queries.

The following is an example usage of Category::

    >>> root = Category.objects.create(name = 'root')
    >>> middle = Category.objects.create(name = 'middle', parent = root)
    >>> bottom = Category.objects.create(name = 'bottom', parent = middle)
    >>> print(Category.objects.all())
    [<Category: root @ 1>, <Category: middle @ 2>, <Category: bottom @ 3>]

See the module documentation and examples for a comprehensive guide on using the CTE node and its manager.

=============================
Release Notes
=============================

v0.9.0, 3/5/2011 -- Initial public release.
v0.9.1, 19/11/2011 -- Added is_branch utility method to CTENode Model.
v0.9.2, 3/3/2012 -- Introduced structural operations for representing trees as dictionaries, traversing attributes and structure (visitor pattern), and 'drilldown' facility based on attribute path filtering. Added documentation and removed whitespace.

=============================
Future Work
=============================

- Abstract models for sibling ordering semantics (integer total and partial orders, and lexicographic string orders) [high priority, easy task].
- Support for dynamic specification of traversal and ordering [normal priority, hard task].
- Support other databases (which feature CTE in some way) [low priority, normal difficulty task].


=============================
Contributors
=============================

Written and maintained by Alexis Petrounias < http://www.petrounias.org/ >


=============================
License
=============================

Copyright (c) 2011, Alexis Petrounias <www.petrounias.org>

All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

Neither the name of the author nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


