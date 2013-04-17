# -*- coding: utf-8 -*-

from skosprovider.providers import VocabularyProvider

from skosprovider.skos import (
    Concept,
    Collection
)

import requests


class OnroerendErfgoedProvider(VocabularyProvider):
    '''A provider that can work with the REST-services of
    https://inventaris.onroerenderfgoed.be/thesaurus

    '''

    def __init__(self, metadata, url=None):
        if not 'default_language' in metadata:
            metadata['default_language'] = 'nl'
        super(OnroerendErfgoedProvider, self).__init__(metadata)
        if url is None:
            url = 'https://inventaris.onroerenderfgoed.be/thesaurus/typologie'
        self.url = url

    def get_by_id(self, id):
        url = (self.url + '/%s.json') % id
        r = requests.get(url)
        if r.status_code == 404:
            return False
        result = r.json()
        if result['term_type'] == 'ND':
            return self.get_by_id(result['use'])
        concept = {}
        concept['id'] = result['id']
        concept['type'] = 'concept' if result['term_type'] == 'PT' else 'collection'
        concept['labels'] = []
        concept['labels'].append(
            {
                'type': 'prefLabel',
                'language': result['language'],
                'label': result['term']
            }
        )
        if 'broader_term' in result:
            concept['broader'] = [result['broader_term']]
        if 'narrower_terms' in result:
            if concept['type'] == 'concept':
                concept['narrower'] = result['narrower_terms']
            else:
                concept['members'] = result['narrower_terms']
        if 'use_for' in result:
            for t in result['use_for']:
                term = self._get_term_by_id(t)
                concept['labels'].append(
                    {
                        'type': 'altLabel',
                        'language': term['language'],
                        'label': term['term']
                    }
                )
        if 'related_terms' in result:
            concept['related'] = result['related_terms']
        return self._from_dict(concept)

    def _from_dict(self, concept):
        if concept['type'] == 'concept':
            return Concept(
                id = concept['id'],
                labels = concept['labels'] if 'labels' in concept else [],
                broader = concept['broader'] if 'broader' in concept else [],
                narrower = concept['narrower'] if 'narrower' in concept else [],
                related = concept['related'] if 'related' in concept else []
            )
        else:
            return Collection(
                id = concept['id'],
                labels = concept['labels'] if 'labels' in concept else [],
                members = concept['members'] if 'members' in concept else [],
            )

    def _get_term_by_id(self, id):
        '''Simple utility function to load a term.
        '''
        url = (self.url + '/%s.json') % id
        r = requests.get(url)
        return r.json()

    def find(self, query):
        return self._do_query(query)

    def get_all(self):
        return self._do_query()

    def _do_query(self, query=None):
        url = self.url + '/lijst.json'
        args = {'type[]': ['HR', 'PT', 'NL']}
        if query is not None:
            if 'type' in query:
                if query['type'] == 'collection':
                    args['type[]'] = ['HR', 'NL']
                elif query['type'] == 'concept':
                    args['type[]'] = ['PT']
            if 'label' in query:
                args['term'] = query['label']
        r = requests.get(url, params=args)
        result = r.json()
        items = result['items']
        if query is not None and 'collection' in query:
            #Restrict results to element of collection
            coll = self.get_by_id(query['collection']['id'])
            if not coll or not isinstance(coll, Collection):
                raise ValueError(
                    'You are searching for items in an unexisting collection.'
                )
            else:
                if 'depth' in query['collection'] and query['collection']['depth'] == 'all':
                    members = self.expand(coll.id)
                else:
                    members = coll.members
            items = [x for x in items if x['id'] in members]
        return [
            {
                'id': x['id'],
                'label': x['omschrijving']
            } for x in items
        ]

    def expand_concept(self, id):
        return self.expand(id)

    def expand(self, id):
        url = (self.url + '/%s/subtree.json') % id
        r = requests.get(url)
        if r.status_code == 404:
            return False
        return r.json()

