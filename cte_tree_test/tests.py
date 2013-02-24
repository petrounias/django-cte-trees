# -*- coding: utf-8 -*-
#
# Copyright (c) 2011, Alexis Petrounias <www.petrounias.org>.
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright notice, this
# list of conditions and the following disclaimer in the documentation and/or
# other materials provided with the distribution.
#
# Neither the name of the author nor the names of its contributors may be used
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

""" Unit tests for the Django CTE Trees test application.
"""

__status__ = "Prototype"
__version__ = "0.9.2"
__maintainer__ = ("Alexis Petrounias <www.petrounias.org>", )
__author__ = ("Alexis Petrounias <www.petrounias.org>", )

# Python
from datetime import date
from uuid import UUID

# Django
from django.test import TestCase
from django.core.exceptions import ImproperlyConfigured, FieldError

# Django CTE Trees
from cte_tree_test.models import *


class SimpleNodeTest(TestCase):
    
    def test_node_creation(self):
        
        node = SimpleNode.objects.create()
        
        self.assertEqual(SimpleNode.objects.get().id, node.id)
        self.assertEqual(len(SimpleNode.objects.all()), 1)
        self.assertEqual(len(SimpleNode.objects.filter()), 1)
        self.assertEqual(SimpleNode.objects.count(), 1)
        
        
    def test_multiple_node_creation(self):
        
        node_1 = SimpleNode.objects.create()
        node_2 = SimpleNode.objects.create()
        
        self.assertEqual(len(SimpleNode.objects.filter()), 2)
        self.assertEqual(SimpleNode.objects.count(), 2)
        
        
    def test_node_save(self):
        
        node = SimpleNode()
        
        node.save()
        
        self.assertEqual(node.id, SimpleNode.objects.get().id)
        
    
    def test_node_delete(self):
        
        node = SimpleNode.objects.create()
        
        node.delete()
        
        self.assertEqual(len(SimpleNode.objects.filter()), 0)
        self.assertEqual(SimpleNode.objects.count(), 0)
        

    def test_tree_structure(self):
        
        root_node = SimpleNode.objects.create()
        middle_node = SimpleNode.objects.create(parent = root_node)
        bottom_node = SimpleNode.objects.create(parent = middle_node)
        
        fresh_root_node = SimpleNode.objects.get(id = root_node.id)
        fresh_middle_node = SimpleNode.objects.get(id = middle_node.id)
        fresh_bottom_node = SimpleNode.objects.get(id = bottom_node.id)
        
        self.assertEqual(fresh_root_node.depth, 1)
        self.assertEqual(fresh_root_node.path, [root_node.id])
        self.assertEqual(fresh_root_node.ordering, [root_node.id])
        
        self.assertEqual(fresh_middle_node.depth, 2)
        self.assertEqual(fresh_middle_node.path,
            [root_node.id,middle_node.id])
        self.assertEqual(fresh_middle_node.ordering,
            [root_node.id, middle_node.id])
        
        self.assertEqual(fresh_bottom_node.depth, 3)
        self.assertEqual(fresh_bottom_node.path,
            [root_node.id, middle_node.id, bottom_node.id])
        self.assertEqual(fresh_bottom_node.ordering,
            [root_node.id, middle_node.id, bottom_node.id])
        
    
    def test_node_roots(self):
        
        root_node_1 = SimpleNode.objects.create()
        root_node_2 = SimpleNode.objects.create()
        non_root_node_1 = SimpleNode.objects.create(parent = root_node_1)
        non_root_node_2 = SimpleNode.objects.create(parent = root_node_2)
        
        self.assertEqual(len(SimpleNode.objects.roots()), 2)
        self.assertEqual(SimpleNode.objects.roots().count(), 2)
        
        root_node_pks = [root_node_1.pk, root_node_2.pk]
        for node in SimpleNode.objects.roots():
            self.assertTrue(node.pk in root_node_pks)
            
            
    def test_tree_structure_leaves(self):
        
        root_node = SimpleNode.objects.create()
        middle_node = SimpleNode.objects.create(parent = root_node)
        bottom_node_1 = SimpleNode.objects.create(parent = middle_node)
        bottom_node_2 = SimpleNode.objects.create(parent = middle_node)
        bottom_node_3 = SimpleNode.objects.create(parent = middle_node)
        
        self.assertEqual([bottom_node_1.id, bottom_node_2.id, bottom_node_3.id],
            [node.id for node in SimpleNode.objects.leaves()])
        

    def test_tree_structure_branches(self):

        root_node = SimpleNode.objects.create()
        middle_node = SimpleNode.objects.create(parent = root_node)
        bottom_node_1 = SimpleNode.objects.create(parent = middle_node)
        bottom_node_2 = SimpleNode.objects.create(parent = middle_node)
        bottom_node_3 = SimpleNode.objects.create(parent = middle_node)

        self.assertEqual([root_node.id, middle_node.id],
            [node.id for node in SimpleNode.objects.branches()])


    def test_tree_structure_parent(self):
        
        root_node = SimpleNode.objects.create()
        middle_node = SimpleNode.objects.create(parent = root_node)
        bottom_node = SimpleNode.objects.create(parent = middle_node)
    
        self.assertEqual(root_node.parent, None)
        self.assertEqual(middle_node.parent.id, root_node.id)
        self.assertEqual(bottom_node.parent.id, middle_node.id)
        self.assertEqual(bottom_node.parent.parent.id, root_node.id)
        
    
    def test_tree_structure_children(self):
        
        root_node = SimpleNode.objects.create()
        middle_node = SimpleNode.objects.create(parent = root_node)
        bottom_node_1 = SimpleNode.objects.create(parent = middle_node)
        bottom_node_2 = SimpleNode.objects.create(parent = middle_node)
        bottom_node_3 = SimpleNode.objects.create(parent = middle_node)
        
        self.assertEqual(root_node.children.all()[0].id, middle_node.id)
        
        self.assertEqual([node.pk for node in middle_node.children.all()],
            [bottom_node_1.pk, bottom_node_2.pk, bottom_node_3.pk])
        
        self.assertEqual(len(bottom_node_1.children.all()), 0)
        
    
    def test_tree_structure_siblings(self):
        
        root_node = SimpleNode.objects.create()
        middle_node_1 = SimpleNode.objects.create(parent = root_node)
        middle_node_2 = SimpleNode.objects.create(parent = root_node)
        bottom_node_1 = SimpleNode.objects.create(parent = middle_node_1)
        bottom_node_2_1 = SimpleNode.objects.create(parent = middle_node_2)
        bottom_node_2_2 = SimpleNode.objects.create(parent = middle_node_2)
        
        self.assertEqual(len(root_node.siblings()), 0)
        self.assertEqual(root_node.siblings().count(), 0)
        
        self.assertEqual(middle_node_1.siblings()[0].id, middle_node_2.id)
        self.assertEqual(middle_node_2.siblings()[0].id, middle_node_1.id)
        
        self.assertEqual(len(bottom_node_1.siblings()), 0)
        self.assertEqual(bottom_node_1.siblings().count(), 0)
        
        self.assertEqual(bottom_node_2_1.siblings()[0].id, bottom_node_2_2.id)
        self.assertEqual(bottom_node_2_2.siblings()[0].id, bottom_node_2_1.id)
        
        
    def test_tree_structure_descendants(self):
        
        root_node = SimpleNode.objects.create()
        middle_node = SimpleNode.objects.create(parent = root_node)
        bottom_node_1 = SimpleNode.objects.create(parent = middle_node)
        bottom_node_2 = SimpleNode.objects.create(parent = middle_node)
        bottom_node_3 = SimpleNode.objects.create(parent = middle_node)
        
        self.assertEqual([node.pk for node in root_node.descendants()],
            [middle_node.pk, bottom_node_1.pk, bottom_node_2.pk,
             bottom_node_3.pk])
        
        self.assertEqual([node.pk for node in middle_node.descendants()],
            [bottom_node_1.pk, bottom_node_2.pk, bottom_node_3.pk])
        
        self.assertEqual(len(bottom_node_1.descendants()), 0)
        
    
    def test_tree_structure_ancestors(self):
        
        root_node = SimpleNode.objects.create()
        middle_node = SimpleNode.objects.create(parent = root_node)
        bottom_node = SimpleNode.objects.create(parent = middle_node)
        fresh_root_node = SimpleNode.objects.get(id = root_node.id)
        fresh_middle_node = SimpleNode.objects.get(id = middle_node.id)
        fresh_bottom_node = SimpleNode.objects.get(id = bottom_node.id)
        
        self.assertEqual(len(fresh_root_node.ancestors()), 0)
        
        self.assertEqual(fresh_root_node.ancestors().count(), 0)
        
        self.assertEqual(fresh_middle_node.ancestors()[0].id, root_node.id)
        
        self.assertEqual([node.pk for node in fresh_bottom_node.ancestors()],
            [root_node.id, middle_node.id])
        
        
    def test_tree_structure_root(self):
        
        root_node = SimpleNode.objects.create()
        middle_node = SimpleNode.objects.create(parent = root_node)
        bottom_node = SimpleNode.objects.create(parent = middle_node)
        
        fresh_root_node = SimpleNode.objects.get(id = root_node.id)
        fresh_middle_node = SimpleNode.objects.get(id = middle_node.id)
        fresh_bottom_node = SimpleNode.objects.get(id = bottom_node.id)
        
        self.assertEqual(fresh_root_node.root().id, root_node.id)
        self.assertEqual(fresh_middle_node.root().id, root_node.id)
        self.assertEqual(fresh_bottom_node.root().id, root_node.id)
        
        
    def test_tree_structure_intersection(self):
        
        root_node = SimpleNode.objects.create()
        middle_node = SimpleNode.objects.create(parent = root_node)
        bottom_node_1 = SimpleNode.objects.create(parent = middle_node)
        bottom_node_2 = SimpleNode.objects.create(parent = middle_node)
        bottom_node_3 = SimpleNode.objects.create(parent = middle_node)
        
        # We need the path information to get ancestors.
        fresh_bottom_node_2 = SimpleNode.objects.get(id = bottom_node_2.id)
        q = fresh_bottom_node_2.ancestors() & root_node.descendants()
        self.assertEqual(middle_node.id, q[0].id)
        
        
    def test_tree_structure_is_child_of(self):
        
        root_node = SimpleNode.objects.create()
        middle_node = SimpleNode.objects.create(parent = root_node)
        bottom_node_1 = SimpleNode.objects.create(parent = middle_node)
        bottom_node_2 = SimpleNode.objects.create(parent = middle_node)
        bottom_node_3 = SimpleNode.objects.create(parent = middle_node)
        
        self.assertTrue(middle_node.is_child_of(root_node))
        self.assertFalse(bottom_node_1.is_child_of(root_node))
        
        
    def test_tree_structure_is_parent_of(self):
        
        root_node = SimpleNode.objects.create()
        middle_node = SimpleNode.objects.create(parent = root_node)
        bottom_node_1 = SimpleNode.objects.create(parent = middle_node)
        bottom_node_2 = SimpleNode.objects.create(parent = middle_node)
        bottom_node_3 = SimpleNode.objects.create(parent = middle_node)
        
        self.assertTrue(root_node.is_parent_of(middle_node))
        self.assertFalse(root_node.is_parent_of(bottom_node_1))
        
        
    def test_tree_structure_is_sibling_of(self):
        
        root_node = SimpleNode.objects.create()
        another_root_node = SimpleNode.objects.create()
        middle_node = SimpleNode.objects.create(parent = root_node)
        bottom_node_1 = SimpleNode.objects.create(parent = middle_node)
        bottom_node_2 = SimpleNode.objects.create(parent = middle_node)
        bottom_node_3 = SimpleNode.objects.create(parent = middle_node)
        
        self.assertTrue(bottom_node_1.is_sibling_of(bottom_node_2))
        self.assertTrue(bottom_node_2.is_sibling_of(bottom_node_1))
        
        # Ensure edge case when parents are None.
        self.assertTrue(root_node.is_sibling_of(another_root_node))
                        
        self.assertFalse(bottom_node_1.is_sibling_of(middle_node))
        self.assertFalse(bottom_node_1.is_sibling_of(root_node))
        
        # Ensure edge case when compared to self.
        self.assertFalse(bottom_node_1.is_sibling_of(bottom_node_1))
        self.assertFalse(middle_node.is_sibling_of(middle_node))
        
        
    def test_tree_structure_is_descendant_of(self):
        
        root_node = SimpleNode.objects.create()
        middle_node = SimpleNode.objects.create(parent = root_node)
        bottom_node = SimpleNode.objects.create(parent = middle_node)
        
        fresh_root_node = SimpleNode.objects.get(id = root_node.id)
        fresh_middle_node = SimpleNode.objects.get(id = middle_node.id)
        fresh_bottom_node = SimpleNode.objects.get(id = bottom_node.id)
        
        self.assertTrue(fresh_middle_node.is_descendant_of(fresh_root_node))
        self.assertFalse(fresh_root_node.is_descendant_of(fresh_middle_node))
        
        self.assertTrue(fresh_bottom_node.is_descendant_of(fresh_root_node))
        self.assertFalse(fresh_root_node.is_descendant_of(fresh_bottom_node))
        
        self.assertTrue(fresh_bottom_node.is_descendant_of(fresh_middle_node))
        self.assertFalse(fresh_middle_node.is_descendant_of(fresh_bottom_node))
        
        self.assertFalse(fresh_root_node.is_descendant_of(fresh_root_node))
        self.assertFalse(fresh_middle_node.is_descendant_of(fresh_middle_node))
        self.assertFalse(fresh_bottom_node.is_descendant_of(fresh_bottom_node))
        
        
    def test_tree_structure_is_descendant_of_none(self):
        
        root_node = SimpleNode.objects.create()
        middle_node = SimpleNode.objects.create(parent = root_node)
        
        fresh_root_node = SimpleNode.objects.get(id = root_node.id)
        fresh_middle_node = SimpleNode.objects.get(id = middle_node.id)
        
        self.assertTrue(fresh_middle_node.is_descendant_of(fresh_root_node))
        
        self.assertFalse(fresh_middle_node.is_descendant_of(None))
        
        
    def test_tree_structure_is_ancestor_of(self):
        
        root_node = SimpleNode.objects.create()
        middle_node = SimpleNode.objects.create(parent = root_node)
        bottom_node = SimpleNode.objects.create(parent = middle_node)
        
        fresh_root_node = SimpleNode.objects.get(id = root_node.id)
        fresh_middle_node = SimpleNode.objects.get(id = middle_node.id)
        fresh_bottom_node = SimpleNode.objects.get(id = bottom_node.id)
        
        self.assertFalse(fresh_middle_node.is_ancestor_of(fresh_root_node))
        self.assertTrue(fresh_root_node.is_ancestor_of(fresh_middle_node))
        
        self.assertFalse(fresh_bottom_node.is_ancestor_of(fresh_root_node))
        self.assertTrue(fresh_root_node.is_ancestor_of(fresh_bottom_node))
        
        self.assertFalse(fresh_bottom_node.is_ancestor_of(fresh_middle_node))
        self.assertTrue(fresh_middle_node.is_ancestor_of(fresh_bottom_node))
        
        self.assertFalse(fresh_root_node.is_ancestor_of(fresh_root_node))
        self.assertFalse(fresh_middle_node.is_ancestor_of(fresh_middle_node))
        self.assertFalse(fresh_bottom_node.is_ancestor_of(fresh_bottom_node))
        
        
    def test_tree_structure_is_ancestor_of_none(self):
        
        root_node = SimpleNode.objects.create()
        middle_node = SimpleNode.objects.create(parent = root_node)
        
        fresh_root_node = SimpleNode.objects.get(id = root_node.id)
        fresh_middle_node = SimpleNode.objects.get(id = middle_node.id)
        
        self.assertTrue(fresh_root_node.is_ancestor_of(fresh_middle_node))
        self.assertFalse(fresh_root_node.is_ancestor_of(None))
        
        
    def test_tree_structure_is_leaf(self):
        
        root_node = SimpleNode.objects.create()
        middle_node = SimpleNode.objects.create(parent = root_node)
        bottom_node_1 = SimpleNode.objects.create(parent = middle_node)
        bottom_node_2 = SimpleNode.objects.create(parent = middle_node)
        bottom_node_3 = SimpleNode.objects.create(parent = middle_node)
        
        self.assertFalse(root_node.is_leaf())
        self.assertFalse(middle_node.is_leaf())
        self.assertTrue(bottom_node_1.is_leaf())
        self.assertTrue(bottom_node_2.is_leaf())
        self.assertTrue(bottom_node_3.is_leaf())
        

    def test_tree_structure_is_branch(self):

        root_node = SimpleNode.objects.create()
        middle_node = SimpleNode.objects.create(parent = root_node)
        bottom_node_1 = SimpleNode.objects.create(parent = middle_node)
        bottom_node_2 = SimpleNode.objects.create(parent = middle_node)
        bottom_node_3 = SimpleNode.objects.create(parent = middle_node)

        self.assertTrue(root_node.is_branch())
        self.assertTrue(middle_node.is_branch())
        self.assertFalse(bottom_node_1.is_branch())
        self.assertFalse(bottom_node_2.is_branch())
        self.assertFalse(bottom_node_3.is_branch())


    def test_tree_attribute_path(self):

        root_node = SimpleNamedNode.objects.create(name = 'root')
        middle_node = SimpleNamedNode.objects.create(parent = root_node,
            name = 'middle')
        bottom_node = SimpleNamedNode.objects.create(parent = middle_node,
            name = 'bottom')

        fresh_root_node = SimpleNamedNode.objects.get(name = 'root')
        fresh_middle_node = SimpleNamedNode.objects.get(name = 'middle')
        fresh_bottom_node = SimpleNamedNode.objects.get(name = 'bottom')

        self.assertEqual(['root', ], fresh_root_node.attribute_path('name'))
        self.assertEqual(['root', 'middle', ],
            fresh_middle_node.attribute_path('name'))
        self.assertEqual(['root', 'middle', 'bottom', ],
            fresh_bottom_node.attribute_path('name'))

        self.assertEqual(['foo', ], fresh_root_node.attribute_path('bar',
            missing = 'foo'))

        def custom_visitor(node, attribute):
            value = getattr(node, attribute, None)
            if value == 'middle':
                return 'foo'
            if value == 'bottom':
                return None
            return value

        self.assertEqual(['root', 'foo', 'bar', ],
            fresh_bottom_node.attribute_path('name', missing = 'bar',
                visitor = custom_visitor))


    def test_tree_structure_as_tree(self):

        root_node = OrderedNamedNode.objects.create(name = 'root')
        middle_node = OrderedNamedNode.objects.create(parent = root_node,
            name = 'middle')
        bottom_node_3 = OrderedNamedNode.objects.create(parent = middle_node,
            name = 'bottom 3')
        bottom_node_1 = OrderedNamedNode.objects.create(parent = middle_node,
            name = 'bottom 1')
        bottom_node_2 = OrderedNamedNode.objects.create(parent = middle_node,
            name = 'bottom 2')
        another_root_node = OrderedNamedNode.objects.create(name = 'root other')

        fresh_root_node = OrderedNamedNode.objects.get(name = 'root')
        fresh_middle_node = OrderedNamedNode.objects.get(name = 'middle')
        fresh_bottom_node_1 = OrderedNamedNode.objects.get(name = 'bottom 1')
        fresh_bottom_node_2 = OrderedNamedNode.objects.get(name = 'bottom 2')
        fresh_bottom_node_3 = OrderedNamedNode.objects.get(name = 'bottom 3')
        fresh_another_root_node = OrderedNamedNode.objects.get(name = 'root other')

        # get the forest
        tree = OrderedNamedNode.objects.as_tree()
        self.assertEqual(len(tree), 2)
        self.assertEqual(len(tree[0]['children']), 1)
        self.assertEqual(len(tree[1]['children']), 0)
        self.assertEqual(tree[0]['children'][0]['children'][1]['node'].id,
            fresh_bottom_node_2.id)

        # get a specific tree
        middle_tree = fresh_middle_node.as_tree()
        self.assertEqual(middle_tree['node'].id, middle_node.id)
        self.assertFalse(middle_tree['leaf'])
        self.assertTrue(middle_tree['branch'])
        self.assertEqual(middle_tree['depth'], 2)
        self.assertEqual(middle_tree['ordering'], ['root', 'middle', ])
        self.assertEqual(middle_tree['path'],
            [str(root_node.id), str(middle_node.id), ])
        self.assertEqual(len(middle_tree['children']), 3)
        self.assertEqual(middle_tree['children'][1]['node'].id,
            fresh_bottom_node_2.id)


    def test_tree_structure_as_tree_custom(self):

        root_node = OrderedNamedNode.objects.create(name = 'root')
        middle_node = OrderedNamedNode.objects.create(parent = root_node,
            name = 'middle')
        bottom_node_3 = OrderedNamedNode.objects.create(parent = middle_node,
            name = 'bottom 3')
        bottom_node_1 = OrderedNamedNode.objects.create(parent = middle_node,
            name = 'bottom 1')
        bottom_node_2 = OrderedNamedNode.objects.create(parent = middle_node,
            name = 'bottom 2')
        another_root_node = OrderedNamedNode.objects.create(name = 'root other')

        fresh_root_node = OrderedNamedNode.objects.get(name = 'root')
        fresh_middle_node = OrderedNamedNode.objects.get(name = 'middle')
        fresh_bottom_node_1 = OrderedNamedNode.objects.get(name = 'bottom 1')
        fresh_bottom_node_2 = OrderedNamedNode.objects.get(name = 'bottom 2')
        fresh_bottom_node_3 = OrderedNamedNode.objects.get(name = 'bottom 3')
        fresh_another_root_node = OrderedNamedNode.objects.get(name = 'root other')

        def custom_visitor(manager, node):
            tree = manager._default_node_visitor(node)
            tree['person'] = tree['node']
            del tree['node']
            return tree

        def custom_children(manager, node, visitor, children):
            if node.name == 'bottom 2':
                return {}
            return { 'offspring' : [ child.as_tree(
                visitor = visitor, children = children) for child in \
                node.children.exclude(name = 'bottom 2') ] }

        # get the forest
        tree = OrderedNamedNode.objects.as_tree(visitor = custom_visitor,
            children = custom_children)
        self.assertEqual(len(tree), 2)
        self.assertEqual(len(tree[0]['offspring']), 1)
        self.assertEqual(len(tree[1]['offspring']), 0)
        self.assertEqual(tree[0]['offspring'][0]['offspring'][1]['person'].id,
            fresh_bottom_node_3.id)

        # get a specific tree
        middle_tree = fresh_middle_node.as_tree(visitor = custom_visitor,
            children = custom_children)
        self.assertEqual(middle_tree['person'].id, middle_node.id)
        self.assertFalse(middle_tree['leaf'])
        self.assertTrue(middle_tree['branch'])
        self.assertEqual(middle_tree['depth'], 2)
        self.assertEqual(middle_tree['ordering'], ['root', 'middle', ])
        self.assertEqual(middle_tree['path'],
            [str(root_node.id), str(middle_node.id), ])
        self.assertEqual(len(middle_tree['offspring']), 2)
        self.assertEqual(middle_tree['offspring'][1]['person'].id,
            fresh_bottom_node_3.id)


    def test_tree_drilldown(self):

        # check empty forest (no roots, empty path)
        self.assertRaises(SimpleNamedNode.DoesNotExist,
            lambda: SimpleNamedNode.objects.drilldown(('name',),[]))

        root_node = SimpleNamedNode.objects.create(name = 'root')
        middle_node = SimpleNamedNode.objects.create(parent = root_node,
            name = 'middle')
        bottom_node = SimpleNamedNode.objects.create(parent = middle_node,
            name = 'bottom')

        fresh_root_node = SimpleNamedNode.objects.get(name = 'root')
        fresh_middle_node = SimpleNamedNode.objects.get(name = 'middle')
        fresh_bottom_node = SimpleNamedNode.objects.get(name = 'bottom')

        # check missing path component
        self.assertRaises(SimpleNamedNode.DoesNotExist,
            lambda: SimpleNamedNode.objects.drilldown(('name',),
                [('root',),('xxx')]))

        # check missing root component
        self.assertRaises(SimpleNamedNode.DoesNotExist,
            lambda: SimpleNamedNode.objects.drilldown(('name',),
                [('xxx',),('xxx')]))

        # check success
        self.assertEqual(fresh_bottom_node, SimpleNamedNode.objects.drilldown(
            ('name', ), [('root',), ('middle',), ('bottom',)]))

        # check empty path success
        self.assertEqual(fresh_root_node, SimpleNamedNode.objects.drilldown(
                ('name', ), []))

        # check extraneous path component
        self.assertRaises(SimpleNamedNode.DoesNotExist,
            lambda: SimpleNamedNode.objects.drilldown(('name',),
                [('root',), ('middle',), ('bottom',), ('xxx',)]))


    def test_tree_drilldown_complex_filtering(self):

        root_node = ValueNamedNode.objects.create(name = 'root', v = 5)
        middle_node = ValueNamedNode.objects.create(parent = root_node,
            name = 'middle', v = 5)
        bottom_node_1 = ValueNamedNode.objects.create(parent = middle_node,
            name = 'xxx bottom 1', v = 7)
        bottom_node_2 = ValueNamedNode.objects.create(parent = middle_node,
            name = 'bottom 2', v = 1)
        bottom_node_3 = ValueNamedNode.objects.create(parent = middle_node,
            name = 'bottom 3', v = 6)

        fresh_root_node = ValueNamedNode.objects.get(name = 'root')
        fresh_middle_node = ValueNamedNode.objects.get(name = 'middle')
        fresh_bottom_node_1 = ValueNamedNode.objects.get(name = 'xxx bottom 1')
        fresh_bottom_node_2 = ValueNamedNode.objects.get(name = 'bottom 2')
        fresh_bottom_node_3 = ValueNamedNode.objects.get(name = 'bottom 3')

        self.assertEqual(fresh_bottom_node_3, ValueNamedNode.objects.drilldown(
            ('name__startswith', 'v__gte'),
            [('root', 5), ('middle', 5), ('bottom', 5)]))


    def test_node_delete_pharaoh(self):
        
        root_node = SimpleNode.objects.create()
        middle_node = SimpleNode.objects.create(parent = root_node)
        bottom_node_1 = SimpleNode.objects.create(parent = middle_node)
        bottom_node_2 = SimpleNode.objects.create(parent = middle_node)
        bottom_node_3 = SimpleNode.objects.create(parent = middle_node)
        
        middle_node.delete()
        
        self.assertEqual(len(SimpleNode.objects.all()), 1)
        self.assertEqual(SimpleNode.objects.count(), 1)
        self.assertEqual(SimpleNode.objects.get().id, root_node.id)
    
    
    def test_node_delete_grandmother(self):
        
        root_node = SimpleNode.objects.create()
        middle_node = SimpleNode.objects.create(parent = root_node)
        bottom_node_1 = SimpleNode.objects.create(parent = middle_node)
        bottom_node_2 = SimpleNode.objects.create(parent = middle_node)
        bottom_node_3 = SimpleNode.objects.create(parent = middle_node)
        
        middle_node.delete(
            method = SimpleNode.objects.DELETE_METHOD_GRANDMOTHER)
        
        self.assertEqual(len(SimpleNode.objects.all()), 4)
        self.assertEqual(SimpleNode.objects.count(), 4)
        self.assertEqual([node.id for node in SimpleNode.objects.all()],
            [root_node.id, bottom_node_1.id, bottom_node_2.id,
             bottom_node_3.id])
        self.assertEqual(len(root_node.children.all()), 3)
        self.assertEqual(root_node.children.count(), 3)
        self.assertEqual([node.depth for node in root_node.children.all()],
            [2,2,2])
        
    
    def test_node_delete_monarchy(self):
        
        root_node = SimpleNode.objects.create()
        middle_node = SimpleNode.objects.create(parent = root_node)
        bottom_node_1 = SimpleNode.objects.create(parent = middle_node)
        bottom_node_2 = SimpleNode.objects.create(parent = middle_node)
        bottom_node_3 = SimpleNode.objects.create(parent = middle_node)
        
        middle_node.delete(method = SimpleNode.objects.DELETE_METHOD_MONARCHY)
        
        fresh_bottom_node_1 = SimpleNode.objects.get(id = bottom_node_1.id)
        
        self.assertEqual(len(SimpleNode.objects.all()), 4)
        self.assertEqual(SimpleNode.objects.count(), 4)
        self.assertEqual([node.id for node in SimpleNode.objects.all()],
            [root_node.id, bottom_node_1.id, bottom_node_2.id,
             bottom_node_3.id])
        self.assertEqual(len(root_node.children.all()), 1)
        self.assertEqual(root_node.children.count(), 1)
        self.assertEqual([node.depth for node in root_node.children.all()],[2])
        
        self.assertEqual(fresh_bottom_node_1.depth, 2)
        self.assertEqual(fresh_bottom_node_1.children.count(), 2)
        self.assertEqual(len(fresh_bottom_node_1.children.all()), 2)
        self.assertEqual([3,3],
            [node.depth for node in fresh_bottom_node_1.children.all()])
        
        
    def test_node_delete_none(self):
        
        root_node = NoneDeleteNode.objects.create()
        middle_node = NoneDeleteNode.objects.create(parent = root_node)
        bottom_node_1 = NoneDeleteNode.objects.create(parent = middle_node)
        bottom_node_2 = NoneDeleteNode.objects.create(parent = middle_node)
        bottom_node_3 = NoneDeleteNode.objects.create(parent = middle_node)
        
        middle_node.delete()
        
        self.assertEqual(len(NoneDeleteNode.objects.all()), 1)
        self.assertEqual(NoneDeleteNode.objects.count(), 1)
        self.assertEqual(NoneDeleteNode.objects.get().id, root_node.id)
        
        
    def test_node_move(self):
        
        root_node = SimpleNode.objects.create()
        middle_node = SimpleNode.objects.create(parent = root_node)
        bottom_node_1 = SimpleNode.objects.create(parent = middle_node)
        bottom_node_2 = SimpleNode.objects.create(parent = middle_node)
        bottom_node_3 = SimpleNode.objects.create(parent = middle_node)
        
        fresh_bottom_node_3 = SimpleNode.objects.get(id = bottom_node_3.id)
        
        self.assertEqual(fresh_bottom_node_3.depth, 3)
        
        bottom_node_3.move(root_node, position = lambda node, destination: None,
            save = True)
        
        fresh_bottom_node_3 = SimpleNode.objects.get(id = bottom_node_3.id)
        
        self.assertEqual(fresh_bottom_node_3.depth, 2)
        
        
