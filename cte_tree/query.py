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

""" Django CTE Trees Query Compiler.
"""
from __future__ import print_function
from __future__ import absolute_import

__status__ = "beta"
__version__ = "1.0.2"
__maintainer__ = (u"Alexis Petrounias <www.petrounias.org>", )
__author__ = (u"Alexis Petrounias <www.petrounias.org>", )

# Django
from django.db import connections
from django.db.models.query import QuerySet
from django.db.models.sql import UpdateQuery, InsertQuery, DeleteQuery, \
    AggregateQuery
from django.db.models.sql.query import Query
from django.db.models.sql.compiler import SQLCompiler, SQLUpdateCompiler, \
    SQLInsertCompiler, SQLDeleteCompiler, SQLAggregateCompiler
from django.db.models.sql.where import ExtraWhere, WhereNode


class CTEQuerySet(QuerySet):
    """
    The QuerySet which ensures all CTE Node SQL compilation is processed by the
    CTE Compiler and has the appropriate extra syntax, selects, tables, and
    WHERE clauses.
    """

    def __init__(self, model = None, query = None, using = None, offset = None, hints = None):
        """
        Prepares a CTEQuery object by adding appropriate extras, namely the
        SELECT virtual fields, the WHERE clause which matches the CTE pk with
        the real table pk, and the tree-specific order_by parameters. If the
        query object has already been prepared through this phase, then it
        won't be prepared again.

        :param model:
        :type model:
        :param query:
        :type query:
        :param using:
        :type using:
        :param offset:
        :type offset:
        :return:
        :rtype:
        """
        # Only create an instance of a Query if this is the first invocation in
        # a query chain.
        if query is None:
            query = CTEQuery(model, offset = offset)
        super(CTEQuerySet, self).__init__(model, query, using)

    def aggregate(self, *args, **kwargs):
        """
        Returns a dictionary containing the calculations (aggregation)
        over the current queryset

        If args is present the expression is passed as a kwarg using
        the Aggregate object's default alias.
        """
        if self.query.distinct_fields:
            raise NotImplementedError("aggregate() + distinct(fields) not implemented.")
        for arg in args:
            # The default_alias property may raise a TypeError, so we use
            # a try/except construct rather than hasattr in order to remain
            # consistent between PY2 and PY3 (hasattr would swallow
            # the TypeError on PY2).
            try:
                arg.default_alias
            except (AttributeError, TypeError):
                raise TypeError("Complex aggregates require an alias")
            kwargs[arg.default_alias] = arg

        query = self.query.clone(CTEAggregateQuery)
        for (alias, aggregate_expr) in kwargs.items():
            query.add_annotation(aggregate_expr, alias, is_summary=True)
            if not query.annotations[alias].contains_aggregate:
                raise TypeError("%s is not an aggregate expression" % alias)
        return query.get_aggregation(self.db, kwargs.keys())


