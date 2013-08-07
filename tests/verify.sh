#!/bin/bash


# Usage:   ./verify.sh <locality-name> <mongo-username> <mongo-password>
# Example: ./verify.sh ca-san-jose     mymongouser      mymongopswd


dump_local() {
  local locality_name="$1"
  local username="$2"
  local password="$3"

  local db_name="opengovernment_local"
  local tmpfile="/tmp/mongoquery-`date +%s`.js"

  #echo "db.legislators.find( { \"state\" : \"$locality_name\" }, { _id: 0, full_name: 1, first_name: 1, middle_name: 1, last_name: 1, suffixes: 1, gender: 1, district: 1, chamber: 1, roles: 1, url: 1, photo_url: 1, offices: 1, email: 1, sources: 1 } ).sort( { last_name: 1, first_name: 1 } ).pretty()" > $tmpfile
  echo "db.legislators.find( { \"state\" : \"$locality_name\" }, { _id: 0, _type: 0, _all_ids: 0, created_at: 0, updated_at: 0, _scraped_name: 0, state: 0, leg_id: 0, party: 0, active: 0 } ).sort( { last_name: 1, first_name: 1 } ).pretty()" > $tmpfile

  cat $tmpfile | mongo --username $username --password $password localhost:27017/$db_name | egrep -v MongoDB.shell.version\|connecting.to\|bye | more
  rm $tmpfile
}

locality_name="$1"
username="$2"
password="$3"

# Dump the MongoDB documents for locality_name and compare against saved text
dump_local $locality_name $username $password | diff - `dirname $0`/$locality_name.json
rc="$?"

if [ "$rc" = "0" ]; then
   echo "OK - $locality_name matches $locality_name.json"
else
   echo "ERROR - $locality_name differs from $locality_name.json"
fi
exit $rc

