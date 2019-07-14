# scrapy-learn
# Anime figure crawler

1. download and install anaconda

useful commands:
conda info --envs
conda env remove --name test123

2. create a environment
conda create -n crawlerEnv
conda activate crawlerEnv

3. install scrapy
conda install -c conda-forge scrapy

run conda list, you should see scrapy package

4. scrapy tutorial
https://docs.scrapy.org/en/latest/intro/tutorial.html

5. How to set up debugger for scrapy in PyCharm
(1) script path: C:\Users\yuqing\Anaconda3\envs\crawlerEnv\Scripts\scrapy-script.py
(2) parameter: crawl spider_name      no surrounding quotes!
(3) set the correct working directory!

6. remember to use double quote when use Scrapy shell
(1)scrapy shell "https://www.bigbadtoystore.com/lists?pageIndex=11&ListId=35"
(2)then run response.xpath()

7.
Pseudo-elements don't exist in the DOM tree (hence the name), therefore they cannot be selected with XPath