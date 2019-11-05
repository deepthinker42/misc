#!/bin/bash

SCRIPT=$(basename $BASH_SOURCE)
LOG=${SCRIPT%.*}.log

if [[ "x${1}" == "x" ]]; then
    echo -e "\nUsage:  ${SCRIPT} <alias>\n"
    exit 1
fi
if [[ ! -e ".keypass" ]]; then
    echo -e "\nStore password in .keypass file in this directory, then \"${SCRIPT} <alias>\"\n"
    exit 1
fi

#
# Read keypass file to get keypass and storepass
#
keypass=$(cat .keypass)
if [[ ${#keypass} -lt 6 ]]; then
    echo -e "\nPassword must be at least 6 characters\n"
    exit 1
fi

#
# Remove any previous keystore and truststore
#
rm -f $(hostname -s)-keystore.jks $(hostname -s)-truststore.jks

#
# Create the keystore
#
echo "Generating keystore" > ${LOG}
keytool -genkey -alias toros-server -keyalg RSA -keystore $(hostname -s)-keystore.jks -keysize 2048 -dname "EMAILADDRESS=${USER}@$(hostname -s), CN=$(hostname -s).ticom-geo.com, OU=Ticom Geomatics, O=Ticom Geomatics, ST=Texas, C=US" -storepass ${keypass} -keypass ${keypass} -noprompt >> ${LOG} 2>&1
if [[ $? -ne 0 ]]; then
    echo "Error creating keyststore.  See ${LOG} for details."
    exit 1
fi
echo $(hostname -s)-keystore.jks
echo $(hostname -s)-keystore.jks >> ${LOG}

#
# Create the cer used to create the truststore
#
echo "Generating cer" >> ${LOG}
keytool -export -alias toros-server -file $(hostname -s)-truststore.cer -keystore $(hostname -s)-keystore.jks -storepass ${keypass} -keypass ${keypass} -noprompt >> ${LOG} 2>&1
if [[ $? -ne 0 ]]; then
    echo "Error creating cer.  See ${LOG} for details."
    exit 1
fi

#
# Create the truststore
#
echo "Generating truststore" >> ${LOG}
keytool -import -trustcacerts -alias toros-server -file $(hostname -s)-truststore.cer -keystore $(hostname -s)-truststore.jks -storepass ${keypass} -keypass ${keypass} -noprompt >> ${LOG} 2>&1
if [[ $? -ne 0 ]]; then
    echo "Error creating truststore.  See ${LOG} for details."
    exit 1
fi
echo $(hostname -s)-truststore.jks
echo $(hostname -s)-trustystore.jks >> ${LOG}

#
# Cleanup
#
echo "Deleting cer and .keypass" >> ${LOG}
rm -f $(hostname -s)-truststore.cer .keypass ${LOG}
