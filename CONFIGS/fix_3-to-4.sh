#!/bin/bash

for f in $( ls |grep "4" | grep -v "fix" ); do

	cat $f | sed "s/networkSize = 3/networkSize = 4/" > temp
	cat temp > $f
done

rm temp