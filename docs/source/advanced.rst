.. basic:

Advanced Usage
===========
All imports are from::

    from cte_tree.models import ...


.. contents::
    :local:


Extending and Inheritance
-------------------------

If a custom Manager is specified, it must inherit from CTENodeManager::

    class CategoryManager(CTENodeManager):

        ...

    class Category(CTENode):

        name = CharField(max_length = 128, null = False)

        objects = CategoryManager()

        def __unicode__(self):
            return '%s @ %s' % (self.name, self.depth)



Dummy Fields
------------

It is possible to add the fields for 'depth', 'path', and 'ordering' as normal
fields to a Django model, so that mechanics of Django, third party, or your own
modules find them. Doing so will create columns for them in the database, but
their values will always be overridden by the materialized CTE table. They will
also never be written (unless you explicitly do so) through an UPDATE query,
meaning the columns will remain empty. Although this is wasteful, it may be
useful or even necessary, given that Django does not cater for non-managed
fields (only entire models).

Therefore, the fields package provides three such fields which are automatically
set to null, blank, and non-editable, and can be used as such::


    from cte_tree.fields import DepthField, PathField, OrderingField

    class Category(CTENode):

        depth = DepthField()
        path = PathField()
        ordering = OrderingField()

        name = CharField(max_length = 128, null = False)

        objects = CategoryManager()

        def __unicode__(self):
            return '%s @ %s' % (self.name, self.depth)

