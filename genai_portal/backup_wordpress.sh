#!/bin/bash

TZ='Asia/Shanghai' 
TS=`date '+%Y%m%d-%H%M%S'`

WP_PATH="/home/ubuntu/genai-portal/"
WP_TAR="/tmp/wordpress.${TS}.tar.gz"
WP_DB="/tmp/wordpress.db.${TS}.log"
WP_DB_TAR="/tmp/wordpress.db.${TS}.log.tar.gz"
CIFS_PATH="/home/ansible/yulu/cifs_data/luyu/Gen-AI/portal/"

echo "the TS:${TS}"
#1.backup the wordpress site
echo "1.backup the wordpress site: WP_TAR is ${WP_TAR}, WP_PATH is ${WP_PATH}"
tar -czvf ${WP_TAR} -C ${WP_PATH} wordpress 

#2.backup the wordpress database
sudo mysqldump -uroot  --databases wordpress > ${WP_DB} 
tar -czvf ${WP_DB_TAR} ${WP_DB}

#3.mv to cifs_data
echo "3.mv to cifs_data:"
echo "3.1 WP_TAR is ${WP_TAR}, CIFS_PATH is ${CIFS_PATH}"
mv ${WP_TAR} ${CIFS_PATH}
echo "3.2 WP_DB_TAR is ${WP_DB_TAR}, CIFS_PATH is ${CIFS_PATH}"
mv ${WP_DB_TAR} ${CIFS_PATH}

echo "finish the Backup for ${WP_TAR} and ${WP_DB_TAR} in ${CIFS_PATH}"
echo -e "\n\n\n"
