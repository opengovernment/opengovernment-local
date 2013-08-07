# encoding: utf-8

from .legislators import SanJoseLegislatorScraper

metadata = dict(
    name=u'San José',
    abbreviation='ca-san-jose',
    capitol_timezone='America/Los_Angeles',
    # http://en.wikipedia.org/wiki/San_Jose_City_Council
    legislature_name=u'San José City Council',
    legislature_url='http://www.sanjoseca.gov/',
    chambers={
        'upper': {'name': 'Council', 'title': 'Councilmember'},
    },
    # The mayor and councilmembers are elected to four-year terms. The mayor and
    # the odd-numbered district councilmembers begin in 2011. The even-numbered
    # district councilmembers begin in 2009.
    terms=[
        dict(name='2011-2012', start_year=2011, end_year=2012, sessions=['2012']),
    ],
    # The website organizes documents by year, so organize sessions by year.
    session_details={
        '2012': {
            'type': 'primary',
            'display_name': '2012 Legislative Session',
            '_scraped_name': '2012',
        },
    },
    # Minutes go to 1995. Agendas go to 2001.
    _ignored_scraped_sessions=[
        '2011',
        '2010',
        '2009',
        '2008',
        '2007',
        '2006',
        '2005',
        '2004',
        '2003',
        '2002',
        '2001',
        '2000',
        '1999',
        '1998',
        '1997',
        '1996',
        '1995',
    ],
    feature_flags=[]
)

def session_list():
    import lxml.html
    from scrapelib import urlopen
    from datetime import date

    url = 'http://www3.sanjoseca.gov/clerk/agenda.asp'
    doc = lxml.html.fromstring(urlopen(url))
    doc.make_links_absolute(url)

    timespan = next(text for text in doc.xpath('//text()[contains(.,"Meeting")][contains(.,"Minutes")]/following::text()') if text.strip())
    start = int(timespan.split('-', 1)[0])
    return map(str, range(start, date.today().year))

# @todo def extract_text(doc, data):