class SimpleNodeErrorsTest(TestCase):
    
    def test_node_parameters_parent_1(self):
        
        # _cte_node_parent points to a non-existing field.
        self.assertRaises(ImproperlyConfigured,
            BadParameter_parent_1_Node.objects.create)
    
    
    def test_node_parameters_parent_2(self):
        
        # Parent Foreign Key points to different CTENode Model.
        self.assertRaises(ImproperlyConfigured,
            BadParameter_parent_2_Node.objects.create)
        
        
    def test_node_parameters_parent_3(self):
        
        # Parent Foreign Key points to arbitrary Model.
        self.assertRaises(ImproperlyConfigured,
            BadParameter_parent_3_Node.objects.create)
        
        
    def test_node_parameters_parent_4(self):
        
        # Parent Foreign Key missing.
        self.assertRaises(ImproperlyConfigured,
            BadParameter_parent_4_Node.objects.create)
        
        
    def test_node_parameters_traversal(self):
        
        self.assertRaises(ImproperlyConfigured,
            BadParameter_traversal_Node.objects.create)
        
        
    def test_node_parameters_delete(self):
        
        self.assertRaises(ImproperlyConfigured,
            BadParameter_delete_Node.objects.create)
        
            
    def test_node_virtual_fields(self):
        
        root_node = SimpleNode.objects.create()
        
        read_path = lambda node: node.path
        
        self.assertRaises(AttributeError, read_path, root_node)
        self.assertRaises(FieldError, root_node.ancestors)
    
        
