paka.sitemaps
=============
.. image:: https://travis-ci.org/PavloKapyshin/paka.sitemaps.svg?branch=master
    :target: https://travis-ci.org/PavloKapyshin/paka.sitemaps

``paka.sitemaps`` is a Python library that helps generate XML files according
to `sitemaps.org protocol <https://www.sitemaps.org/protocol.html>`_.


Features
--------
- Python 2.7 and 3.5 are supported
- PyPy (Python 2.7) is supported
- does not depend on any web framework
- automatically splits all added URLs into sitemaps and sitemap indexes
- lazily writes to file system


Examples
--------
.. code-block:: pycon

    >>> from paka import sitemaps

Create directory for resulting XML files (here it is a temporary directory):

.. code-block:: pycon

    >>> import tempfile
    >>> fs_root = tempfile.mkdtemp()

Create sitemap building context, add few URLs to it, and close the context:

.. code-block:: pycon

    >>> ctx = sitemaps.Context(
    ...     fs_root=fs_root, base_url=u"http://example.org")
    >>> ctx.add(u"/some/path-here/", priority=0.1)
    >>> ctx.add(u"/other")
    >>> ctx.close()

Now `fs_root` contains one sitemap and one sitemap index:

.. code-block:: pycon

    >>> import os
    >>> sorted(os.listdir(fs_root))
    ['i1.xml', 's1-1.xml']

Results can be checked with XML parser (here ``lxml`` is used):

.. code-block:: pycon

    >>> from lxml import etree
    >>> doc = etree.parse(os.path.join(fs_root, "s1-1.xml"))
    >>> ns = {"s": sitemaps.XMLNS}
    >>> url_els = doc.xpath("//s:url", namespaces=ns)
    >>> sorted([el.findtext("s:loc", namespaces=ns) for el in url_els])
    ['http://example.org/other', 'http://example.org/some/path-here/']

Remove directory and files created for demonstration:

.. code-block:: pycon

    >>> import shutil
    >>> shutil.rmtree(fs_root)


Installation
------------
Library is `available on PyPI <https://pypi.python.org/pypi/paka.sitemaps>`_,
you can use ``pip`` for installation:

.. code-block:: console

    $ pip install paka.sitemaps


Running tests
-------------
.. code-block:: console

    $ tox


Getting coverage
----------------
Collect info:

.. code-block:: console

    $ tox -e coverage

View HTML report:

.. code-block:: console

    $ sensible-browser .tox/coverage/tmp/cov_html/index.html


Checking code style
-------------------
Run code checkers:

.. code-block:: console

    $ tox -e checks


Getting documentation
---------------------
Build HTML docs:

.. code-block:: console

    $ tox -e docs

View built docs:

.. code-block:: console

    $ sensible-browser .tox/docs/tmp/docs_html/index.html
