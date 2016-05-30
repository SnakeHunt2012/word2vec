GROUP="hdp-guanggao"
table_name="huangjingwen_query_triple"

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
query_ori string,
query_seg string,
query_clean string
) 
PARTITIONED BY (ds string) 
ROW FORMAT DELIMITED 
FIELDS TERMINATED BY '\t' 
LINES TERMINATED BY '\n' 
STORED AS TEXTFILE;

insert overwrite table ${table_name} partition(ds='$DATE')
select t1.query, t1.seg, t2.clean from 
(
select query, seg from huangjingwen_query_seg where ds='${DATE}'
) t1
join
(
select query, clean from huangjingwen_query_clean where ds='${DATE}'
) t2
on 
(
t1.query = t2.query
);
" | sudo -u $GROUP -E $HIVE_HOME/bin/hive > ./hive.log
