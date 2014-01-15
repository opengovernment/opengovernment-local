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
    #
    # Apparently terms must be defined in increasing time order due to
    # billy/importers/legislators.py def term_older_than
    #
    # https://github.com/jamesturk comments 
    # at https://github.com/sunlightlabs/billy/pull/242#issuecomment-22285710 state:
    # A term would be the shortest time that people can serve for in this case,
    # so you'd have a 2011-2013 (sic) term and a 2013-2016 (sic) term and some people would
    # automatically be in both and some would have faced an election between them. 
    # Staggered terms are a pain to model, but this approach has worked well for states.
    terms=[
        dict(name='2011-2012', start_year=2011, end_year=2012, sessions=['2012']),
        dict(name='2013-2014', start_year=2013, end_year=2014, sessions=['2013', '2014']),
    ],
    # The website organizes documents by year, so organize sessions by year.
    session_details={
        '2014': {
            'type': 'primary',
            'display_name': '2014 Legislative Session',
            '_scraped_name': '2014',
        },
        '2013': {
            'type': 'primary',
            'display_name': '2013 Legislative Session',
            '_scraped_name': '2013',
        },
        '2012': {
            'type': 'primary',
            'display_name': '2012 Legislative Session',
            '_scraped_name': '2012',
        },
    },
    # Minutes go to 1995. Agendas go to 2001.
    # (per http://www3.sanjoseca.gov/clerk/2011agenda.asp)
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

def strip_council_agendas_prefix(str):
    import string
    return string.replace(str, 'Council Agendas ', '')

def session_list():
    import lxml.html
    from scrapelib import urlopen
    from datetime import date
    import string

    # Start from City Clerk page
    city_clerk_url = 'http://sanjoseca.gov/index.aspx?NID=145'
    city_clerk_doc = lxml.html.fromstring(urlopen(city_clerk_url))
    city_clerk_doc.make_links_absolute(city_clerk_url)

    # Find current year
    current_year_url = city_clerk_doc.xpath('//td[//span]//a[contains(text(),"Council Agendas 2")]/@href')[0]
    current_year_doc = lxml.html.fromstring(urlopen(current_year_url))
    current_year_doc.make_links_absolute(current_year_url)

    current_year_text = current_year_doc.xpath('//tr[contains(@class, "telerik-reTableHeaderRow")]//td[contains(text(),"COUNCIL AGENDAS")]/text()')[0]
    current_year = string.split(current_year_text)[0]

    # Find agenda years
    council_agendas = map(string.strip, current_year_doc.xpath('//a[contains(text(),"Council Agendas 2")]/text()'))
    agenda_years = map(strip_council_agendas_prefix, council_agendas)

    # Find old archived years
    archives_url = current_year_doc.xpath("//a[contains(text(),'Archived Agendas')]/@href")[0]
    archives_doc = lxml.html.fromstring(urlopen(archives_url))
    archives_doc.make_links_absolute(archives_url)

    archived_council_agendas = map(string.strip, archives_doc.xpath('//table[./tr/td/div/strong[text()="Council Agendas/Synopses"]]//a/text()'))
    while archived_council_agendas.count('') > 0:
	archived_council_agendas.remove('')

    archived_council_minutes = map(string.strip, archives_doc.xpath('//table[./tr/td/div/strong[text()="Council Meeting Minutes"]]//a/text()'))
    while archived_council_minutes.count('') > 0:
	archived_council_minutes.remove('')

    aggregated_years = [current_year] + agenda_years + archived_council_agendas + archived_council_minutes
    unique_years     = list(set(aggregated_years))
    int_years        = map(int, unique_years)
    int_years.sort()
    session_years    = map(str, int_years)

    return session_years

# @todo def extract_text(doc, data):
