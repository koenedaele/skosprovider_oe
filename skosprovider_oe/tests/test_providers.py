# -*- coding: utf-8 -*-

try:
    import unittest2 as unittest
except ImportError:  # pragma NO COVER
    import unittest  # noqa

from skosprovider_oe.providers import (
    OnroerendErfgoedProvider
)

from skosprovider.skos import (
    Concept,
    Collection
)


class OnroerendErfgoedProviderTests(unittest.TestCase):
    def setUp(self):
        self.typologie = OnroerendErfgoedProvider(
            {'id': 'TYPOLOGIE'},
            url='https://inventaris.onroerenderfgoed.be/thesaurus/typologie'
        )
        self.stijl = OnroerendErfgoedProvider(
            {'id': 'STIJL'},
            url='https://inventaris.onroerenderfgoed.be/thesaurus/stijl'
        )

    def tearDown(self):
        del self.typologie
        del self.stijl

    def test_default_url(self):
        typologie = OnroerendErfgoedProvider(
            {'id': 'TYPOLOGIE'}
        )
        self.assertEquals(
            'https://inventaris.onroerenderfgoed.be/thesaurus/typologie',
            typologie.url
        )

    def test_base_url(self):
        typologie = OnroerendErfgoedProvider(
            {'id': 'TYPOLOGIE'},
            base_url='http://inventaris.vioe.be/thesaurus/%s'
        )
        self.assertEquals(
            'http://inventaris.vioe.be/thesaurus/typologie',
            typologie.url
        )

    def test_thesaurus(self):
        soort = OnroerendErfgoedProvider(
            {'id': 'SOORT'},
            thesaurus='soort'
        )
        self.assertEquals(
            'https://inventaris.onroerenderfgoed.be/thesaurus/soort',
            soort.url
        )

    def test_get_vocabulary_id(self):
        self.assertEquals('TYPOLOGIE', self.typologie.get_vocabulary_id())

    def test_get_metadata(self):
        self.assertEquals({'id': 'TYPOLOGIE', 'default_language': 'nl'},
                          self.typologie.get_metadata())

    def test_get_by_unexisting_id(self):
        self.assertFalse(self.typologie.get_by_id('RESTAFVAL'))

    def test_get_by_uri(self):
        self.assertFalse(self.typologie.get_by_uri(
            'urn:x-skosprovider:typologie:700'
        ))

    def test_find(self):
        result = self.typologie.find({'label': 'kerken'})
        self.assertGreater(len(result), 0)
        for c in result:
            self.assertIn('id', c)
            self.assertIn('label', c)

    def test_find_collections(self):
        result = self.typologie.find({'type': 'collection'})
        self.assertGreater(len(result), 0)
        for c in result:
            self.assertIn('id', c)
            self.assertIn('label', c)
            cc = self.typologie.get_by_id(c['id'])
            self.assertIsInstance(cc, Collection)

    def test_find_concepts(self):
        # Use stijl thesaurus to speed things up
        result = self.stijl.find({
            'type': 'concept',
            'label': 'isme'
        })
        self.assertGreater(len(result), 0)
        for c in result:
            self.assertIn('id', c)
            self.assertIn('label', c)
            cc = self.stijl.get_by_id(c['id'])
            self.assertIsInstance(cc, Concept)

    def test_find_in_collection(self):
        result = self.stijl.find({
            'collection': {
                'id': 62,
                'depth': 'all'
            }
        })
        self.assertGreater(len(result), 0)
        resultids = [s.get('id') for s in result]
        expansion = self.stijl.expand(62)
        self.assertEqual(set(expansion),set(resultids))

    def test_find_in_collection_depth(self):
        members = self.typologie.find({
            'collection': {
                'id': 1604,
                'depth': 'members'
            }, 
            'type': 'concept'
        })
        all = self.typologie.find({
            'collection': {
                'id': 1604,
                'depth': 'all'
            },
            'type': 'concept'
        })
        self.assertGreater(len(all), len(members))
        self.assertNotEqual(members, all)

    def test_find_in_unexisting_collection(self):
        self.assertRaises(ValueError, self.stijl.find, {'collection': {'id': 'bestaat_niet'}})

    def test_get_all(self):
        result = self.typologie.get_all()
        self.assertGreater(len(result), 0)
        for c in result:
            self.assertIn('id', c)
            self.assertIn('label', c)

    def test_get_top_concepts(self):
        top = self.stijl.get_top_concepts()
        self.assertGreater(len(top), 0)
        for c in top:
            cc = self.stijl.get_by_id(c['id'])
            self.assertIsInstance(cc, Concept)

    def test_expand_concept(self):
        result = self.typologie.expand_concept(100)
        self.assertGreater(len(result), 0)

    def test_expand_unexisting(self):
        self.assertEqual(False, self.typologie.expand(987654321))

    def test_get_by_id(self):
        '''
        Query for hoeven and check each individual.

        Querying for hoeven gives us both concepts and collections to test.
        '''
        kerken = self.typologie.find({'label': 'hoeven'})
        for k in kerken:
            result = self.typologie.get_by_id(k['id'])
            try:
                self.assertIsInstance(result, Concept)
            except AssertionError:
                self.assertIsInstance(result, Collection)

    def test_get_by_id_returns_primary_term(self):
        result = self.stijl.get_by_id(58)
        self.assertNotEquals(58, result.id)
