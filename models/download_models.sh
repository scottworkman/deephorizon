#!/usr/bin/env sh
#
# This script downloads and unpacks the model files, solver definitions, 
# and learned network weights for all networks described in the paper.

if [ $1 == '--demo' ]
then
  URL='http://amos.csr.uky.edu/modelzoo/deephorizon/deephorizon_single.zip'
else
  URL='http://amos.csr.uky.edu/modelzoo/deephorizon/deephorizon.zip'
fi
  
echo "Downloading..."

wget $URL -O 'deephorizon.zip'
  
echo "Unzipping..."

unzip deephorizon.zip

echo "Done."
