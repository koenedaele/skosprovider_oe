# -*- coding: utf-8 -*-

from skosprovider.providers import VocabularyProvider

import requests

class OnroerendErfgoedProvider(VocabularyProvider):
    '''A provider that can work with the REST-services of https://inventaris.onroerenderfgoed.be/thesaurus

    '''

    def __init__(self, metadata, url = None):
        if not 'default_language' in metadata:
            metadata['default_language'] = 'nl'
        super(OnroerendErfgoedProvider,self).__init__(metadata)
        if url is None:
            url = 'https://inventaris.onroerenderfgoed.be/thesaurus/typologie'
        self.url = url

    def get_by_id(self,id):
        url = (self.url + '/%s.json') %  id
        r = requests.get(url)
        if r.status_code == 404:
            return False
        result = r.json
        if result['term_type'] == 'ND':
            return self.get_by_id(result['use'])
        concept = {}
        concept['id'] = result['id']
        concept['labels'] = []
        concept['labels'].append({'type': 'pref', 'lang': result['language'], 'label': result['term']})
        concept['broader'] = [result['broader_term']]
        if 'narrower_terms' in result:
            concept['narrower'] = result['narrower_terms']
        if 'use_for' in result:
            for t in result['use_for']:
                term = self._get_term_by_id(t)
                concept['labels'].append({'type': 'alt', 'lang': term['language'], 'label': term['term']})
        if 'related_terms' in result:
            concept['related'] = result['related_terms']
        return concept

    def _get_term_by_id(self, id):
        '''Simple utility function to load a term.
        '''
        url = (self.url + '/%s.json') %  id
        r = requests.get(url)
        return r.json

    def find(self,query):
        return self._do_query(query)

    def get_all(self):
        return self._do_query()

    def _do_query(self,query=None):
        url = self.url + '/lijst.json'
        if query is not None:
            args = {'term': query['label']}
        else:
            args = {'type[]': ['HR', 'PT', 'NL']}
        r = requests.get(url, params=args)
        result = r.json
        return [{'id': x['id'], 'label': x['omschrijving']} for x in result['items']]

    def expand_concept(self,id):
        url = (self.url + '/%s/subtree.json') %  id
        r = requests.get(url)
        return r.json
