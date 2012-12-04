# encoding: utf-8
from datetime import date

import boundaries

boundaries.register(u'San José Council Districts',
    domain=u'San José, CA',
    last_updated=date(2012, 12, 4),
    name_func=lambda f: 'District %s' % f.get('DISTRICTS'),
    id_func=boundaries.attr('DISTRICTS'),
    authority=u'City of San José',
    source_url='http://www.sanjoseca.gov/index.aspx?NID=3308',
    data_url='http://www.sanjoseca.gov/DocumentCenter/View/9266',
    notes='Boundaries change every 10 years according to the census.',
)