class CTEQuery(Query):
    """
    A Query which processes SQL compilation through the CTE Compiler, as well as
    keeps track of extra selects, the CTE table, and the corresponding WHERE
    clauses.
    """

    def __init__(self, model, where = WhereNode, offset = None):
        """
        Delegates initialization to Django's Query, and in addition adds the
        necessary extra selects, table, and where clauses for the CTE. Depending
        on the ordering semantics specified in the CTE Node as well as any
        order_by queries, the final order_by of the Query is generated. In the
        event of an offset Node being specified (such as querying for all of the
        descendants of a Node), an additional appropriate WHERE clauses is also
        added.

        :param model:
        :type model:
        :param where:
        :type where:
        :param offset:
        :type offset:
        :return:
        :rtype:
        """
        super(CTEQuery, self).__init__(model, where = where)
        # import from models here to avoid circular imports.
        from .models import CTENodeManager
        if not model is None:
            where = [self._generate_where(self)]
            # If an offset Node is specified, then only those Nodes which
            # contain the offset Node as a parent (in their path virtual field)
            # will be returned.
            if not offset is None:
                where.append("""'{id}' = ANY({cte}."{path}")""".format(
                    cte = model._cte_node_table,
                    path = model._cte_node_path,
                    id = str(offset.id)))
            order_by_prefix = []
            if model._cte_node_traversal == \
                CTENodeManager.TREE_TRAVERSAL_NONE:
                chosen_traversal = CTENodeManager.DEFAULT_TREE_TRAVERSAL
            else:
                chosen_traversal = model._cte_node_traversal
            if chosen_traversal == CTENodeManager.TREE_TRAVERSAL_DFS:
                order_by_prefix = [ model._cte_node_ordering ]
            if chosen_traversal == CTENodeManager.TREE_TRAVERSAL_BFS:
                order_by_prefix = [ model._cte_node_depth,
                    model._cte_node_ordering ]
            # prepend correct CTE table prefix to order_by fields
            order_by = ['{cte}.{field}'.format(
                cte = model._cte_node_table, field = field) for \
                    field in order_by_prefix]
            if hasattr(model, '_cte_node_order_by') and \
                not model._cte_node_order_by is None and \
                len(model._cte_node_order_by) > 0:
                order_by.extend([field[0] if type(field) == tuple else \
                    field for field in model._cte_node_order_by])
            # Specify the virtual fields for depth, path, and ordering;
            # optionally the offset Node constraint; and the desired ordering.
            # The CTE table will be added later by the Compiler only if the
            # actual query needs it.
            self.add_extra(
                select = {
                    model._cte_node_depth : '{cte}.{depth}'.format(
                        cte = model._cte_node_table,
                        depth = model._cte_node_depth),
                    model._cte_node_path : '{cte}.{path}'.format(
                        cte = model._cte_node_table,
                        path = model._cte_node_path),
                    model._cte_node_ordering : '{cte}.{ordering}'.format(
                        cte = model._cte_node_table,
                        ordering = model._cte_node_ordering),
                },
                select_params = None,
                where = where,
                params = None,
                tables = None,
                order_by = order_by)

    @classmethod
    def _generate_where(cls, query):
        def maybe_alias(table):
            if table in query.table_map:
                return query.table_map[table][0]
            return table
        return '{cte}."{pk}" = {table}."{pk}"'.format(
            cte = query.model._cte_node_table,
            pk = query.model._meta.pk.attname,
            table = maybe_alias(query.model._meta.db_table))

    @classmethod
    def _remove_cte_where(cls, query):
        where = cls._generate_where(query)
        for w in query.where.children:
            if isinstance(w, ExtraWhere):
                if where in w.sqls:
                    query.where.children.remove(w)

    def get_compiler(self, using = None, connection = None):
        """ Overrides the Query method get_compiler in order to return
            an instance of the above custom compiler.
        """
        # Copy the body of this method from Django except the final
        # return statement. We will ignore code coverage for this.
        if using is None and connection is None: #pragma: no cover
            raise ValueError("Need either using or connection")
        if using:
            connection = connections[using]
        # Check that the compiler will be able to execute the query
        for alias, aggregate in self.annotation_select.items():
            connection.ops.check_aggregate_support(aggregate)
        # Instantiate the custom compiler.
        return {
            CTEUpdateQuery : CTEUpdateQueryCompiler,
            CTEInsertQuery : CTEInsertQueryCompiler,
            CTEDeleteQuery : CTEDeleteQueryCompiler,
            CTEAggregateQuery : CTEAggregateQueryCompiler,
        }.get(self.__class__, CTEQueryCompiler)(self, connection, using)

    def clone(self, klass = None, memo = None, **kwargs):
        """ Overrides Django's Query clone in order to return appropriate CTE
            compiler based on the target Query class. This mechanism is used by
            methods such as 'update' and '_update' in order to generate UPDATE
            queries rather than SELECT queries.
        """
        klass = {
            UpdateQuery : CTEUpdateQuery,
            InsertQuery : CTEInsertQuery,
            DeleteQuery : CTEDeleteQuery,
            AggregateQuery : CTEAggregateQuery,
        }.get(klass, self.__class__)
        return super(CTEQuery, self).clone(klass, memo, **kwargs)


