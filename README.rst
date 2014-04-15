skosprovider_oe: a skos provider for Onroerend Erfgoed
======================================================

This library implements a `SKOS provider <https://github.com/koenedaele/skosprovider>` 
for the thesaurus webservice of https://inventaris.onroerenderfgoed.be/thesaurus.

.. image:: https://travis-ci.org/koenedaele/skosprovider_oe.png?branch=master
        :target: https://travis-ci.org/koenedaele/skosprovider_oe
.. image:: https://coveralls.io/repos/koenedaele/skosprovider_oe/badge.png?branch=master
        :target: https://coveralls.io/r/koenedaele/skosprovider_oe
.. image:: https://badge.fury.io/py/skosprovider_oe.png
        :target: http://badge.fury.io/py/skosprovider_oe

Usage
-----

.. code-block:: python

    from skosprovider_oe.providers import OnroerendErfgoedProvider
    
    typologie = OnroerendErfgoedProvider(
        {'id': 'TYPOLOGIE'},
        'https://inventaris.onroerenderfgoed.be/thesaurus/typologie'
    )

    concepts = typologie.get_all()
