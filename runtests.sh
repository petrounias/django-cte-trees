#!/bin/sh
PYTHONPATH=. coverage run --branch --include="*cte_tree/*" cte_tree_test/manage.py test -v 2
coverage report -m