class CTEUpdateQuery(UpdateQuery, CTEQuery):
    pass


class CTEInsertQuery(InsertQuery, CTEQuery):
    pass


class CTEDeleteQuery(DeleteQuery, CTEQuery):
    pass


class CTEAggregateQuery(AggregateQuery, CTEQuery):
    pass


class CTECompiler(object):

    CTE = """WITH RECURSIVE {cte} ("{depth}", "{path}", "{ordering}", "{pk}") AS (

    SELECT 1 AS depth,
           array[{pk_path}] AS {path},
           {order} AS {ordering},
           T."{pk}"
      FROM {db_table} T
     WHERE T."{parent}" IS NULL

     UNION ALL

    SELECT {cte}.{depth} + 1 AS {depth},
           {cte}.{path} || {pk_path},
           {cte}.{ordering} || {order},
           T."{pk}"
      FROM {db_table} T
      JOIN {cte} ON T."{parent}" = {cte}."{pk}")

    """

    @classmethod
    def generate_sql(cls, connection, query, as_sql):
        """

        :param query:
        :type query:
        :param sql:
        :type sql:
        :return:
        :rtype:
        """
        # add the CTE table to the Query's extras precisely once (because we
        # could be combining multiple CTE Queries).
        if not query.model._cte_node_table in query.extra_tables:
            query.add_extra(
                select = None,
                select_params = None,
                where = None,
                params = None,
                tables = [query.model._cte_node_table],
                order_by = None)

        # place appropriate CTE table prefix to any order_by or extra_order_by
        # entries which reference virtual fields, and preserve the optional
        # sign.
        cte_columns = (
            query.model._cte_node_depth,
            query.model._cte_node_path,
            query.model._cte_node_ordering,
        )
        def maybe_prefix_order_by(order_by):
            for index, o in enumerate(order_by):
                _o = o.lstrip('-')
                if _o in cte_columns:
                    order_by[index] = '{sign}{cte}.{column}'.format(
                        sign = '-' if o[0] == '-' else '',
                        cte = query.model._cte_node_table,
                        column = _o)
        maybe_prefix_order_by(query.order_by)
        maybe_prefix_order_by(query.extra_order_by)

        # Obtain compiled SQL from Django.
        sql = as_sql()

        def maybe_cast(field):
            # If the ordering information specified a type to cast to, then use
            # this type immediately, otherwise determine whether a
            # variable-length character field should be cast into TEXT or if no
            # casting is necessary. A None type defaults to the latter.
            if type(field) == tuple and not field[1] is None:
                return 'CAST (T."%s" AS %s)' % field
            else:
                if type(field) == tuple:
                    name = field[0]
                else:
                    name = field
                _field = query.model._meta.get_field(name)
                if _field.db_type(connection).startswith('varchar'):
                    return 'CAST (T."%s" AS TEXT)' % name
                else:
                    return 'T."%s"' % name

        # The primary key is used in the path; in case it is of a custom type,
        # ensure appropriate casting is performed. This is a very rare
        # condition, as most types can be used directly in the path, especially
        # since no other fields with incompatible types are combined (with a
        # notable exception of VARCHAR types which must be converted to TEXT).
        pk_path = maybe_cast((query.model._meta.pk.attname,
            query.model._cte_node_primary_key_type))

        # If no explicit ordering is specified, then use the primary key. If the
        # primary key is used in ordering, and it is of a type which needs
        # casting in order to be used in the ordering, then it is possible that
        # explicit casting was not specified through _cte_node_order_by because
        # it is expected to be specified through the _cte_node_primary_key_type
        # attribute. Specifying the cast type of the primary key in the
        # _cte_node_order_by attribute has precedence over
        # _cte_node_primary_key_type.
        if not hasattr(query.model, '_cte_node_order_by') or \
            query.model._cte_node_order_by is None or \
            len(query.model._cte_node_order_by) == 0:
            order = 'array[%s]' % maybe_cast((
                query.model._meta.pk.attname,
                query.model._cte_node_primary_key_type))
        else:
            # Compute the ordering virtual field constructor, possibly casting
            # fields into a common type.
            order = '||'.join(['array[%s]' % maybe_cast(field) for \
                field in query.model._cte_node_order_by])
        # Prepend the CTE with the ordering constructor and table
        # name to the SQL obtained from Django above.
        return (''.join([
            cls.CTE.format(order = order,
                cte = query.model._cte_node_table,
                depth = query.model._cte_node_depth,
                path = query.model._cte_node_path,
                ordering = query.model._cte_node_ordering,
                parent = query.model._cte_node_parent_attname,
                pk = query.model._meta.pk.attname,
                pk_path = pk_path,
                db_table = query.model._meta.db_table
            ), sql[0]]), sql[1])


