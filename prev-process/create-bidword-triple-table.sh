GROUP="hdp-guanggao"
table_name="huangjingwen_bidword_triple"

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
bidword_ori string,
bidword_seg string,
bidword_clean string
) 
PARTITIONED BY (ds string) 
ROW FORMAT DELIMITED 
FIELDS TERMINATED BY '\t' 
LINES TERMINATED BY '\n' 
STORED AS TEXTFILE;

insert overwrite table ${table_name} partition(ds='$DATE')
select t1.bidword, t1.seg, t2.clean from 
(
select bidword, seg from huangjingwen_bidword_seg where ds='${DATE}'
) t1
join
(
select bidword, clean from huangjingwen_bidword_clean where ds='${DATE}'
) t2
on
(
t1.bidword = t2.bidword
);
" | sudo -u $GROUP -E $HIVE_HOME/bin/hive > ./hive.log
