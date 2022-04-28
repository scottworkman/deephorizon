#!/bin/bash
#
# This script downloads and unpacks the model files, solver definitions, 
# and learned network weights for all networks described in the paper.

if [ "$1" == '--demo' ]
then
  URL='https://wustl.box.com/shared/static/0s5xli5uisxn4x138oxybc9l28n5whpy.zip'
else
  URL='https://wustl.box.com/shared/static/kk7hcdsp82s4nv53cckxce26xhroggnu.zip'
fi
  
echo "Downloading..."

wget $URL -O 'deephorizon.zip'
  
echo "Unzipping..."

unzip deephorizon.zip

echo "Done."
