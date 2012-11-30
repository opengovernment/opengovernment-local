from datetime import date

import boundaries

boundaries.register('Pennsylvania Places',
    domain='Pennsylvania',
    last_updated=date(2012, 11, 29),
    name_func=boundaries.attr('NAME'),
    id_func=boundaries.attr('GEOID'),
    slug_func=boundaries.attr('GEOID'),
    authority='United States Census Bureau',
    source_url='http://www.census.gov/cgi-bin/geo/shapefiles2012/main',
    data_url='http://www2.census.gov/geo/tiger/TIGER2012/PLACE/tl_2012_42_place.zip',
)
