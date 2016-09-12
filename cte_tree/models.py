# -*- coding: utf-8 -*-
#
# This document is free and open-source software, subject to the OSI-approved
# BSD license below.
#
# Copyright (c) 2011 - 2013 Alexis Petrounias <www.petrounias.org>,
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# * Neither the name of the author nor the names of its contributors may be used
# to endorse or promote products derived from this software without specific
# prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Django CTE Trees Models.
"""
from __future__ import absolute_import

__status__ = "beta"
__version__ = "1.0.2"
__maintainer__ = (u"Alexis Petrounias <www.petrounias.org>", )
__author__ = (u"Alexis Petrounias <www.petrounias.org>", )

# Django
from django.core.exceptions import ImproperlyConfigured, FieldError
from django.db.models import Model, Manager, ForeignKey, CASCADE
from django.db.models.fields import FieldDoesNotExist
from django.utils.translation import ugettext as _

# Django CTE Trees
from .query import CTEQuerySet


class CTENodeManager(Manager):
    """ Custom :class:`Manager` which ensures all queries involving
        :class:`CTENode` objects are processed by the custom SQL compiler.
        Additionally, provides tree traversal queries for obtaining node
        children, siblings, ancestors, descendants, and roots.

        If your Model inherits from :class:`CTENode` and use your own custom
        :class:`Manager`, you must ensure the following three:

        1) your :class:`Manager` inherits from :class:`CTENodeManager`,

        2) if you override the :meth:`get_queryset` method in order to
        return a custom :class:`QuerySet`, then your `QuerySet` must also
        inherit from :class:`CTENodeManager.CTEQuerySet`, and

        3) invoke the :meth:`_ensure_parameters` on your :class:`Manager`
        at least once before using a :class:`QuerySet` which inherits from
        :class:`CTENodeManager.CTEQuerySet`, unless you have supplied the
        necessary CTE node attributes on the :class:`CTENode` :class:`Model` in
        some other way.

        The methods :meth:`prepare_delete`, :meth:`prepare_delete_pharaoh`,
        :meth:`prepare_delete_grandmother`, and
        :meth:`prepare_delete_monarchy` can be directly used to prepare
        nodes for deletion with either the default or explicitly-specified
        deletion semantics. The :class:`CTENode` abstract :class:`Model`
        defines a :meth:`CTENode.delete` method which delegates preparation
        to this manager.

    """
    # SQL CTE temporary table name.
    DEFAULT_TABLE_NAME = 'cte'
    DEFAULT_CHILDREN_NAME = 'children'

    # Tree traversal semantics.
    TREE_TRAVERSAL_NONE = 'none'
    TREE_TRAVERSAL_DFS = 'dfs'
    TREE_TRAVERSAL_BFS = 'bfs'
    TREE_TRAVERSAL_METHODS = (TREE_TRAVERSAL_NONE, TREE_TRAVERSAL_DFS,
        TREE_TRAVERSAL_BFS)
    TREE_TRAVERSAL_CHOICES = (
        (TREE_TRAVERSAL_NONE, _('none')),
        (TREE_TRAVERSAL_DFS, _('depth first search')),
        (TREE_TRAVERSAL_BFS, _('breadth first search')),
    )
    DEFAULT_TREE_TRAVERSAL = TREE_TRAVERSAL_DFS

    # Virtual fields.
    VIRTUAL_FIELD_DEPTH = 'depth'
    VIRTUAL_FIELD_PATH = 'path'
    VIRTUAL_FIELD_ORDERING = 'ordering'

    # Deletion semantics.
    DELETE_METHOD_NONE = 'none'
    DELETE_METHOD_PHARAOH = 'pharaoh'
    DELETE_METHOD_GRANDMOTHER = 'grandmother'
    DELETE_METHOD_MONARCHY = 'monarchy'
    DELETE_METHODS = (DELETE_METHOD_NONE, DELETE_METHOD_PHARAOH,
        DELETE_METHOD_GRANDMOTHER, DELETE_METHOD_MONARCHY)
    DELETE_METHOD_CHOICES = (
        (DELETE_METHOD_NONE, _('none')),
        (DELETE_METHOD_PHARAOH, _('pharaoh (all subtree)')),
        (DELETE_METHOD_GRANDMOTHER, _('grandmother (move subtree up)')),
        (DELETE_METHOD_MONARCHY,
         _('monarchy (first child becomes subtree root)')),
    )
    DEFAULT_DELETE_METHOD = DELETE_METHOD_PHARAOH

    # Related manager lookup should return this custom Manager in order to use
    # the custom QuerySet above.
    use_for_related_fields = True


    def _ensure_parameters(self):
        """ Attempts to load and verify the CTE node parameters. Will use
            default values for all missing parameters, and raise an exception if
            a parameter's value cannot be verified. This method will only
            perform these actions once, and set the :attr:`_parameters_checked`
            attribute to ``True`` upon its first success.
        """

        if hasattr(self, '_parameters_checked'):
            return

        if not hasattr(self.model, '_cte_node_table') or \
            self.model._cte_node_table is None:
            setattr(self.model, '_cte_node_table',
                self.DEFAULT_TABLE_NAME)

        if not hasattr(self.model, '_cte_node_depth') or \
            self.model._cte_node_depth is None:
            setattr(self.model, '_cte_node_depth',
                self.VIRTUAL_FIELD_DEPTH)

        if not hasattr(self.model, '_cte_node_path') or \
            self.model._cte_node_depth is None:
            setattr(self.model, '_cte_node_path',
                self.VIRTUAL_FIELD_PATH)

        if not hasattr(self.model, '_cte_node_ordering') or \
            self.model._cte_node_ordering is None:
            setattr(self.model, '_cte_node_ordering',
                self.VIRTUAL_FIELD_ORDERING)

        if not hasattr(self.model, '_cte_node_traversal') or \
            self.model._cte_node_traversal is None:
            setattr(self.model, '_cte_node_traversal',
                self.DEFAULT_TREE_TRAVERSAL)

        if not hasattr(self.model, '_cte_node_children') or \
            self.model._cte_node_children is None:
            setattr(self.model, '_cte_node_children',
                self.DEFAULT_CHILDREN_NAME)

        if not hasattr(self.model, '_cte_node_primary_key_type'):
            setattr(self.model, '_cte_node_primary_key_type', None)

        # Determine the parent foreign key field name, either
        # explicitly specified, or the first foreign key to 'self'.
        # If we need to determine, then we set the attribute for future
        # reference.
        if not hasattr(self.model, '_cte_node_parent') or \
            self.model._cte_node_parent is None:
            found = False
            for f in self.model._meta.fields:
                if isinstance(f, ForeignKey):
                    if f.rel.to == self.model:
                        setattr(self.model, '_cte_node_parent', f.name)
                        found = True
            if not found:
                raise ImproperlyConfigured(
                    _('CTENode must have a Foreign Key to self for the parent '
                      'relation.'))

        try:
            parent_field = self.model._meta.get_field(
                self.model._cte_node_parent)
        except FieldDoesNotExist:
            raise ImproperlyConfigured(''.join([
                _('CTENode._cte_node_parent must specify a Foreign Key to self, '
                  'instead it is: '),
                self.model._cte_node_parent]))

        # Ensure parent relation is a Foreign Key to self.
        if not parent_field.rel.to == self.model:
            raise ImproperlyConfigured(''.join([
                _('CTENode._cte_node_parent must specify a Foreign Key to self, '
                  'instead it is: '),
                self.model._cte_node_parent]))

        # Record the parent field attribute name for future reference.
        setattr(self.model, '_cte_node_parent_attname',
            self.model._meta.get_field(
                self.model._cte_node_parent).attname)

        # Ensure traversal choice is valid.
        traversal_choices = [choice[0] for choice in \
            self.TREE_TRAVERSAL_CHOICES]
        if not self.model._cte_node_traversal in traversal_choices:
            raise ImproperlyConfigured(
                ' '.join(['CTENode._cte_node_traversal must be one of [',
                    ', '.join(traversal_choices), ']; instead it is:',
                    self.model._cte_node_traversal]))

        # Ensure delete choice is valid.
        if not hasattr(self.model, '_cte_node_delete_method') or \
            self.model._cte_node_delete_method is None:
            setattr(self.model, '_cte_node_delete_method',
                self.DEFAULT_DELETE_METHOD)
        else:
            # Ensure specified method is valid.
            method_choices = [dm[0] for dm in \
                self.DELETE_METHOD_CHOICES]
            if not self.model._cte_node_delete_method in method_choices:
                raise ImproperlyConfigured(
                    ' '.join(['delete method must be one of [',
                        ', '.join(method_choices), ']; instead it is:',
                        self.model._cte_node_delete_method]))

        setattr(self, '_parameters_checked', True)


    def _ensure_virtual_fields(self, node):
        """ Attempts to read the virtual fields from the given `node` in order
            to ensure they exist, resulting in an early :class:`AttributeError`
            exception in case of missing virtual fields. This method requires
            several parameters, and thus invoked :meth:`_ensure_parameters`
            first, possibly resulting in an :class:`ImproperlyConfigured`
            exception being raised.

            :param node: the :class:`CTENode` for which to verify that the
                virtual fields are present.
        """
        # Uses several _cte_node_* parameters, so ensure they exist.
        self._ensure_parameters()
        for vf in [self.model._cte_node_depth, self.model._cte_node_path,
            self.model._cte_node_ordering]:
            if not hasattr(node, vf):
                raise FieldError(
                    _('CTENode objects must be loaded from the database before '
                      'they can be used.'))


    def get_queryset(self):
        """ Returns a custom :class:`QuerySet` which provides the CTE
            functionality for all queries concerning :class:`CTENode` objects.
            This method overrides the default :meth:`get_queryset` method of
            the :class:`Manager` class.

            :returns: a custom :class:`QuerySet` which provides the CTE
                functionality for all queries concerning :class:`CTENode`
                objects.
        """
        # The CTEQuerySet uses _cte_node_* attributes from the Model, so ensure
        # they exist.
        self._ensure_parameters()
        return CTEQuerySet(self.model, using = self._db)


    def roots(self):
        """ Returns a :class:`QuerySet` of all root :class:`CTENode` objects.

            :returns: a :class:`QuerySet` of all root :class:`CTENode` objects.
        """
        # We need to read the _cte_node_parent attribute, so ensure it exists.
        self._ensure_parameters()
        # We need to construct: self.filter(parent = None)
        return self.filter(**{ self.model._cte_node_parent : None})


    def leaves(self):
        """ Returns a :class:`QuerySet` of all leaf nodes (nodes with no
            children).

            :return: A :class:`QuerySet` of all leaf nodes (nodes with no
                children).
        """
        # We need to read the _cte_node_children attribute, so ensure it exists.
        self._ensure_parameters()
        return self.exclude(**{
            '%s__id__in' % self.model._cte_node_children : self.all(),
        })


    def branches(self):
        """ Returns a :class:`QuerySet` of all branch nodes (nodes with at least
            one child).

            :return: A :class:`QuerySet` of all leaf nodes (nodes with at least
                one child).
        """
        # We need to read the _cte_node_children attribute, so ensure it exists.
        self._ensure_parameters()
        return self.filter(**{
            '%s__id__in' % self.model._cte_node_children : self.all(),
        }).distinct()


    def root(self, node):
        """ Returns the :class:`CTENode` which is the root of the tree in which
            the given `node` participates (or `node` if it is a root node). This
            method functions through the :meth:`get` method.

            :param node: A :class:`CTENode` whose root is required.

            :return: A :class:`CTENode` which is the root of the tree in which
                the given `node` participates (or the given `node` if it is a
                root node).
        """
        # We need to use the path virtual field, so ensure it exists.
        self._ensure_virtual_fields(node)
        return self.get(pk = getattr(node, self.model._cte_node_path)[0])


    def siblings(self, node):
        """ Returns a :class:`QuerySet` of all siblings of a given
            :class:`CTENode` `node`.

            :param node: a :class:`CTENode` whose siblings are required.

            :returns: A :class:`QuerySet` of all siblings of the given `node`.
        """
        # We need to read the _cte_node_parent* attributes, so ensure they
        # exist.
        self._ensure_parameters()
        # We need to construct: filter(parent = node.parent_id)
        return self.filter(**{ self.model._cte_node_parent : \
            getattr(node, self.model._cte_node_parent_attname) }).exclude(
                id = node.id)


    def ancestors(self, node):
        """ Returns a :class:`QuerySet` of all ancestors of a given
            :class:`CTENode` `node`.

            :param node: A :class:`CTENode` whose ancestors are required.

            :returns: A :class:`QuerySet` of all ancestors of the given `node`.
        """
        # We need to use the path virtual field, so ensure it exists.
        self._ensure_virtual_fields(node)
        return self.filter(
            pk__in = getattr(node, self.model._cte_node_path)[:-1])


    def descendants(self, node):
        """ Returns a :class:`QuerySet` with all descendants for a given
            :class:`CTENode` `node`.

            :param node: the :class:`CTENode` whose descendants are required.

            :returns: A :class:`QuerySet` with all descendants of the given
                `node`.
        """
        # We need to read the _cte_node_* attributes, so ensure they exist.
        self._ensure_parameters()
        # This is implemented in the CTE WHERE logic, so we pass a reference to
        # the offset CTENode to the custom QuerySet, which will process it.
        # Because the compiler will include the node in question in the offset,
        # we must exclude it here.
        return CTEQuerySet(self.model, using = self._db,
            offset = node).exclude(pk = node.pk)


    def is_parent_of(self, node, subject):
        """ Returns ``True`` if the given `node` is the parent of the given
            `subject` node, ``False`` otherwise. This method uses the
            :attr:`parent` field, and so does not perform any query.

            :param node: the :class:`CTENode' for which to determine whether it
                is a parent of the `subject`.

            :param subject: the :class:`CTENode` for which to determine whether
                its parent is the `node`.

            :returns: ``True`` if `node` is the parent of `subject`, ``False``
                otherwise.
        """
        return subject.parent_id == node.id


    def is_child_of(self, node, subject):
        """ Returns ``True`` if the given `node` is a child of the given
            `subject` node, ``False`` otherwise. This method used the
            :attr:`parent` field, and so does not perform any query.

            :param node: the :class:`CTENode' for which to determine whether it
                is a child of the `subject`.

            :param subject: the :class:`CTENode` for which to determine whether
                one of its children is the `node`.

            :returns: ``True`` if `node` is a child of `subject`, ``False``
                otherwise.
        """
        return node.parent_id == subject.id


    def is_sibling_of(self, node, subject):
        """ Returns ``True`` if the given `node` is a sibling of the given
            `subject` node, ``False`` otherwise. This method uses the
            :attr:`parent` field, and so does not perform any query.

            :param node: the :class:`CTENode' for which to determine whether it
                is a sibling of the `subject`.

            :param subject: the :class:`CTENode` for which to determine whether
                one of its siblings is the `node`.

            :returns: ``True`` if `node` is a sibling of `subject`, ``False``
                otherwise.
        """
        # Ensure nodes are not siblings of themselves.
        return not node.id == subject.id and node.parent_id == subject.parent_id


    def is_ancestor_of(self, node, subject):
        """ Returns ``True`` if the given `node` is an ancestor of the given
            `subject` node, ``False`` otherwise. This method uses the
            :attr:`path` virtual field, and so does not perform any query.

            :param node: the :class:`CTENode' for which to determine whether it
                is an ancestor of the `subject`.

            :param subject: the :class:`CTENode` for which to determine whether
                one of its ancestors is the `node`.

            :returns: ``True`` if `node` is an ancestor of `subject`, ``False``
                otherwise.
        """
        # We will need to use the path virtual field, so ensure it exists.
        self._ensure_virtual_fields(node)

        # Convenience check so is_ancestor_of can be combined with methods
        # returning nodes without the caller having to worry about a None
        # subject.
        if subject is None:
            return False

        # Optimization: a node will never be an ancestor of a root node.
        if getattr(subject, subject._cte_node_depth) == 1:
            return False

        # The path will either be an index of primitives, or an encoding of an
        # array.
        if type(getattr(node, node._cte_node_path)) == list:
            # We can slice with -1 because we know that depth > 1 from above.
            return node.id in getattr(subject, subject._cte_node_path)[0:-1]
        else:
            # Search for node id up to the penultimate entry in the path of the
            # subject, meaning we ignore the end of the path consisting of:
            # a) the ending closing curly brace,
            # b) the length of the subject id, and
            # c) the separator character,
            # therefore we look for a match ending at the length of the
            # subject's id string plus two (so negative index length minus two).
            return getattr(subject, subject._cte_node_path)[:-len(str(subject.id)) - 2].index(
                str(node.id)) > 0


    def is_descendant_of(self, node, subject):
        """ Returns ``True`` if the given `node` is a descendant of the given
            `subject` node, ``False`` otherwise. This method uses the
            :attr:`path` virtual field, and so does not perform any query.

            :param node: the :class:`CTENode' for which to determine whether it
                is a descendant of the `subject`.

            :param subject: the :class:`CTENode` for which to determine whether
                one of its descendants is the `node`.

            :returns: ``True`` if `node` is a descendant of `subject`, ``False``
                otherwise.
        """
        # We will need to use the path virtual field, so ensure it exists.
        self._ensure_virtual_fields(node)

        # Convenience check so is_descendant_of can be combined with methods
        # returning nodes without the caller having to worry about a None
        # subject.
        if subject is None:
            return False

        # Optimization: a root node will never be a descendant of any node.
        if getattr(node, node._cte_node_depth) == 1:
            return False

        # The path will either be an index of primitives, or an encoding of an
        # array.
        if type(getattr(node, node._cte_node_path)) == list:
            # We can slice with -1 because we know that depth > 1 from above.
            return subject.id in getattr(node, node._cte_node_path)[0:-1]
        else:
            # Search for subject id up to the penultimate entry in the path of
            # the node, meaning we ignore the end of the path consisting of:
            # a) the ending closing curly brace,
            # b) the length of the node id, and
            # c) the separator character,
            # therefore we look for a match ending at most at the length of the
            # node's id string plus two (so negative index length minus two).
            return getattr(node, node._cte_node_path)[:-len(str(node.id)) - 2].index(str(subject.id)) > 0


    def is_leaf(self, node):
        """ Returns ``True`` if the given `node` is a leaf (has no children),
            ``False`` otherwise.

            :param node: the :class:`CTENode` for which to determine whether it
                is a leaf.

            :return: ``True`` if `node` is a leaf, ``False`` otherwise.
        """
        return not node.children.exists()


    def is_branch(self, node):
        """ Returns ``True`` if the given `node` is a branch (has at least one
            child), ``False`` otherwise.

            :param node: the :class:`CTENode` for which to determine whether it
                is a branch.

            :return: ``True`` if `node` is a branch, ``False`` otherwise.
        """
        return node.children.exists()


    def attribute_path(self, node, attribute, missing = None,
        visitor = lambda node, attribute: getattr(node, attribute, None)):
        """ Generates a list of values of the `attribute` of all ancestors of
            the given `node` (as well as the node itself). If a value is
            ``None``, then the optional value of `missing` is used (by default
            ``None``).

            By default, the ``getattr(node, attribute, None) or missing``
            mechanism is used to obtain the value of the attribute for each
            node. This can be overridden by supplying a custom `visitor`
            function, which expects as arguments the node and the attribute, and
            should return an appropriate value for the required attribute.

            :param node: the :class:`CTENode` for which to generate the
                attribute path.

            :param attribute: the name of the attribute.

            :param missing: optional value to use when attribute value is None.

            :param visitor: optional function responsible for obtaining the
                attribute value from a node.

            :return: a list of values of the required `attribute` of the
                ancestor path of the given `node`.
        """
        return [ visitor(c, attribute) or missing for c in node.ancestors() ] +\
            [ visitor(node, attribute) or missing ]


    def as_tree(self, visitor = None, children = None):
        """ Recursively traverses each tree (starting from each root) in order
            to generate a dictionary-based tree structure of the entire forest.
            Each level of the forest/tree is a list of nodes, and each node
            consists of a dictionary representation, where the entry
            ``children`` (by default) consists of a list of dictionary
            representations of its children.

            Optionally, a `visitor` callback can be used, which is responsible
            for generating a dictionary representation of a given
            :class:`CTENode`. By default, the :meth:`_default_node_visitor` is
            used which generates a dictionary with the current node as well as
            structural properties. See :meth:`_default_node_visitor` for the
            appropriate signature of this callback.

            Optionally, a `children` callback can be used, which is responsible
            for determining which :class:`CTENode`s are children of each visited
            :class:`CTENode`, resulting in a key (by default ``children``) and a
            list of children :class:`CTENode` objects, which are then included
            in the dictionary representation of the currently-visited node. See
            :meth:`_default_node_children` for the appropriate signature of this
            callback.

            For each node visited, the :meth:`CTENode.as_tree` method is invoked
            along with the optional `visitor` and `children` arguments. This
            method, if not overridden, will delegate to :meth:`node_as_tree`,
            which is responsible for invoking the :meth:`visitor` and
            :meth:`children methods, as well as updating the dictionary
            representation of the node with the representation of the children
            nodes.

            :param visitor: optional function responsible for generating the
                dictionary representation of a node.

            :param children: optional function responsible for generating a
                children key and list for a node.

            :return: a dictionary representation of the structure of the forest.
        """
        return [root.as_tree(visitor = visitor, children = children) for \
            root in self.roots()]


    def node_as_tree(self, node,
        visitor = lambda self, node: self._default_node_visitor(node),
        children = lambda self, node, visitor, children: \
            self._default_node_children(node, visitor, children)):
        """ Visits a :class:`CTENode` `node` and delegates to the (optional)
            `visitor` callback, as well as the (optional) `children` callback,
            in order to generate a dictionary representation of the node along
            with its children nodes.

            :param node: the :class:`CTENode` for which to generate the
                representation.

            :param visitor: optional function responsible for generating the
                dictionary representation of the node.

            :param children: optional function responsible for generating a
                children key and list for the node.

            :return: a dictionary representation of the structure of the node
                and its descendant tree.
        """
        tree = visitor(self, node)
        tree.update(children(self, node, visitor, children))
        return tree


    def _default_node_visitor(self, node):
        """ Generates a dictionary representation of the given :class:`CTENode`
        `node`, which consists of the node itself under the key ``node``, as
        well as structural information under the keys ``depth``, ``path``,
        ``ordering``, ``leaf``, and ``branch``.

        :param node: the :class:`CTENode` for which to generate the
            representation.

        :return: a dictionary representation of the structure of the node.
        """
        return {
            'depth' : getattr(node, node._cte_node_depth),
            'path' : [str(c) for c in getattr(node, node._cte_node_path)],
            'ordering' : getattr(node, node._cte_node_ordering),
            'leaf' : node.is_leaf(),
            'branch' : node.is_branch(),
            'node' : node,
        }


    def _default_node_children(self, node, visitor, children):
        """ Generates a key and list of children of the given :class:`CTENode`
        `node`, intended to be used as an update to the dictionary
        representation generated by the :meth:`node_as_tree` method. The key is
        ``children`` and the list consists of the children of the given node as
        determined by the `children` callback.

        Each child node is, in turn, visited through recursive calls to
        :meth:`node_as_child`, and the `visitor` and `children` parameters are
        passed along.

        :param node: the :class:`CTENode` for which to generate the children
            representation.

        :param visitor: optional function responsible for generating the
            dictionary representation of the node.

        :param children: optional function responsible for generating a
            children key and list for the node.

        :return: a key and list representation of the structure of the children
            of the given node.
        """
        return { self.model._cte_node_children : [ self.node_as_tree(child,
            visitor = visitor, children = children) for child in \
                node.children.all() ] }


    def drilldown(self, attributes, path):
        """ Recursively descends the tree/forest (starting from each root node)
            in order to find a :class:`CTENode` which corresponds to the given
            `path`. The path is expected to be an iterable of tuples, called
            path components, consisting of attribute values with which to filter
            through the QuerySet API. The name of the attribute to which each
            value corresponds is specified in `attributes`, which is expected
            to conform to Django's QuerySet API for the filter semantics. Each
            value in the path component tuple will be mapped to its
            corresponding attribute name before being passed to the filter
            method.

            For example, if the node model features the integer field ``x``
            and the boolean field ``y``, we can drill down in the following way:

                drilldown(('x__gte', 'y'),[(35, True), (37, False)])

            The simplest form of drilldown is to match with equality on a single
            attribute, such as ``name``, as in the following example:

                drilldown(('name',), [('path',), ('to',), ('my',), ('node',)])

            Don't forget the trailing comma if specifying singleton tuples! If
            you need very simple, one-attribute path components, it is suggested
            you extend the manager with your own convenience method; the above
            will, for instance, become:

                def drilldown_by_name(self, path):
                    return self.drilldown(('name',),
                        [(component,) for component in path])

            Failure to find the required node results in a :class:`DoesNotExist`
            exception being raised.

            An empty path will result in the first root node being returned (if
            at least one root node exists).
        """

        # empty path result in first root, if present
        if len(path) == 0:
            try:
                return self.roots()[0]
            except IndexError:
                raise self.model.DoesNotExist

        # bootstrap with the first component, then iterate through the remaining
        # components in the path as long as each child node is found
        component = path[0]
        current = None

        # mapping of attribute names with values, as per QuerySet filter
        attrs = lambda component: dict(zip(attributes, component))

        # find the root corresponding to the bootstrapped initial path component
        try:
            root = self.roots().filter(**attrs(component))[0]
        except IndexError:
            raise self.model.DoesNotExist

        # proceed to drill down until path components are exhausted
        current = root
        for component in path[1:]:
            try:
                current = current.children.filter(**attrs(component))[0]
            except IndexError:
                raise self.model.DoesNotExist
        return current


    def prepare_delete(self, node, method, position = None, save = True):
        """ Prepares a given :class:`CTENode` `node` for deletion, by executing
            the required deletion semantics (Pharaoh, Grandmother, or Monarchy).

            The `method` argument can be one of the valid
            :const:`DELETE_METHODS` choices. If it is
            :const:`DELETE_METHOD_NONE` or ``None``, then the default delete
            method will be used (as specified from the optional
            :attr:`_cte_node_delete_method`).

            Under the :const:`DELETE_METHOD_GRANDMOTHER` and
            :const:`DELETE_METHOD_MONARCHY` delete semantics, descendant nodes
            may be moved; in this case the optional `position` can be a
            ``callable`` which is invoked prior to each move operation (see
            :meth:`move` for details).

            Furthermore, by default, after each move operation, sub-tree nodes
            which were moved will be saved through a call to :meth:`Model.save`
            unless `save` is ``False``.

            This method delegates move operations to :meth:`move`.

            :param node: the :class:`CTENode` to prepare for deletion.

            :param method: optionally, a delete method to use.

            :param position: optionally, a ``callable`` to invoke prior to each
                move operation.

            :param save: flag indicating whether to save after each move
                operation, ``True`` by default.
        """
        # If no delete method preference is specified, use attribute.
        if method is None:
            method = node._cte_node_delete_method
        # If no preference specified, use default.
        if method == self.DELETE_METHOD_NONE:
            method = self.DEFAULT_DELETE_METHOD
        # Delegate to appropriate method.
        getattr(self, 'prepare_delete_%s' % method)(node, position, save)


    def prepare_delete_pharaoh(self, node, position = None, save = True):
        """ Prepares a given :class:`CTENode` `node` for deletion, by executing
            the :const:`DELETE_METHOD_PHARAOH` semantics.

            This method does not perform any sub-tree reorganization, and hence
            no move operation, so the `position` and `save` arguments are
            ignored; they are present for regularity purposes with the rest of
            the deletion preparation methods.

            :param node: the :class:`CTENode` to prepare for deletion.

            :param position: this is ignored, but present for regularity.

            :param save: this is ignored, but present for regularity.
        """
        # Django will take care of deleting the sub-tree through the reverse
        # Foreign Key parent relation.
        pass


    def prepare_delete_grandmother(self, node, position = None, save = True):
        """ Prepares a given :class:`CTENode` `node` for deletion, by executing
            the :const:`DELETE_METHOD_GRANDMOTHER` semantics. Descendant nodes,
            if present, will be moved; in this case the optional `position` can
            be a ``callable`` which is invoked prior to each move operation (see
            :meth:`move` for details).

            By default, after each move operation, sub-tree nodes which were
            moved will be saved through a call to :meth:`Model.save` unless
            `save` is ``False``.

            This method delegates move operations to :meth:`move`.

            :param node: the :class:`CTENode` to prepare for deletion.

            :param position: optionally, a ``callable`` to invoke prior to each
                move operation.

            :param save: flag indicating whether to save after each move
                operation, ``True`` by default.
        """
        # Move all children to the node's parent.
        for child in node.children.all():
            child.move(node.parent, position, save)


    def prepare_delete_monarchy(self, node, position = None, save = True):
        """ Prepares a given :class:`CTENode` `node` for deletion, by executing
            the :const:`DELETE_METHOD_MONARCHY` semantics. Descendant nodes,
            if present, will be moved; in this case the optional `position` can
            be a ``callable`` which is invoked prior to each move operation (see
            :meth:`move` for details).

            By default, after each move operation, sub-tree nodes which were
            moved will be saved through a call to :meth:`Model.save` unless
            `save` is ``False``.

            This method delegates move operations to :meth:`move`.

            :param node: the :class:`CTENode` to prepare for deletion.

            :param position: optionally, a ``callable`` to invoke prior to each
                move operation.

            :param save: flag indicating whether to save after each move
                operation, ``True`` by default.
        """
        # We are going to iterate all children, even though the first child is
        # treated in a special way, because the query iterator may be custom, so
        # we will avoid using slicing children[0] and children[1:].
        first = None
        for child in node.children.all():
            if first is None:
                first = child
                first.move(node.parent, position, save)
            else:
                child.move(first, position, save)


    def move(self, node, destination, position = None, save = False):
        """ Moves the given :class:`CTENode` `node` and places it as a child
            node of the `destination` :class:`CTENode` (or makes it a root node
            if `destination` is ``None``).

            Optionally, `position` can be a callable which is invoked prior to
            placement of the `node` with the `node` and the `destination` node
            as the sole two arguments; this can be useful in implementing
            specific sibling ordering semantics.

            Optionally, if `save` is ``True``, after the move operation
            completes (after the :attr:`CTENode.parent` foreign key is updated
            and the `position` callable is called if present), a call to
            :meth:`Model.save` is made.

            :param destination: the destination node of this move, ``None``
                denoting that the node will become a root node.

            :param position: optional callable invoked prior to placement for
                purposes of custom sibling ordering semantics.

            :param save: optional flag indicating whether this model's
                :meth:`save` method should be invoked after the move.

            :return: this node.
        """
        # Allow custom positioning semantics to specify the position before
        # setting the parent.
        if not position is None:
            position(node, destination)
        node.parent = destination
        if save:
            node.save()
        return node


class CTENode(Model):
    """ Abstract :class:`Model` which implements a node in a CTE tree. This
        model features a mandatory foreign key to the parent node (hence to
        ``self``), which, when ``None``, indicates a root node. Multiple nodes
        with a ``None`` parent results in a forest, which can be constrained
        either with custom SQL constraints or through application logic.

        It is necessary for any custom :class:`Manager` of this model to inherit
        from :class:`CTENodeManager`, as all functionality of the CTE tree is
        implemented in the manager.

        It is possible to manipulate individual nodes when not loaded through
        the custom manager, or when freshly created either through the
        :meth:`create` method or through the constructor, however, any operation
        which requires tree information (the :attr:`depth`, :attr:`path`,
        and :attr:`ordering` virtual fields) will not work, and any attempt to
        invoke such methods will result in an :class:`ImproperlyConfigured`
        exception being raised.

        Many runtime properties of nodes are specified through a set of
        parameters which are stored as attributes of the node class, and begin
        with ``_cte_node_``. Before any of these parameters are used, the
        manager will attempt to load and verify them, raising an
        :class:`ImproperlyConfigured` exception if any errors are encountered.
        All parameters have default values.

        All :class:`QuerySet` objects involving CTE nodes use the
        :meth:`QuerySet.extra` semantics in order to specify additional
        ``SELECT``, ``WHERE``, and ``ORDER_BY`` SQL semantics, therefore, they
        cannot be combined through the ``OR`` operator (the ``|`` operator).

        The following parameters can optionally be specified at the class level:

        * _cte_node_traversal:

            A string from one of :const:`TREE_TRAVERSAL_METHODS`, which
            specifies the default tree traversal order. If this parameters is
            ``None`` or :const:`TREE_TRAVERSAL_NONE`, then
            :const:`DEFAULT_TREE_TRAVERSAL` method is used (which is ``dfs``
            for depth-first).

        * _cte_node_order_by:

            A list of strings or tuples specifying the ordering of siblings
            during tree traversal (in the breadth-first method, siblings are
            ordered depending on their parent and not the entire set of nodes at
            the given depth of the tree).

            The entries in this list can be any of the model fields, much like
            the entries in the :attr:`ordering` of the model's :class:`Meta`
            class or the arguments of the :meth:`order_by` method of
            :class:`QuerySet`.

            These entries may also contain the virtual field :attr:`depth`,
            which cannot be used by the normal :class:`QuerySet` because Django
            cannot recognize such virtual fields.

            In case of multiple entries, they must all be of the same database
            type. For VARCHAR fields, their values will be cast to TEXT, unless
            otherwise specified. It is possible to specify the database type
            into which the ordering field values are cast by providing tuples of
            the form ``(fieldname, dbtype)`` in the ordering sequence.

            Specifying cast types is necessary when combining different data
            types in the ordering sequence, such as an int and a float (casting
            the int into a float is probably the desired outcome in this
            situation). In the worst case, TEXT can be specified for all casts.

        * _cte_node_delete_method:

            A string specifying the desired default deletion semantics, which
            may be one of :const:`DELETE_METHODS`. If this parameter is missing
            or ``None`` or :const:`DELETE_METHOD_NONE`, then the default
            deletion semantics :const:`DEFAULT_DELETE_METHOD` will be used
            (which is :const:`DELETE_METHOD_PHARAOH` or ``pharaoh`` for the
            Pharaoh deletion semantics).

        * _cte_node_parent:

            A string referencing the name of the :class:`ForeignKey` field which
            implements the parent relationship, typically called ``parent`` and
            automatically inherited from this class.

            If this parameter is missing, and no field with the name ``parent``
            can be found, then the first :class:`ForeignKey` which relates to
            this model will be used as the parent relationship field.

        * _cte_node_children:

            A string referencing the `related_name` attribute of the
            :class:`ForeignKey` field which implements the parent relationship,
            typically called ``parent`` (specified in
            :const:`DEFAULT_CHILDREN_NAME`) and automatically
            inherited from this class.

        * _cte_node_table:

            The name of the temporary table to use with the ``WITH`` CTE SQL
            statement when compiling queries involving nodes. By default this is
            :const:`DEFAULT_TABLE_NAME` (which is ``cte``).

        * _cte_node_primary_key_type:

            A string representing the database type of the primary key, if the
            primary key is a non-standard type, and must be cast in order to be
            used in the :attr:`path` or :attr:`ordering` virtual fields
            (similarly to the :attr:`_cte_node_order_by` parameter above).

            A ``VARCHAR`` primary key will be automatically cast to ``TEXT``,
            unless explicitly specified otherwise through this parameter.


        * _cte_node_path, _cte_node_depth, _cte_node_ordering:

            Strings specifying the attribute names of the virtual fields
            containing the path, depth, and ordering prefix of each node, by
            default, respectively, :const:`VIRTUAL_FIELD_PATH` (which is
            ``path``), :const:`VIRTUAL_FIELD_DEPTH` (which is ``depth``), and
            :const:`VIRTUAL_FIELD_ORDERING` (which is ``ordering``).
    """

    # This ForeignKey is mandatory, however, its name can be different, as long
    # as it's specified through _cte_node_parent.
    _cte_node_parent = 'parent'
    parent = ForeignKey('self', on_delete=CASCADE, null = True, blank = True,
        related_name = 'children')

    # This custom Manager is mandatory.
    objects = CTENodeManager()


    def root(self):
        """ Returns the CTENode which is the root of the tree in which this
            node participates.
        """
        return self.__class__.objects.root(self)


    def siblings(self):
        """ Returns a :class:`QuerySet` of all siblings of this node.

            :returns: A :class:`QuerySet` of all siblings of this node.
        """
        return self.__class__.objects.siblings(self)


    def ancestors(self):
        """ Returns a :class:`QuerySet` of all ancestors of this node.

            :returns: A :class:`QuerySet` of all ancestors of this node.
        """
        return self.__class__.objects.ancestors(self)


    def descendants(self):
        """ Returns a :class:`QuerySet` of all descendants of this node.

            :returns: A :class:`QuerySet` of all descendants of this node.
        """
        return self.__class__.objects.descendants(self)


    def is_parent_of(self, subject):
        """ Returns ``True`` if this node is the parent of the given `subject`
            node, ``False`` otherwise. This method uses the :attr:`parent`
            field, and so does not perform any query.

            :param subject: the :class:`CTENode` for which to determine whether
                its parent is this node.

            :returns: ``True`` if this node is the parent of `subject`,
                ``False`` otherwise.
        """
        return self.__class__.objects.is_parent_of(self, subject)


    def is_child_of(self, subject):
        """ Returns ``True`` if this node is a child of the given `subject`
            node, ``False`` otherwise. This method used the :attr:`parent`
            field, and so does not perform any query.

            :param subject: the :class:`CTENode` for which to determine whether
                one of its children is this node.

            :returns: ``True`` if this node is a child of `subject`, ``False``
                otherwise.
        """
        return self.__class__.objects.is_child_of(self, subject)


    def is_sibling_of(self, subject):
        """ Returns ``True`` if this node is a sibling of the given `subject`
            node, ``False`` otherwise. This method uses the :attr:`parent`
            field, and so does not perform any query.

            :param subject: the :class:`CTENode` for which to determine whether
                one of its siblings is this node.

            :returns: ``True`` if this node is a sibling of `subject`, ``False``
                otherwise.
        """
        return self.__class__.objects.is_sibling_of(self, subject)


    def is_ancestor_of(self, subject):
        """ Returns ``True`` if the node is an ancestor of the given `subject`
            node, ``False`` otherwise. This method uses the :attr:`path` virtual
            field, and so does not perform any query.

            :param subject: the :class:`CTENode` for which to determine whether
                one of its ancestors is this node.

            :returns: ``True`` if this node is an ancestor of `subject`,
                ``False`` otherwise.
        """
        return self.__class__.objects.is_ancestor_of(self, subject)


    def is_descendant_of(self, subject):
        """ Returns ``True`` if the node is a descendant of the given `subject`
            node, ``False`` otherwise. This method uses the :attr:`path` virtual
            field, and so does not perform any query.

            :param subject: the :class:`CTENode` for which to determine whether
                one of its descendants is this node.

            :returns: ``True`` if this node is a descendant of `subject`,
                ``False`` otherwise.
        """
        return self.__class__.objects.is_descendant_of(self, subject)


    def is_leaf(self):
        """ Returns ``True`` if this node is a leaf (has no children), ``False``
            otherwise.

            :return: ``True`` if this node is a leaf, ``False`` otherwise.
        """
        return self.__class__.objects.is_leaf(self)


    def is_branch(self):
        """ Returns ``True`` if this node is a branch (has at least one child),
            ``False`` otherwise.

            :return: ``True`` if this node is a branch, ``False`` otherwise.
        """
        return self.__class__.objects.is_branch(self)


    def attribute_path(self, attribute, missing = None, visitor = None):
        """ Generates a list of values of the `attribute` of all ancestors of
            this node (as well as the node itself). If a value is ``None``, then
            the optional value of `missing` is used (by default ``None``).

            By default, the ``getattr(node, attribute, None) or missing``
            mechanism is used to obtain the value of the attribute for each
            node. This can be overridden by supplying a custom `visitor`
            function, which expects as arguments the node and the attribute, and
            should return an appropriate value for the required attribute.

            :param attribute: the name of the attribute.

            :param missing: optional value to use when attribute value is None.

            :param visitor: optional function responsible for obtaining the
                attribute value from a node.

            :return: a list of values of the required `attribute` of the
                ancestor path of this node.
        """
        _parameters = { 'node' : self, 'attribute' : attribute }
        if not missing is None:
            _parameters['missing'] = missing
        if not visitor is None:
            _parameters['visitor'] = visitor
        return self.__class__.objects.attribute_path(**_parameters)


    def as_tree(self, visitor = None, children = None):
        """ Recursively traverses each tree (starting from each root) in order
            to generate a dictionary-based tree structure of the entire forest.
            Each level of the forest/tree is a list of nodes, and each node
            consists of a dictionary representation, where the entry
            ``children`` (by default) consists of a list of dictionary
            representations of its children.

            See :meth:`CTENodeManager.as_tree` and
            :meth:`CTENodeManager.node_as_tree` for details on how this method
            works, as well as its expected arguments.

            :param visitor: optional function responsible for generating the
                dictionary representation of a node.

            :param children: optional function responsible for generating a
                children key and list for a node.

            :return: a dictionary representation of the structure of the forest.
        """
        _parameters = { 'node' : self }
        if not visitor is None:
            _parameters['visitor'] = visitor
        if not children is None:
            _parameters['children'] = children
        return self.__class__.objects.node_as_tree(**_parameters)


    def move(self, destination = None, position = None, save = False):
        """ Moves this node and places it as a child node of the `destination`
            :class:`CTENode` (or makes it a root node if `destination` is
            ``None``).

            Optionally, `position` can be a callable which is invoked prior to
            placement of the node with this node and the destination node as the
            sole two arguments; this can be useful in implementing specific
            sibling ordering semantics.

            Optionally, if `save` is ``True``, after the move operation
            completes (after the :attr:`parent` foreign key is updated and the
            `position` callable is called if present), a call to
            :meth:`Model.save` is made.

            :param destination: the destination node of this move, ``None``
                denoting that the node will become a root node.

            :param position: optional callable invoked prior to placement for
                purposes of custom sibling ordering semantics.

            :param save: optional flag indicating whether this model's
                :meth:`save` method should be invoked after the move.

            :return: this node.
        """
        return self.__class__.objects.move(self, destination, position, save)


    def delete(self, method = None, position = None, save = True):
        """ Prepares the tree for deletion according to the deletion semantics
            specified for the :class:`CTENode` Model, and then delegates to the
            :class:`CTENode` superclass ``delete`` method.

            Default deletion `method` and `position` callable can be overridden
            by being supplied as arguments to this method.

            :param method: optionally a particular deletion method, overriding
                the default method specified for this model.

            :param position: optional callable to invoke prior to each move
                operation, should the delete method require any moves.

            :param save: optional flag indicating whether this model's
                :meth:`save` method should be invoked after each move operation,
                should the delete method require any moves.
        """
        self.__class__.objects.prepare_delete(self, method = method,
            position = position, save = save)
        return super(CTENode, self).delete()


    class Meta:
        abstract = True
        # Prevent cycles in order to maintain tree / forest property.
        unique_together = [('id', 'parent'), ]

