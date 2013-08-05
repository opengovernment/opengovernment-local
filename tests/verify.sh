#!/bin/bash

dump_local() {
  local username="$1"
  local password="$2"
  local locality_name="$3"

  local db_name="opengovernment_local"
  local tmpfile="/tmp/mongoquery-`date +%s`.js"

  #echo "db.legislators.find( { \"state\" : \"$locality_name\" }, { _id: 0, full_name: 1, first_name: 1, middle_name: 1, last_name: 1, suffixes: 1, gender: 1, district: 1, chamber: 1, roles: 1, url: 1, photo_url: 1, offices: 1, email: 1, sources: 1 } ).pretty()" > $tmpfile
  echo "db.legislators.find( { \"state\" : \"$locality_name\" }, { _id: 0, _type: 0, _all_ids: 0, created_at: 0, updated_at: 0, _scraped_name: 0, state: 0, leg_id: 0, party: 0, active: 0 } ).pretty()" > $tmpfile

  cat $tmpfile | mongo --username $username --password $password localhost:27017/$db_name | egrep -v MongoDB.shell.version\|connecting.to\|bye | more
  rm $tmpfile
}

username="$1"
password="$2"
locality_name="$3"

# Dump the MongoDB documents for locality_name and compare against saved text
dump_local $username $password $locality_name | diff - $locality_name.json
rc="$?"

if [ "$rc" = "0" ]; then
   echo "OK - $locality_name matches $locality_name.json"
else
   echo "ERROR - $locality_name differs from $locality_name.json"
fi
exit $rc

