#!/bin/sh

filepath="../examples/"
templfiles="templ_bloodnormal.json templ_general.json templ_smoke.json templ_all.json "
datafiles="data_general.json data_bloodnormal.json data_smoke.json data_all.json"
otherfiles="offer.json trans.json"

for item in $templfiles
do
	./postdata -file $filepath$item
done

