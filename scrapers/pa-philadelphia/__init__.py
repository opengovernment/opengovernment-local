# encoding: utf-8

from .legislators import PhiladelphiaLegislatorScraper

# @see http://billy.readthedocs.org/en/latest/metadata.html
# @see https://raw.github.com/sunlightlabs/openstates/master/openstates/pa/__init__.py
# @see https://raw.github.com/sunlightlabs/openstates/master/openstates/dc/__init__.py
metadata = dict(
    name='Philadelphia',
    abbreviation='pa-philadelphia',
    capitol_timezone='America/New_York',
    # http://en.wikipedia.org/wiki/Philadelphia_City_Council
    legislature_name='Philadelphia City Council',
    legislature_url='http://philadelphiacitycouncil.net/',
    # http://philadelphiacitycouncil.net/about-city-council/
    chambers={
        'upper': {'name': 'Council', 'title': 'Councilmember'},
    },
    # A councilmember's term is four years.
    terms=[
        dict(name='2012-2016', start_year=2012, end_year=2016, sessions=['2013', '2012']),
    ],
    # A new session begins January 2 of each year, according to media sources.
    session_details={
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
    # Transcripts go to 1997. Legislation and events go to 2000.
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
    ],
    feature_flags=[]
)

def session_list():
    from billy.scrape.utils import url_xpath
    return url_xpath(
        'http://legislation.phila.gov/council-transcriptroom/transroom_date.aspx',
        '//select[@id="ddlYear"]/option[position()>1]/text()'
    )

# @todo def extract_text(doc, data):
