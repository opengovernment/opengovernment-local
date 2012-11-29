# Open Government: Local

This is a temporary repository of scrapers written using [Billy](http://billy.readthedocs.org/) to collect legislative information from local governments in the United States.

## Getting Started

To get started, you may re-use [Open 13](https://github.com/opennorth/open13)'s excellent instructions, replacing `open13` where appropriate. Briefly, if you already have Git, Python 2.7 and virtualenvwrapper 1.7 or greater, then [fork this repository](https://github.com/opengovernment/opengovernment-local) and run:

```sh
git clone https://github.com/YOURUSERNAME/opengovernment-local.git
cd opengovernment-local
mkvirtualenv oglocal --system-site-packages
pip install -r requirements.txt
```

## Boundary Service

You do not need a boundary service to run the scrapers. If you have PostgreSQL and PostGIS:

```sh
createdb oglocal
psql oglocal -f /path/to/postgis.sql
psql oglocal -f /path/to/spatial_ref_sys.sql
cp local_settings.py.example local_settings.py
```

Then, edit `local_settings.py` with your PostgreSQL credentials and run:

```sh
python site/manage.py syncdb
```

## Running Scrapers

```sh
billy-update pa-philadelphia --fastmode
```

## Writing a Scraper

For now, see the [OpenStates documentation](http://openstates.org/contributing/).

## Bugs? Questions?

This project's main repository is on GitHub: [http://github.com/opengovernment/opengovernment-local](http://github.com/opengovernment/opengovernment-local), where your contributions, forks, bug reports, feature requests, and feedback are greatly welcomed.

Copyright (c) 2012 Participatory Politics Foundation, released under the MIT license
