#!/usr/bin/env bash

(
cd /home/bitcoin/nodeyez/data/compassminingstatus/
for DCountry in */
do
    echo "Processing ${DCountry}"
    cd ${DCountry}
    for DFacility in */
    do
        echo "Processing ${DFacility}"
        cd ${DFacility}
        for f in $(ls *.html)
        do
            thejson=`cat ${f} | grep data-react-props | grep -Po '^.{61}\K.*' | sed -e 's@"></div>@@' | sed -e 's/&quot;/"/g'`
            monthcount=`echo $thejson | jq -r ' .months | length'`
            #for loop the months
            for (( m=0; m<${monthcount}; m++ ))
            do
                yearmonth=`echo $thejson | jq -r ' .months['${m}'].days[0] | .date | split("-") | .[0]+"-"+.[1] ' `
                echo Extracting data for ${yearmonth} into ${yearmonth}.json
                echo $thejson | jq -r ' .months['${m}']' > ${yearmonth}.json
            done
        done
        cd ..
    done
    cd ..
done
)