class SimpleNodeUsageTest(TestCase):
    
    def test_node_usage(self):
        
        root_node = SimpleNode.objects.create()
        middle_node = SimpleNode.objects.create(parent = root_node)
        bottom_node_1 = SimpleNode.objects.create(parent = middle_node)
        bottom_node_2 = SimpleNode.objects.create(parent = middle_node)
        bottom_node_3 = SimpleNode.objects.create(parent = middle_node)
        
        root_node_user = SimpleNodeUser.objects.create(node = root_node)
        
        self.assertEqual(SimpleNodeUser.objects.get().node.id, root_node.id)
    
    
class SimpleNamedNodeTest(TestCase):
    
    def test_node_creation(self):
        
        node = SimpleNamedNode.objects.create(name = 'root')
        
        self.assertEqual(SimpleNamedNode.objects.get().name, node.name)

        
    def test_user_creation(self):
        
        node = SimpleNamedNode.objects.create(name = 'root')
        user = SimpleNamedNodeUser.objects.create(node = node,
            name = 'root user')
        
        self.assertEqual(user.node.name, 'root')
        
        
    def test_ordering(self):
        
        root_node = SimpleNamedNode.objects.create(name = 'root')
        middle_node = SimpleNamedNode.objects.create(parent = root_node,
            name = 'middle')
        
        # Create these in mixed order to test ordering by name below.
        bottom_node_2 = SimpleNamedNode.objects.create(parent = middle_node,
            name = 'bottom 2')
        bottom_node_3 = SimpleNamedNode.objects.create(parent = middle_node,
            name = 'bottom 3')
        bottom_node_1 = SimpleNamedNode.objects.create(parent = middle_node,
            name = 'bottom 1')
        
        # Order should be by primary key, not name.
        node_names = [node.name for node in SimpleNamedNode.objects.all()]
        self.assertEqual(node_names,
            ['root', 'middle', 'bottom 2', 'bottom 3', 'bottom 1'])
        
        # But if we override ordering, we can get back to flat name space.
        flat_node_names = [node.name for node in \
            SimpleNamedNode.objects.all().order_by('name')]
        self.assertEqual(flat_node_names,
            ['bottom 1', 'bottom 2', 'bottom 3', 'middle', 'root'])
        
        
    def test_node_filter_chaining(self):
        
        root_node = SimpleNamedNode.objects.create(name = 'root')
        middle_node = SimpleNamedNode.objects.create(parent = root_node,
            name = 'middle')
        bottom_node_1 = SimpleNamedNode.objects.create(parent = middle_node,
            name = 'bottom 1')
        bottom_node_2 = SimpleNamedNode.objects.create(parent = middle_node,
            name = 'bottom 2')
        bottom_node_3 = SimpleNamedNode.objects.create(parent = middle_node,
            name = 'bottom 3')
        
        self.assertEqual('bottom 1',
            SimpleNamedNode.objects.filter(id__gt = 1).exclude(
                name = 'bottom 3').filter(
                    name__in = ['bottom 3', 'bottom 1'])[0].name)
        
        
