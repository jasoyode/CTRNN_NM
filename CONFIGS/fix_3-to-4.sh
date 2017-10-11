#!/bin/bash

for f in $( ls |grep "5" | grep -v "fix" ); do

	cat $f | sed "s/networkSize = 3/networkSize = 5/" > temp
	cat temp > $f
done

rm temp