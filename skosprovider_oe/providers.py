# -*- coding: utf-8 -*-

from skosprovider.providers import VocabularyProvider

from skosprovider.skos import (
    Concept,
    Collection
)

import requests

import warnings

from skosprovider.uri import UriPatternGenerator


class OnroerendErfgoedProvider(VocabularyProvider):
    '''A provider that can work with the REST-services of
    https://inventaris.onroerenderfgoed.be/thesaurus

    '''

    session = None
    '''
    A :class:`requests.Session`
    '''

    def __init__(self, metadata, **kwargs):
        if not 'default_language' in metadata:
            metadata['default_language'] = 'nl'
        if 'base_url' in kwargs:
            self.base_url = kwargs['base_url']
        else:
            self.base_url = 'https://inventaris.onroerenderfgoed.be/thesaurus/%s'
        if 'thesaurus' in kwargs:
            self.thesaurus = kwargs['thesaurus']
        else:
            self.thesaurus = 'typologie'
        if not 'url' in kwargs:
            self.url = self.base_url % self.thesaurus
        else:
            self.url = kwargs['url']
        self.session = requests.Session()
        super(OnroerendErfgoedProvider, self).__init__(metadata, **kwargs)

    def get_by_id(self, id):
        url = (self.url + '/%s.json') % id
        r = self.session.get(url)
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
            term = self._get_term_by_id(result['broader_term'])
            # Should not be possible, but you never know
            if term['term_type'] == 'ND': # pragma: no cover
                term = self._get_term_by_id(term['use'])
            if term['term_type'] == 'PT':
                concept['broader'] = [term['id']]
            else:
                concept['member_of'] = [term['id']]
                if 'broader_term' in term:
                    bt = self._get_term_by_id(term['broader_term'])
                else:
                    bt = False
                while bt:
                    if bt['term_type'] == 'PT':
                        concept['broader'] = [bt['id']]
                        bt = False
                    else:
                        if 'broader_term' in bt:
                            bt = self._get_term_by_id(bt['broader_term'])
                        else:
                            bt = False
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

    def get_by_uri(self, uri):
        warnings.warn(                                                          
            'This provider currently does not fully support URIs,\
             because the underlying service does not support them and URIs \
             have not been decided for these thesauri.',
             UserWarning                                                  
        )
        return False

    def _from_dict(self, concept):
        if concept['type'] == 'concept':
            return Concept(
                id = concept['id'],
                labels = concept['labels'] if 'labels' in concept else [],
                broader = concept['broader'] if 'broader' in concept else [],
                narrower = concept['narrower'] if 'narrower' in concept else [],
                related = concept['related'] if 'related' in concept else [],
                member_of = concept['member_of'] if 'member_of' in concept else []
            )
        else:
            return Collection(
                id = concept['id'],
                labels = concept['labels'] if 'labels' in concept else [],
                members = concept['members'] if 'members' in concept else [],
                member_of = concept['member_of'] if 'member_of' in concept else []
            )

    def _get_term_by_id(self, id):
        '''Simple utility function to load a term.
        '''
        url = (self.url + '/%s.json') % id
        r = self.session.get(url)
        return r.json()

    def find(self, query):
        return self._do_query(query)

    def get_all(self):
        return self._do_query()

    def get_top_concepts(self, **kwargs):
        language = self._get_language(**kwargs)
        url = self.url + '/lijst.json'
        args = {'type[]': ['HR']}
        r = self.session.get(url, params=args)
        result = r.json()
        items = result['items']
        top = self.get_by_id(items[0]['id'])
        res = []
        def expand_coll(res, coll):
            for nid in coll.members:
                c = self.get_by_id(nid)
                if isinstance(c, Collection):
                    res = expand_coll(res, c)
                else:
                    res.append({
                        'id': c.id,
                        'label': c.label(language)
                    })
            return res
        return expand_coll(res, top)

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
        r = self.session.get(url, params=args)
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
        r = self.session.get(url)
        if r.status_code == 404:
            return False
        return r.json()

    def get_top_display(self, **kwargs):
        '''
        Returns all concepts or collections that form the top-level of a display
        hierarchy.

        As opposed to the :meth:`get_top_concepts`, this method can possibly
        return both concepts and collections. 

        :rtype: Returns a list of concepts and collections. For each an
            id is present and a label. The label is determined by looking at 
            the `**kwargs` parameter, the default language of the provider 
            and falls back to `en` if nothing is present.
        '''
        language = self._get_language(**kwargs)
        url = self.url + '/lijst.json'
        args = {'type[]': ['HR']}
        r = self.session.get(url, params=args)
        result = r.json()
        items = result['items']
        top = self.get_by_id(items[0]['id'])
        res = []
        def expand_coll(res, coll):
            for nid in coll.members:
                c = self.get_by_id(nid)
                res.append({
                    'id': c.id,
                    'label': c.label(language)
                })
            return res
        return expand_coll(res, top)

    def get_children_display(self, id, **kwargs):
        '''
        Return a list of concepts or collections that should be displayed
        under this concept or collection.

        :param id: A concept or collection id.
        :rtype: A list of concepts and collections. For each an
            id is present and a label. The label is determined by looking at
            the `**kwargs` parameter, the default language of the provider 
            and falls back to `en` if nothing is present. If the id does not 
            exist, return `False`.
        '''
        language = self._get_language(**kwargs)
        item = self.get_by_id(id)
        res = []
        if isinstance(item, Collection):
            for mid in item.members:
                m = self.get_by_id(mid)
                res.append({
                    'id': m.id,
                    'label': m.label(language)
                })
        else:
            for cid in item.narrower:
                c = self.get_by_id(cid)
                res.append({
                    'id': c.id,
                    'label': c.label(language)
                })
        return res