class OrderedNamedNodeTest(TestCase):
    
    def test_node_creation(self):
        
        node = OrderedNamedNode.objects.create(name = 'root')
        fresh_node = OrderedNamedNode.objects.get()
        
        self.assertEqual(fresh_node.ordering, [node.name])
        
    
    def test_simple_ordering(self):
        
        root_node = OrderedNamedNode.objects.create(name = 'root')
        middle_node = OrderedNamedNode.objects.create(parent = root_node,
            name = 'middle')
        
        # Create these in mixed order to test ordering by name below.
        bottom_node_2 = OrderedNamedNode.objects.create(parent = middle_node,
            name = 'bottom 2')
        bottom_node_3 = OrderedNamedNode.objects.create(parent = middle_node,
            name = 'bottom 3')
        bottom_node_1 = OrderedNamedNode.objects.create(parent = middle_node,
            name = 'bottom 1')
        
        # Order should be by path name, not primary key.
        node_names = [node.name for node in OrderedNamedNode.objects.all()]
        self.assertEqual(['root', 'middle', 'bottom 1', 'bottom 2', 'bottom 3'],
            node_names)
        
        # But if we override ordering, we can get back to flat name space.
        flat_node_names = [node.name for node in \
            OrderedNamedNode.objects.all().order_by('name')]
        self.assertEqual(['bottom 1', 'bottom 2', 'bottom 3', 'middle', 'root'],
            flat_node_names)
        
    
