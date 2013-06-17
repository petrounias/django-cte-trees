Module cte_tree.models
============================================

.. moduleauthor:: Alexis Petrounias <www.petrounias.org>

Any Model can be turned into a tree by inheriting from the abstract
:class:`CTENode`. By default, this model will feature a :class:`ForeignKey` to
`self` named `parent`, and with a `related_name` of `children`. Furthermore, it
will feature a custom :class:`CTENodeManager` through the
:attr:`CTENode.objects` attribute.

Each instance of a :class:`CTENode` will feature three **virtual** fields, by
default named :attr:`depth`, :attr:`path`, and :attr:`ordering`; these fields
are populated through a custom CTE SQL query, and contain, respectively, the
depth of a node (starting with root nodes of depth one), the path (an array of
primary keys, or an encoded string if the primary key type requires this), and
a custom ordering key (usually starting with the DFS or BFS order key, and then
extended with custom ordering specified by the concrete Model).

All parameters regarding the configuration of the tree are specified as
attributes in the concrete Model inheriting from :class:`CTENode`, and have the
form :attr:`_cte_node_*`. See below for a complete listing and interpretation of
each parameter.

An important caveat when using CTE queries is ordering: any CTE query which is
cloned and processed through an :meth:`order_by` invocation will result in the
CTE ordering of the nodes to be overridden. Therefore, if you wish to maintain
proper tree ordering, you must specify any custom fields to order by through the
:attr:`_cte_node_order_by` attribute (see below). Unfortunately, it is not
possible to re-create tree ordering through an :meth:`order_by` invocation (see
technical notes for an explanation).

In case custom ordering among siblings is desired (such as using an integer, or
lexicographic order of a string name, and so on), the :meth:`move` method
accepts a parameter ``position`` which, if not ``None``, is expected to be a
callable that is invoked with the destination and the node currently being
moved as arguments, before any modification to the parent relationship is made.
Thus, the :meth:`move` method delegates to this callable in order to specify or
modify order-related attributes, enforce constraints, or even change the
attributes of siblings (such as creating a hole in a contiguous integer total
order).


.. contents::
    :local:
  
=======
CTENode
=======

.. autoclass:: cte_tree.models.CTENode
   :members:


==============
CTENodeManager
==============

.. autoclass:: cte_tree.models.CTENodeManager
   :members:

