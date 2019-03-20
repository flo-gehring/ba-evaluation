#! /bin/bash

sots=( "Boosting" "KCF" "MedianFlow" "MIL" "MOSSE" "TLD" )
for i in "${sots[@]}"
do
	echo $i
	python3 evaluate.py ../data/eval_root/SOT2/groundtruths/ ../data/eval_root/SOT2/$i
	
done
#echo SMOT
# 