class DFSOrderedNodeTest(TestCase):
    
    def test_ordering_dfs(self):
        
        root_node = DFSOrderedNode.objects.create(v = 1)
        # The following two have different v values, but created in the
        # opposite order from which we are ordering.
        middle_node_1 = DFSOrderedNode.objects.create(parent = root_node,
            v = 5)
        middle_node_2 = DFSOrderedNode.objects.create(parent = root_node,
            v = 4)
        
        # The following two have the same v value.
        bottom_node_1_1 = DFSOrderedNode.objects.create(
            parent = middle_node_1, v = 3)
        bottom_node_1_2 = DFSOrderedNode.objects.create(
            parent = middle_node_1, v = 3)
        
        # The following have different v values, but created in 'reverse' order.
        bottom_node_2_1 = DFSOrderedNode.objects.create(
            parent = middle_node_2, v = 5)
        bottom_node_2_2 = DFSOrderedNode.objects.create(
            parent = middle_node_2, v = 4)
        
        expected_order = [root_node.id, middle_node_2.id, bottom_node_2_2.id,
            bottom_node_2_1.id, middle_node_1.id, bottom_node_1_1.id,
            bottom_node_1_2.id]
        
        self.assertEqual(expected_order,
            [node.id for node in DFSOrderedNode.objects.all()])
        
        
