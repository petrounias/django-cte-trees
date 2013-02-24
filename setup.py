from setuptools import setup, find_packages
import cte_tree
 
setup(
    name = 'django-cte-trees',
    version = cte_tree.__version__,
    packages = find_packages(),
    include_package_data=True,
    author = 'Alexis Petrounias <www.petrounias.org>',
    maintainer = 'Alexis Petrounias <www.petrounias.org>',
    keywords = 'django, postgresql, cte, trees, sql',
    license = 'BSD',
    description = 'Experimental implementation of Adjacency-List trees for Django using PostgreSQL Common Table Expressions (CTE).',
    long_description=open('README.txt').read(),
    url='http://www.petrounias.org/software/django-cte-trees/',
    download_url = "https://github.com/petrounias/django-cte-trees/archive/master.zip",
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)

