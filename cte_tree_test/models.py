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

""" Models for the Django CTE Trees test application.
"""

__status__ = "Prototype"
__version__ = "0.9.2"
__maintainer__ = ("Alexis Petrounias <www.petrounias.org>", )
__author__ = ("Alexis Petrounias <www.petrounias.org>", )

# Django
from django.db.models import Model, ForeignKey, CharField, FloatField, \
    PositiveIntegerField, DateField

# Django CTE Trees
from cte_tree.models import CTENode, CTENodeManager
from cte_tree_test.fields import UUIDField


class SimpleNode(CTENode, Model):

    pass
    
    
class NoneDeleteNode(CTENode, Model):

    _cte_node_delete_method = 'none'
    
    
class SimpleNodeUser(Model):

    node = ForeignKey(SimpleNode, null = False)
    
    
class NamedNode(CTENode, Model):

    name = CharField(max_length = 128, null = False)

    class Meta:

        abstract = True
        
    
class SimpleNamedNode(NamedNode):
    
    pass
    
    
class OrderedNamedNode(NamedNode):
    
    _cte_node_order_by = ['name']


class ValueNamedNode(NamedNode):

    v = PositiveIntegerField()


class SimpleNamedNodeUser(Model):
    
    node = ForeignKey(SimpleNamedNode, null = False)
    
    name = CharField(max_length = 128, null = False)
    
    
class OrderedNamedNodeUser(Model):
    
    node = ForeignKey(OrderedNamedNode, null = False)
    
    name = CharField(max_length = 128, null = False)


class DFSOrderedNode(CTENode, Model):
    
    v = PositiveIntegerField()
    
    _cte_node_traversal = 'dfs'
    
    _cte_node_order_by = ['v']
    
    
class BFSOrderedNode(CTENode, Model):
    
    v = PositiveIntegerField()
    
    _cte_node_traversal = 'bfs'
    
    _cte_node_order_by = ['v']
    
    
class NoneTraversalNode(CTENode, Model):
    
    v = PositiveIntegerField()
    
    _cte_node_traversal = 'none'
    
    _cte_node_order_by = ['v']
    
    
class TypeCoercionNode(CTENode, Model):
    
    name = CharField(max_length = 128, null = False)
    
    v = PositiveIntegerField()
    
    _cte_node_order_by = [('v', 'text'), 'name']
    
    
class TypeCombinationNode(CTENode, Model):
    
    v1 = PositiveIntegerField()
    
    v2 = FloatField()
    
    _cte_node_traversal = 'bfs'
    
    _cte_node_order_by = [('v1', 'float'), 'v2']
    
    
class ExoticTypeNode(CTENode, Model):
    
    v = DateField()
    
    _cte_node_order_by = ['v']
    
    
class DBTypeNode(CTENode, Model):
    
    v = UUIDField()
    
    _cte_node_order_by = ['v']
    
    
class CustomPrimaryKeyNode(CTENode, Model):
    
    id = CharField(max_length = 128, primary_key = True)
    
    
class DBTypePrimaryKeyNode(CTENode, Model):
    
    id = UUIDField(primary_key = True)
    

class BadParameter_parent_1_Node(CTENode, Model):
    
    _cte_node_parent = 'wrong'

    
class ArbitraryNode(CTENode, Model):
    
    pass


class BadParameter_parent_2_Node(CTENode, Model):
    
    
    wrong = ForeignKey(ArbitraryNode, null = True)
    
    _cte_node_parent = 'wrong'
    
    
class ArbitraryModel(Model):
    
    pass


class BadParameter_parent_3_Node(CTENode, Model):
    
    wrong = ForeignKey(ArbitraryModel, null = True)
    
    _cte_node_parent = 'wrong'
    
    
class BadParameter_parent_4_Node(Model):
    
    objects = CTENodeManager()
    
    
class BadParameter_traversal_Node(CTENode, Model):
    
    _cte_node_traversal = 'wrong'
    
    
class BadParameter_delete_Node(CTENode, Model):
    
    _cte_node_delete_method = 'wrong'
    
