# Open Government: Local

This is a temporary repository of scrapers written using [Billy](http://billy.readthedocs.org/) to collect legislative information from local governments in the United States.

_Note: Billy is officially depreciated. We do not currently recommend opengovernment-local to be used as a part of new projects._
## Getting Started

Briefly, if you already have Git, MongoDB, Python 2.7 and virtualenvwrapper 1.7 or greater, then [fork this repository](https://github.com/opengovernment/opengovernment-local) and run:

```sh
git clone https://github.com/YOURUSERNAME/opengovernment-local.git
cd opengovernment-local
mkvirtualenv oglocal
```

If you are not using the boundary service described below, comment out the following line in `requirements.txt`:

```
-e git+http://github.com/rhymeswithcycle/represent-boundaries.git#egg=represent-boundaries
```

Run `pip install -r requirements.txt` and you should be ready to go!

*Note:* If you encounter the error `Error: pg_config executable not found.`, the quick solution is to create a symlink to `pg_config`.

## Boundary Service

### Linux

Install geospatial libraries:

```sh
sudo apt-get install binutils libproj-dev gdal-bin
```

### All operating systems

Then, from the `opengovernment-local` directory, you can run:

```sh
cp site/local_settings.py.example site/local_settings.py
```

Then, edit `site/local_settings.py` with your PostgreSQL credentials and run:

```sh
python site/manage.py syncdb
python site/manage.py migrate
python site/manage.py loadshapefiles
```

The repository for OpenStates' shapefiles is [sunlightlabs/pentagon](https://github.com/sunlightlabs/pentagon).

## Running Scrapers

From the `opengovernment-local` directory:

```sh
billy-update pa-philadelphia --fastmode
billy-update ca-san-jose --fastmode
```

## Writing a Scraper

For now, see the [OpenStates documentation](http://openstates.org/contributing/).

## Running the Site

From the `opengovernment-local` directory:

```sh
python site/manage.py runserver
```

* Browse the web version at http://127.0.0.1:8000/
* Consult the scraper dashboard at http://127.0.0.1:8000/admin/
* Use the API according to the [OpenStates documentation](http://openstates.org/api/)

## Bugs? Questions?

This project's main repository is on GitHub: [http://github.com/opengovernment/opengovernment-local](http://github.com/opengovernment/opengovernment-local), where your contributions, forks, bug reports, feature requests, and feedback are greatly welcomed.

Copyright (c) 2012 Participatory Politics Foundation, released under the MIT license
