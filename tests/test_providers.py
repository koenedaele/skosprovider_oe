# -*- coding: utf-8 -*-

import unittest

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
        self.gebeurtenis = OnroerendErfgoedProvider(
            {'id': 'GEBEURTENIS'},
            base_url='https://inventaris.onroerenderfgoed.be/thesaurus/%s',
            thesaurus='gebeurtenis'
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
        self.assertEquals(
            'TYPOLOGIE',
            self.typologie.get_vocabulary_id()
        )

    def test_get_metadata(self):
        self.assertEquals(
            {
                'id': 'TYPOLOGIE',
                'default_language': 'nl',
                'subject': []
            },
            self.typologie.get_metadata()
        )

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
        result = self.stijl.find({'type': 'collection'})
        self.assertGreater(len(result), 0)
        for c in result:
            self.assertIn('id', c)
            self.assertIn('label', c)
            cc = self.stijl.get_by_id(c['id'])
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
        top = self.gebeurtenis.get_top_concepts()
        self.assertGreater(len(top), 0)
        for c in top:
            cc = self.gebeurtenis.get_by_id(c['id'])
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

    def test_get_by_id_conceptscheme(self):
        result = self.stijl.get_by_id(58)
        self.assertEqual(result.concept_scheme, self.stijl.concept_scheme)

    def test_get_top_display(self):
        top = self.stijl.get_top_display()
        self.assertGreater(len(top), 0)

    def test_get_children_display_concepts(self):
        kapeltypes = self.typologie.get_children_display(513)
        self.assertGreater(len(kapeltypes), 0)

    def test_get_children_display_collections(self):
        cult_metal = self.stijl.get_children_display(63)
        self.assertGreater(len(cult_metal), 0)

    def test_member_of(self):
        romaans = self.stijl.get_by_id(3)
        self.assertEquals([60], romaans.member_of)

    def test_superordinates_of_collection(self):
        opgravingen_naar_methode = self.gebeurtenis.get_by_id(67)
        self.assertIn(38, opgravingen_naar_methode.superordinates)
        self.assertEqual(len(opgravingen_naar_methode.superordinates), 1)

    def test_subordinates_of_collection(self):
        archeologische_opgravingen = self.gebeurtenis.get_by_id(38)
        self.assertIn(67, archeologische_opgravingen.subordinate_arrays)
        self.assertEqual(len(archeologische_opgravingen.subordinate_arrays), 3)

    def test_notes(self):
        romaans = self.stijl.get_by_id(3)
        from skosprovider.skos import Note
        self.assertIsInstance(romaans.notes, list)
        self.assertIsInstance(romaans.notes[0], Note)
        note_values = [note_element.note for note_element in romaans.notes]
        note_1 = 'De romaanse bouwstijl wordt gekenmerkt door massieve stenen muren met kleine gevelopeningen, doorgaans met rondboog en soms gedeeld door middenzuiltjes. De overdekking gebeurde met een vlak houten gewelf, of - minder courant - met stenen ton-, kruis- en koepelgewelven. De decoratieve afwerking wordt gekarakteriseerd door rondboogfriezen, rondboognissen en lisenen. (ca. 10de eeuw tot 1200)'
        self.assertIn(note_1, note_values)
        ad_hoc = self.gebeurtenis.get_by_id(66)
        self.assertEqual(0, len(ad_hoc.notes))
        actualisatie = self.gebeurtenis.get_by_id(120)
        self.assertEqual(1, len(actualisatie.notes))

    def test_source(self):
        romaans = self.stijl.get_by_id(3)
        self.assertIsInstance(romaans.sources, list)
        source = 'HASLINGHUIS, E.J. en JANSE, H., Verklarend woordenboek van de westerse architectuur- en bouwhistorie: bouwkundige termen, Leiden, 2005.'
        sources = [s.citation for s in romaans.sources]
        assert source in sources

    def test_matches(self):
        agr_ls = self.typologie.get_by_id(2103)
        self.assertIsInstance(agr_ls.matches, dict)
        assert 'related' in agr_ls.matches
        assert 'http://vocab.getty.edu/aat/300008631' in agr_ls.matches['related']
