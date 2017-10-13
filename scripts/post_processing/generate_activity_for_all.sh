#!/bin/bash


for dir in $( ls DATA ); do

  echo  "dir: $dir";
  CONFIG=$( ls DATA/$dir/  |grep "ini" );
  
  echo "CONFIG: $CONFIG";
  ./runExp DATA/$dir/$CONFIG DATA/$dir/ generate 
	


done