class BFSOrderedNodeTest(TestCase):
    
    def test_ordering_bfs(self):
        
        root_node = BFSOrderedNode.objects.create(v = 1)
        # The following two have different v values, but created in the
        # opposite order from which we are ordering.
        middle_node_1 = BFSOrderedNode.objects.create(parent = root_node,
            v = 5)
        middle_node_2 = BFSOrderedNode.objects.create(parent = root_node,
            v = 4)
        
        # The following two have the same v value.
        bottom_node_1_1 = BFSOrderedNode.objects.create(
            parent = middle_node_1, v = 3)
        bottom_node_1_2 = BFSOrderedNode.objects.create(
            parent = middle_node_1, v = 3)
        
        # The following have different v values, but created in 'reverse' order.
        bottom_node_2_1 = BFSOrderedNode.objects.create(
            parent = middle_node_2, v = 5)
        bottom_node_2_2 = BFSOrderedNode.objects.create(
            parent = middle_node_2, v = 4)
        
        expected_order = [root_node.id, middle_node_2.id, middle_node_1.id,
            bottom_node_2_2.id, bottom_node_2_1.id, bottom_node_1_1.id,
            bottom_node_1_2.id]
        
        self.assertEqual(expected_order,
            [node.id for node in BFSOrderedNode.objects.all()])
        

class TraversalNodeTest(TestCase):
    
    def test_none_traversal_parameter(self):
        
        root_node = NoneTraversalNode.objects.create(v = 1)
        # The following two have different v values, but created in the
        # opposite order from which we are ordering.
        middle_node_1 = NoneTraversalNode.objects.create(parent = root_node,
            v = 5)
        middle_node_2 = NoneTraversalNode.objects.create(parent = root_node,
            v = 4)
        
        # The following two have the same v value.
        bottom_node_1_1 = NoneTraversalNode.objects.create(
            parent = middle_node_1, v = 3)
        bottom_node_1_2 = NoneTraversalNode.objects.create(
            parent = middle_node_1, v = 3)
        
        # The following have different v values, but created in 'reverse' order.
        bottom_node_2_1 = NoneTraversalNode.objects.create(
            parent = middle_node_2, v = 5)
        bottom_node_2_2 = NoneTraversalNode.objects.create(
            parent = middle_node_2, v = 4)
        
        expected_order = [root_node.id, middle_node_2.id, bottom_node_2_2.id,
            bottom_node_2_1.id, middle_node_1.id, bottom_node_1_1.id,
            bottom_node_1_2.id]
        
        self.assertEqual(expected_order,
            [node.id for node in NoneTraversalNode.objects.all()])
        
        
