#!/usr/bin/env sh
#
# This script downloads and unpacks the model files, solver definitions, 
# and learned network weights for all networks described in the paper.

if [ $1 == '--demo' ]
then
  URL='https://doc-0k-5g-docs.googleusercontent.com/docs/securesc/ha0ro937gcuc7l7deffksulhg5h7mbp1/ckv834bkjv3mph3pp341d45bg4jmt8pp/1472248800000/05018003348500916163/*/0BzEcTtT1A2ILcDZnU2lyVGV6TE0?e=download'
else
  URL='https://doc-10-5g-docs.googleusercontent.com/docs/securesc/ha0ro937gcuc7l7deffksulhg5h7mbp1/2m02fctjabc3jmo3mo1fqta8hr5nbj3l/1472248800000/05018003348500916163/*/0BzEcTtT1A2ILb2QzTkVHLXBiREE?e=download'
fi
  
echo "Downloading..."

wget $URL -O 'deephorizon.zip'
  
echo "Unzipping..."

unzip deephorizon.zip

echo "Done."
