#!/bin/bash

retailers=("target" "samsclub" "dollargeneral" "cvs" "walgreens" "walmart")

#retailers=("walgreens")

for i in "${!retailers[@]}";do
	scrapy crawl ${retailers[$i]}
done


