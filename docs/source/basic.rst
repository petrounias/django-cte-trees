.. basic:

Basic Usage
===========
All imports are from::

    from cte_tree.models import ...


.. contents::
    :local:


Defining a Node
---------------

Define a Model which inherits from cte_tree.models.CTENode::

    class Category(CTENode):

        name = CharField(max_length = 128, null = False)

        def __unicode__(self):
            return '%s @ %s' % (self.name, self.depth)

The Category Model will now have a *parent* foreign key to *self*, as well as
all the tree structure virtual fields (depth, path, ordering) and methods
inherited from CTENode, and a custom Manager for performing the custom CTE
queries.

The following is an example usage of Category::

    >>> root = Category.objects.create(name = 'root')
    >>> middle = Category.objects.create(name = 'middle', parent = root)
    >>> bottom = Category.objects.create(name = 'bottom', parent = middle)
    >>> print(Category.objects.all())
    [<Category: root @ 1>, <Category: middle @ 2>, <Category: bottom @ 3>]

See the module documentation and examples for a comprehensive guide on using the
CTE Node and its manager.


Ordering
--------

By default, CTE Nodes are ordered based on their primary key. This means there
is no guarantee of the traversal order before Nodes are created, nor when new
Nodes are added (although between no changes to the tree the order remains the
same). In most situations (especially test cases) automatic primary keys are
generated in an ascending order, which may give the false impression of
deterministic ordering!

To specify a tree ordering, use the '_cte_node_order_by' parameter, which is a
list of fields with which to order similar to Django's order_by. This parameter
will create the 'ordering' virtual field for the CTE Node, which also supports
ordering on multiple fields by supporting arrays for the 'ordering' field. For
example, the following Category features an 'order' integer field::

    class Category(CTENode):

        name = CharField(max_length = 128, null = False)

        order = PositiveIntegerField(null = False, default = 0)

        _cte_node_order_by = ('order', )

        def __unicode__(self):
            return '%s @ %s : %s' % (self.name, self.depth, self.ordering)

The following is an example usage of the ordered Category::

    >>> root = Category.objects.create(name = 'root')
    >>> first_middle = Category.objects.create(name = 'first middle', parent = root, order = 1)
    >>> second_middle = Category.objects.create(name = 'second middle', parent = root, order = 2)
    >>> first_bottom = Category.objects.create(name = 'first bottom', parent = first_middle, order = 1)
    >>> second_bottom = Category.objects.create(name = 'second bottom', parent = second_middle, order = 1)
    >>> Category.objects.all()
    [<Category: root @ 1 : [0]>,
     <Category: first middle @ 2 : [0, 1]>,
     <Category: first bottom @ 3 : [0, 1, 1]>,
     <Category: second middle @ 2 : [0, 2]>,
     <Category: second bottom @ 3 : [0, 2, 1]>]

which is a depth-first ordering. A breadth-first ordering (in this example
through Django's 'order_by' query, which overrides the default ordering
specified via '_cte_node_order_by') is achieved via::

    >>> Category.objects.all().order_by('depth', 'order')
    [<Category: root @ 1 : [0]>,
     <Category: first middle @ 2 : [0, 1]>,
     <Category: second middle @ 2 : [0, 2]>,
     <Category: first bottom @ 3 : [0, 1, 1]>,
     <Category: second bottom @ 3 : [0, 2, 1]>]

Hence, quite exotic ordering can be achieved. As a last example, a descending
in-order breadth-first search, but with ascending siblings:

    >>> Category.objects.all().order_by('-depth', 'order')
    [<Category: first bottom @ 3 : [0, 1, 1]>,
     <Category: second bottom @ 3 : [0, 2, 1]>,
     <Category: first middle @ 2 : [0, 1]>,
     <Category: second middle @ 2 : [0, 2]>,
     <Category: root @ 1 : [0]>]

and so on.