class TypeCoercionNodeTest(TestCase):
    
    def test_type_coercion(self):
        
        # Note: this tests in DFS. We will order on a VARCHAR, which will be
        # automatically cast into TEXT, and also on an int, which we will have
        # to explicitly cast into TEXT in order to combine with the VARCHAR.
        
        root_node = TypeCoercionNode.objects.create(v = 1, name = '')
        # The following two have different v values, but created in the
        # opposite order from which we are ordering.
        middle_node_1 = TypeCoercionNode.objects.create(parent = root_node,
            v = 5, name = 'foo')
        middle_node_2 = TypeCoercionNode.objects.create(parent = root_node,
            v = 4, name = 'foo')
        
        # The following two have the same v value.
        bottom_node_1_1 = TypeCoercionNode.objects.create(
            parent = middle_node_1, v = 3, name = 'b')
        bottom_node_1_2 = TypeCoercionNode.objects.create(
            parent = middle_node_1, v = 3, name = 'a')
        
        # The following two have the same v and name values, so the order in
        # they will be returned is defined by the database.
        bottom_node_2_1 = TypeCoercionNode.objects.create(
            parent = middle_node_2, v = 4, name = 'foo')
        bottom_node_2_2 = TypeCoercionNode.objects.create(
            parent = middle_node_2, v = 4, name = 'foo')
        
        expected_order = [root_node.id, middle_node_2.id, bottom_node_2_2.id,
            bottom_node_2_1.id, middle_node_1.id, bottom_node_1_2.id,
            bottom_node_1_1.id]
        
        self.assertEqual(expected_order,
            [node.id for node in TypeCoercionNode.objects.all()])
    
    
class TypeCombinationNodeTest(TestCase):
    
    def test_type_combination(self):
        
        # Note: this tests in BFS.
        
        root_node = TypeCombinationNode.objects.create(v1 = 1, v2 = 3.2)
        
        # The following two have different v1 values, but created in the
        # opposite order from which we are ordering.
        middle_node_1 = TypeCombinationNode.objects.create(parent = root_node,
            v1 = 5, v2 = 3.7)
        middle_node_2 = TypeCombinationNode.objects.create(parent = root_node,
            v1 = 4, v2 = 8.9)
        
        # The following two have the same v1 value.
        bottom_node_1_1 = TypeCombinationNode.objects.create(
            parent = middle_node_1, v1 = 3, v2 = 1.5)
        bottom_node_1_2 = TypeCombinationNode.objects.create(
            parent = middle_node_1, v1 = 3, v2 = 1.4)
        
        # The following two have the same v1 and v2 values, so the order in
        # they will be returned is defined by the database.
        bottom_node_2_1 = TypeCombinationNode.objects.create(
            parent = middle_node_2, v1 = 4, v2 = 4)
        bottom_node_2_2 = TypeCombinationNode.objects.create(
            parent = middle_node_2, v1 = 4, v2 = 5)
        
        expected_order = [root_node.id, middle_node_2.id, middle_node_1.id,
            bottom_node_2_1.id, bottom_node_2_2.id, bottom_node_1_2.id,
            bottom_node_1_1.id]
        
        self.assertEqual(expected_order,
            [node.id for node in TypeCombinationNode.objects.all()])
        
        
class ExoticTypeNodeTest(TestCase):
    
    def test_exotic_type(self):
        
        root_node = ExoticTypeNode.objects.create(v = date(1982,9,26))
        # The following two have different v values, but created in the
        # opposite order from which we are ordering.
        middle_node_1 = ExoticTypeNode.objects.create(parent = root_node,
            v = date(2006,7,7))
        middle_node_2 = ExoticTypeNode.objects.create(parent = root_node,
            v = date(1946,1,6))
        
        # The following two have the same v value.
        bottom_node_1_1 = ExoticTypeNode.objects.create(
            parent = middle_node_1, v = date(1924,11,20))
        bottom_node_1_2 = ExoticTypeNode.objects.create(
            parent = middle_node_1, v = date(1924,11,20))
        
        # The following have different v values, but created in 'reverse' order.
        bottom_node_2_1 = ExoticTypeNode.objects.create(
            parent = middle_node_2, v = date(1987,10,20))
        bottom_node_2_2 = ExoticTypeNode.objects.create(
            parent = middle_node_2, v = date(1903,4,25))
        
        expected_order = [root_node.id, middle_node_2.id, bottom_node_2_2.id,
            bottom_node_2_1.id, middle_node_1.id, bottom_node_1_1.id,
            bottom_node_1_2.id]
        
        self.assertEqual(expected_order,
            [node.id for node in ExoticTypeNode.objects.all()])
    
    
class DBTypeNodeTest(TestCase):
    
    sorted_uuids = [
        UUID('24f8aab3-43b1-4359-bbe7-532e33aa8114'),
        UUID('4761ac94-9435-4fe0-9644-3e0b0da4e808'),
        UUID('563a973c-74da-46f9-8be7-70b9b60ca47a'),
        UUID('6309a02a-fec0-48c3-a93d-4a06a80de78b'),
        UUID('75025ae9-fd6d-41d2-8cd3-c34c49267d6d'),
        UUID('78e66b6f-f59c-42df-b20e-ea9855329bea')
    ]
    
    
    def test_ensure_sorted_uuids(self):
        
        previous = None
        for u in self.sorted_uuids:
            if previous is None:
                previous = u
            else:
                self.assertTrue(previous < u)
        
        
    def test_db_type(self):
        
        root_node = DBTypeNode.objects.create(v = self.sorted_uuids[0])
        # The following two have different v values, but created in the
        # opposite order from which we are ordering.
        middle_node_1 = DBTypeNode.objects.create(parent = root_node,
            v = self.sorted_uuids[2])
        middle_node_2 = DBTypeNode.objects.create(parent = root_node,
            v = self.sorted_uuids[1])
        
        # The following two have the same v value.
        bottom_node_1_1 = DBTypeNode.objects.create(
            parent = middle_node_1, v = self.sorted_uuids[3])
        bottom_node_1_2 = DBTypeNode.objects.create(
            parent = middle_node_1, v = self.sorted_uuids[3])
        
        # The following have different v values, but created in 'reverse' order.
        bottom_node_2_1 = DBTypeNode.objects.create(
            parent = middle_node_2, v = self.sorted_uuids[5])
        bottom_node_2_2 = DBTypeNode.objects.create(
            parent = middle_node_2, v = self.sorted_uuids[4])
        
        expected_order = [root_node.id, middle_node_2.id, bottom_node_2_2.id,
            bottom_node_2_1.id, middle_node_1.id, bottom_node_1_1.id,
            bottom_node_1_2.id]
        
        self.assertEqual(expected_order,
            [node.id for node in DBTypeNode.objects.all()])
        
        
    def test_db_type_path(self):
        
        root_node = DBTypeNode.objects.create(v = self.sorted_uuids[0])
        # The following two have different v values, but created in the
        # opposite order from which we are ordering.
        middle_node_1 = DBTypeNode.objects.create(parent = root_node,
            v = self.sorted_uuids[2])
        middle_node_2 = DBTypeNode.objects.create(parent = root_node,
            v = self.sorted_uuids[1])
        
        fresh_middle_node_1 = DBTypeNode.objects.get(id = middle_node_1.id)
        
        self.assertEqual(fresh_middle_node_1.ancestors()[0], root_node)
        
        
    def test_tree_structure_is_child_of(self):
        
        root_node = DBTypeNode.objects.create()
        middle_node = DBTypeNode.objects.create(parent = root_node)
        bottom_node_1 = DBTypeNode.objects.create(parent = middle_node)
        bottom_node_2 = DBTypeNode.objects.create(parent = middle_node)
        bottom_node_3 = DBTypeNode.objects.create(parent = middle_node)
        
        fresh_middle_node = DBTypeNode.objects.get(id = middle_node.id)
        fresh_bottom_node_1 = DBTypeNode.objects.get(id = bottom_node_1.id)
        
        self.assertTrue(fresh_middle_node.is_child_of(root_node))
        self.assertFalse(fresh_bottom_node_1.is_child_of(root_node))
    
    
