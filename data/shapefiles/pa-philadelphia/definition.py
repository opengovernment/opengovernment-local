from datetime import date

import boundaries

class ordinal_namer():
    def __init__(self, name):
        self.name = name

    def __call__(self, feature):
        value = int(feature.get(self.name))
        if value % 100 // 10 == 1:
            suffix = 'th'
        else:
            if value % 10 == 1:
                suffix = 'st'
            elif value % 10 == 2:
                suffix = 'nd'
            elif value % 10 == 3:
                suffix = 'rd'
            else:
                suffix = 'th'
        return u'%d%s District' % (value, suffix)

boundaries.register('Philadelphia Council Districts',
    domain='Philadelphia, PA',
    last_updated=date(2012, 11, 29),
    name_func=ordinal_namer('DIST_NUM'),
    id_func=boundaries.attr('DIST_NUM'),
    authority='City of Philadelphia',
    source_url='http://www.opendataphilly.org/opendata/resource/13/city-council-districts-2000-active/',
    data_url='http://www.pasda.psu.edu/philacity/data/PhiladelphiaCouncilDistricts_2000.zip',
    notes='''Boundaries change in 2016. "Pennsylvania Spatial Data Access (PASDA) is Pennsylvania's official public access geospatial information clearinghouse".''',
)
