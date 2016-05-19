#!/bin/bash
# 
# post-process.sh
# Written by Jingwen HUANG <huangjingwen@360.cn>
# Post-process of the query->bidword procedure.
#

success=0
err_wrong_args=85
err_run_time=1
brand_exclusion_script="brand-exclusion.py"
brand_exclusion_dict="category-brand.tsv"
location_exclusion_script="location-exclusion.py"
location_exclusion_dict="china-higher-location.tsv"
school_exclusion_script="school-exclusion.py"
school_exclusion_dict="school-with-synonym.tsv"
stock_exclusion_script="stock-exclusion.py"
stock_exclusion_dict="stock-seg-dict.tsv"

function usage ()
{
    echo "Usage: `basename $0` sim-file.tsv"
}

case "$1" in
    ""    ) usage; exit ${err_wrong_args};;
    *.tsv ) sim_file=${1};;
    *     ) usage; exit ${err_wrong_args};;
esac

# check arguments
if [ ! -e "${sim_file}" ]
then
    echo "File ${sim_file} dose not exists."
    exit ${err_wrong_args}
fi

if [ ! -f "${sim_file}" ]
then
    echo "File ${sim_file} is not a regular file."
    exist ${err_wrong_args}
fi

# check scripts to use (*.py)
if [ ! -f "${brand_exclusion_script}" ]
then
    echo "Script ${brand_exclusion_script} is not a regular file, or dose not exists."
    exit ${err_wrong_args}
fi

if [ ! -f "${location_exclusion_script}" ]
then
    echo "Script ${location_exclusion_script} is not a regular file, or dose not exists."
    exit ${err_wrong_args}
fi

if [ ! -f "${school_exclusion_script}" ]
then
    echo "Script ${school_exclusion_script} is not a regular file, or dose not exists."
    exit ${err_wrong_args}
fi

if [ ! -f "${school_exclusion_script}" ]
then
    echo "Script ${school_exclusion_script} is not a regular file, or dose not exists."
    exit ${err_wrong_args}
fi

# check dicts to use (*.tsv)
if [ ! -f "${brand_exclusion_dict}" ]
then
    echo "Dict ${brand_exclusion_dict} is not a regular file, or dose not exists."
    exit ${err_wrong_args}
fi

if [ ! -f "${location_exclusion_dict}" ]
then
    echo "Dict ${location_exclusion_dict} is not a regular file, or dose not exists."
    exit ${err_wrong_args}
fi

if [ ! -f "${school_exclusion_dict}" ]
then
    echo "Dict ${school_exclusion_dict} is not a regular file, or dose not exists."
    exit ${err_wrong_args}
fi

if [ ! -f "${school_exclusion_dict}" ]
then
    echo "Dict ${school_exclusion_dict} is not a regular file, or dose not exists."
    exit ${err_wrong_args}
fi

# check files to dump (*.tsv)
prefix=`basename "${sim_file%\.tsv}"`
brand_exclusion_file="${prefix}-brand-exclusion.tsv"
location_exclusion_file="${prefix}-brand-location-exclusion.tsv"
school_exclusion_file="${prefix}-brand-location-school-exclusion.tsv"
stock_exclusion_file="${prefix}-brand-location-school-stock-exclusion.tsv"
stock_exclusion_list="${prefix}-brand-location-school-stock-exclusion-list.tsv"
stock_exclusion_result="${prefix}-brand-location-school-stock-exclusion-result.tsv"

if [ -e "${brand_exclusion_file}" ]
then
    echo "File ${brand_exclusion_file} already exists."
    exit ${err_wrong_args}
fi

if [ -e "${location_exclusion_file}" ]
then
    echo "File ${location_exclusion_file} already exists."
    exit ${err_wrong_args}
fi

if [ -e "${school_exclusion_file}" ]
then
    echo "File ${school_exclusion_file} already exists."
    exit ${err_wrong_args}
fi

if [ -e "${stock_exclusion_file}" ]
then
    echo "File ${stock_exclusion_file} already exists."
    exit ${err_wrong_args}
fi

if [ -e "${stock_exclusion_list}" ]
then
    echo "File ${stock_exclusion_list} already exists."
    exit ${err_wrong_args}
fi

if [ -e "${stock_exclusion_result}" ]
then
    echo "File ${stock_exclusion_result} already exists."
    exit ${err_wrong_args}
fi

# brand exclusion
python ${brand_exclusion_script} ${brand_exclusion_dict} ${sim_file} > ${brand_exclusion_file}
if [ "${?}" -ne "${success}" ]
then
    echo "Brand exclusion error."
    exit ${err_run_time}
fi

# location exclusion
python ${location_exclusion_script} ${location_exclusion_dict} ${brand_exclusion_file} > ${location_exclusion_file}
if [ "${?}" -ne "${success}" ]
then
    echo "Location exclusion error."
    exit ${err_run_time}
fi

# school exclusion
python ${school_exclusion_script} ${school_exclusion_dict} ${location_exclusion_file} > ${school_exclusion_file}
if [ "${?}" -ne "${success}" ]
then
    echo "School exclusion error."
    exit ${err_run_time}
fi

# stock exclusion
python ${stock_exclusion_script} ${stock_exclusion_dict} ${school_exclusion_file} > ${stock_exclusion_file}
if [ "${?}" -ne "${success}" ]
then
    echo "Stock exclusion error."
    exit ${err_run_time}
fi
grep '### record replace ###' ${stock_exclusion_file} | sed 's/### record replace ###\t//g' | sort | uniq > ${stock_exclusion_list}
grep -v '### record replace ###' ${stock_exclusion_file} > ${stock_exclusion_result}
