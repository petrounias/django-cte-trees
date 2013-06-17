.. basic:

Basic Usage
===========
All imports are from::

    from cte_tree.models import ...


.. contents::
    :local:


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
