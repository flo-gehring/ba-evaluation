#! /bin/bash
echo SMOT
python3 evaluate.py ../data/eval_root/groundtruths/ ../data/eval_root/SMOT/
echo PANORAMA_TRACKER
python3 evaluate.py ../data/eval_root/groundtruths/ ../data/eval_root/PANORAMA_TRACKER/
echo DEEPSORT
python3 evaluate.py ../data/eval_root/groundtruths/ ../data/eval_root/DEEPSORT/
