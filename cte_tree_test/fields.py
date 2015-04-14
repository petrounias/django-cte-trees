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

""" Custom Fields for use in the Django CTE Trees test application.
"""

__status__ = "beta"
__version__ = "1.0.2"
__maintainer__ = (u"Alexis Petrounias <www.petrounias.org>", )
__author__ = (u"Alexis Petrounias <www.petrounias.org>", )

# Python
from uuid import UUID, uuid4

# Django
from django.db.models import CharField, SubfieldBase

# PsycoPG 2
from psycopg2.extras import register_uuid


# Register PostgreSQL UUID type.
register_uuid()


class UUIDField(CharField):
    
    # Used so to_python() is called.
    __metaclass__ = SubfieldBase


    def __init__(self, *args, **kwargs):
        kwargs.setdefault('default', uuid4)
        kwargs.setdefault('max_length', 32)
        kwargs.setdefault('editable', not kwargs.get('primary_key', False))
        super(UUIDField, self).__init__(*args, **kwargs)


    def db_type(self, connection = None):
        return 'uuid'

    def get_db_prep_value(self, value, connection, prepared = False):
        if not prepared:
            return self.to_python(value)
        return value
    
    def to_python(self, value):
        if not value:
            return None
        if not isinstance(value, UUID):
            value = UUID(value)
        return value
    

# South support
# see http://south.aeracode.org/docs/tutorial/part4.html#simple-inheritance
try:
    from south.modelsinspector import add_introspection_rules
except ImportError:
    pass
else:
    add_introspection_rules([], [r"^cte_tree_test\.fields\.UUIDField", ])
    
