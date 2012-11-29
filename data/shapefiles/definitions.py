from datetime import date

from boundaryservice import utils

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
        return u'%d%s' % (value, suffix)

SHAPEFILES = {
    # This key should be the plural name of the boundaries in this set
    'Philadelphia Council Districts': {
        # Path to a shapefile, relative to /data/shapefiles
        'file': 'pa-philadelphia/PhiladelphiaCouncilDistricts_2000.shp',
        # Generic singular name for an boundary of from this set
        'singular': 'Philadelphia Council District',
        # Should the singular name come first when creating canonical identifiers for this set?
        'kind_first': False,
        # Function which each feature wall be passed to in order to extract its "external_id" property
        # The utils module contains several generic functions for doing this
        'ider': lambda f: f.get('DIST_NAME'),
        # Function which each feature will be passed to in order to extract its "name" property
        'namer': ordinal_namer('DIST_NAME'),
        # Authority that is responsible for the accuracy of this data
        'authority': 'City of Philadelphia',
        # Geographic extents which the boundary set encompasses
        'domain': 'Philadelphia, PA',
        # Last time the source was checked for new data
        'last_updated': date(2012, 11, 29),
        # A url to the source of the data
        'href': 'http://www.pasda.psu.edu/philacity/data/PhiladelphiaCouncilDistricts_2000.zip',
        # Notes identifying any pecularities about the data, such as columns that were deleted or files which were merged
        'notes': '''Boundaries change in 2016. "Pennsylvania Spatial Data Access (PASDA) is Pennsylvania's official public access geospatial information clearinghouse".''',
        # Encoding of the text fields in the shapefile, i.e. 'utf-8'. If this is left empty 'ascii' is assumed
        'encoding': '',
        # SRID of the geometry data in the shapefile if it can not be inferred from an accompanying .prj file
        # This is normally not necessary and can be left undefined or set to an empty string to maintain the default behavior
        'srid': '',
        # Simplification tolerance to use when creating the simple_geometry
        # column for this shapefile, larger numbers create polygons with fewer
        # points.
        'simplification': 0.0001,
    }
}