class CustomPrimaryKeyNodeTest(TestCase):
        
    def test_tree_structure_is_child_of(self):
        
        # Ensure string-based path encoding works.
        
        root_node = CustomPrimaryKeyNode.objects.create(id = 'root')
        middle_node = CustomPrimaryKeyNode.objects.create(id = 'middle',
            parent = root_node)
        bottom_node_1 = CustomPrimaryKeyNode.objects.create(id = 'bottom 1',
            parent = middle_node)
        bottom_node_2 = CustomPrimaryKeyNode.objects.create(id = 'bottom 2',
            parent = middle_node)
        bottom_node_3 = CustomPrimaryKeyNode.objects.create(id = 'bottom 3',
            parent = middle_node)
        
        fresh_middle_node = CustomPrimaryKeyNode.objects.get(
            id = middle_node.id)
        fresh_bottom_node_1 = CustomPrimaryKeyNode.objects.get(
            id = bottom_node_1.id)
        
        self.assertTrue(fresh_middle_node.is_child_of(root_node))
        self.assertFalse(fresh_bottom_node_1.is_child_of(root_node))
        

    def test_tree_structure_is_descendant_of(self):

        # Ensure string-based path encoding works.

        root_node = CustomPrimaryKeyNode.objects.create(id = 'root')
        middle_node = CustomPrimaryKeyNode.objects.create(id = 'middle',
            parent = root_node)
        bottom_node_1 = CustomPrimaryKeyNode.objects.create(id = 'bottom 1',
            parent = middle_node)
        bottom_node_2 = CustomPrimaryKeyNode.objects.create(id = 'bottom 2',
            parent = middle_node)
        bottom_node_3 = CustomPrimaryKeyNode.objects.create(id = 'bottom 3',
            parent = middle_node)

        fresh_root_node = CustomPrimaryKeyNode.objects.get(id = root_node.id)
        fresh_middle_node = CustomPrimaryKeyNode.objects.get(
            id = middle_node.id)
        fresh_bottom_node_1 = CustomPrimaryKeyNode.objects.get(
            id = bottom_node_1.id)

        self.assertTrue(fresh_bottom_node_1.is_descendant_of(fresh_root_node))

        self.assertTrue(fresh_root_node.is_ancestor_of(fresh_bottom_node_1))

        self.assertFalse(fresh_middle_node.is_descendant_of(
            fresh_bottom_node_1))

        self.assertFalse(fresh_bottom_node_1.is_ancestor_of(fresh_middle_node))


class DBTypePrimaryKeyNodeTest(TestCase):
    
    def test_tree_structure_is_child_of(self):
        
        # Ensure string-based path encoding works.
        
        root_node = DBTypePrimaryKeyNode.objects.create()
        middle_node = DBTypePrimaryKeyNode.objects.create(parent = root_node)
        bottom_node_1 = DBTypePrimaryKeyNode.objects.create(
            parent = middle_node)
        bottom_node_2 = DBTypePrimaryKeyNode.objects.create(
            parent = middle_node)
        bottom_node_3 = DBTypePrimaryKeyNode.objects.create(
            parent = middle_node)
        
        fresh_middle_node = DBTypePrimaryKeyNode.objects.get(
            id = middle_node.id)
        fresh_bottom_node_1 = DBTypePrimaryKeyNode.objects.get(
            id = bottom_node_1.id)
        
        self.assertTrue(fresh_middle_node.is_child_of(root_node))
        self.assertFalse(fresh_bottom_node_1.is_child_of(root_node))
        
        
    def test_tree_structure_is_ancestor_of(self):
        
        # Ensure string-based path encoding works.
        
        root_node = DBTypePrimaryKeyNode.objects.create()
        middle_node = DBTypePrimaryKeyNode.objects.create(parent = root_node)
        bottom_node = DBTypePrimaryKeyNode.objects.create(parent = middle_node)
        
        fresh_root_node = DBTypePrimaryKeyNode.objects.get(id = root_node.id)
        fresh_middle_node = DBTypePrimaryKeyNode.objects.get(
            id = middle_node.id)
        fresh_bottom_node = DBTypePrimaryKeyNode.objects.get(
            id = bottom_node.id)
        
        self.assertFalse(fresh_middle_node.is_ancestor_of(fresh_root_node))
        self.assertTrue(fresh_root_node.is_ancestor_of(fresh_middle_node))
        
        self.assertFalse(fresh_bottom_node.is_ancestor_of(fresh_root_node))
        self.assertTrue(fresh_root_node.is_ancestor_of(fresh_bottom_node))
        
        self.assertFalse(fresh_bottom_node.is_ancestor_of(fresh_middle_node))
        self.assertTrue(fresh_middle_node.is_ancestor_of(fresh_bottom_node))
        
        self.assertFalse(fresh_root_node.is_ancestor_of(fresh_root_node))
        self.assertFalse(fresh_middle_node.is_ancestor_of(fresh_middle_node))
        self.assertFalse(fresh_bottom_node.is_ancestor_of(fresh_bottom_node))
        
        
    def test_tree_structure_is_descendant_of(self):
        
        # Ensure string-based path encoding works.
        
        root_node = DBTypePrimaryKeyNode.objects.create()
        middle_node = DBTypePrimaryKeyNode.objects.create(parent = root_node)
        bottom_node = DBTypePrimaryKeyNode.objects.create(parent = middle_node)
        
        fresh_root_node = DBTypePrimaryKeyNode.objects.get(id = root_node.id)
        fresh_middle_node = DBTypePrimaryKeyNode.objects.get(
            id = middle_node.id)
        fresh_bottom_node = DBTypePrimaryKeyNode.objects.get(
            id = bottom_node.id)
        
        self.assertTrue(fresh_middle_node.is_descendant_of(fresh_root_node))
        self.assertFalse(fresh_root_node.is_descendant_of(fresh_middle_node))
        
        self.assertTrue(fresh_bottom_node.is_descendant_of(fresh_root_node))
        self.assertFalse(fresh_root_node.is_descendant_of(fresh_bottom_node))
        
        self.assertTrue(fresh_bottom_node.is_descendant_of(fresh_middle_node))
        self.assertFalse(fresh_middle_node.is_descendant_of(fresh_bottom_node))
        
        self.assertFalse(fresh_root_node.is_descendant_of(fresh_root_node))
        self.assertFalse(fresh_middle_node.is_descendant_of(fresh_middle_node))
        self.assertFalse(fresh_bottom_node.is_descendant_of(fresh_bottom_node))
