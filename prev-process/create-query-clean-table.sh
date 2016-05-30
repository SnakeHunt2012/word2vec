GROUP="hdp-guanggao"
table_name="huangjingwen_query_clean"

err_args=85

function usage ()
{
    echo "Usage: `basename $0` xxxx-xx-xx"
}

case "$1" in
    ""                    ) usage; exit ${err_args};;
    [0-9]*-[0-9]*-[0-9]*  ) DATE=$1;;
    *                     ) usage; exit ${err_args};;
esac

echo "
create external table if not exists ${table_name} (
query string,
clean string
) 
PARTITIONED BY (ds string) 
ROW FORMAT DELIMITED 
FIELDS TERMINATED BY '\t' 
LINES TERMINATED BY '\n' 
STORED AS TEXTFILE;

alter table ${table_name} drop if exists partition(ds='${DATE}');
alter table ${table_name} add partition(ds='${DATE}') location '/home/hdp-guanggao/huangjingwen/data/query-clean/ds=${DATE}';
" | sudo -u $GROUP -E $HIVE_HOME/bin/hive > ./hive.log