class CTEQueryCompiler(SQLCompiler):

    def as_sql(self, *args, **kwargs):
        """
        Overrides the :class:`SQLCompiler` method in order to prepend the
        necessary CTE syntax, as well as perform pre- and post-processing,
        including adding the extra CTE table and WHERE clauses.

        :param with_limits:
        :type with_limits:
        :param with_col_aliases:
        :type with_col_aliases:
        :return:
        :rtype:
        """
        def _as_sql():
            return super(CTEQueryCompiler, self).as_sql(*args, **kwargs)
        return CTECompiler.generate_sql(self.connection, self.query, _as_sql)


class CTEUpdateQueryCompiler(SQLUpdateCompiler):

    def as_sql(self, *args, **kwargs):
        """
        Overrides the :class:`SQLUpdateCompiler` method in order to remove any
        CTE-related WHERE clauses, which are not necessary for UPDATE queries,
        yet may have been added if this query was cloned from a CTEQuery.

        :return:
        :rtype:
        """
        CTEQuery._remove_cte_where(self.query)
        return super(self.__class__, self).as_sql(*args, **kwargs)


class CTEInsertQueryCompiler(SQLInsertCompiler):

    def as_sql(self, *args, **kwargs):
        """
        Overrides the :class:`SQLInsertCompiler` method in order to remove any
        CTE-related WHERE clauses, which are not necessary for INSERT queries,
        yet may have been added if this query was cloned from a CTEQuery.

        :return:
        :rtype:
        """
        CTEQuery._remove_cte_where(self.query)
        return super(self.__class__, self).as_sql(*args, **kwargs)


class CTEDeleteQueryCompiler(SQLDeleteCompiler):

    def as_sql(self, *args, **kwargs):
        """
        Overrides the :class:`SQLDeleteCompiler` method in order to remove any
        CTE-related WHERE clauses, which are not necessary for DELETE queries,
        yet may have been added if this query was cloned from a CTEQuery.

        :return:
        :rtype:
        """
        CTEQuery._remove_cte_where(self.query)
        return super(self.__class__, self).as_sql(*args, **kwargs)


class CTEAggregateQueryCompiler(SQLAggregateCompiler):

    def as_sql(self, *args, **kwargs):
        """
        Overrides the :class:`SQLAggregateCompiler` method in order to
        prepend the necessary CTE syntax, as well as perform pre- and post-
        processing, including adding the extra CTE table and WHERE clauses.

        :param qn:
        :type qn:
        :return:
        :rtype:
        """
        def _as_sql():
            return super(CTEAggregateQueryCompiler, self).as_sql(*args, **kwargs)
        return CTECompiler.generate_sql(self.connection, self.query, _as_sql)
