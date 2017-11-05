#-*- coding:utf-8 -*-
'''
抓取任意开放网站上的图片，单线程，抓取一张休息一秒. 构建图片数据集，用来测试。
1、只搜索这一个网站上的，外链不搜索
2、
输入：网站主域名 ，保存目录
输出: 保存图片和图片hash，。

。。。通用的抓取器不好写，还是写专用的抓取器吧

'''
import re
import os
import urllib.request
import queue 
import hashlib
from bs4 import BeautifulSoup
import time
import pickle
import socket
import re
import random
import logging
from http.cookiejar import CookieJar

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',level=logging.DEBUG)

start_url = 'http://www.zhangzishi.cc/page/'

timeout = 5
socket.setdefaulttimeout(timeout)
header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36"
        , "Connection": "keep-alive"
        , "Referer": "image / webp, image / *, * / *;q = 0.8"
        ,"Accept":"image/webp,image/*,*/*;q=0.8"
}
BLACK_IMG=['jjnoholiday.jpg']

cj = CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
def fetch_data(url):
    data = None
    try:
        logging.debug('FETCH {} begin.'.format(url))
        req = urllib.request.Request(url ,headers=header)
        response = opener.open(req)
        data = response.read() #.decode('utf8', errors='ignore')
        response.close()
    except socket.timeout:
        logging.warn('FETCH {} timeout.'.format(url))
        time.sleep(random.randint(20,40))
    except urllib.error.HTTPError:
        logging.warn('FETCH {} HTTPError.'.format(url))
    except Exception as err:
         logging.warn('FETCH {} :{}.'.format(url,err))
    else:
        logging.debug('FETCH {} end.'.format(url))

    return data

def fetch_pages(start_url,page_idx,fetch_num=40):
    pages={}
    start_page_idx  =page_idx
    try:
        for i in range(start_page_idx,start_page_idx+fetch_num):
            data = fetch_data(start_url+str(i))
            if data == None:
                continue
            soup = BeautifulSoup(data,"html5lib")
            articles = soup.findAll("article")
            for article  in articles:
                title= article.findAll('a',text=True)[0].get_text()
                title = re.sub(r'[\s+\.\!\/_,$%^*(+\"\'\]+|\[+——！，。？?、~@#￥%……&*（）：:「」·”“《》‘’ \t\n『』]+', "",title)[:15]
                link = article.findAll('a','thumbnail')[0].get('href')
                pages[link]=title
                logging.debug(title)
                
            page_idx = i
            time.sleep(random.randint(1,3))
    except:
        logging.warn('IDX process [{}] error.'.format(start_url+str(i)))
    return pages,page_idx,

def fetch_img(pages,done_imgs,done_urls):
    try:
        for link,title in pages.items():
            if link in done_urls:
                logging.info('DONE_URLS :{}'.format(link))
                continue
            img_idx=0
            data = fetch_data(link)
            if data == None:
                continue
            soup = BeautifulSoup(data,"html5lib")
            imgs = soup.find_all('article')[0].find_all('img')
            dirname = './data/{}'.format(title)
            for img in imgs:
                img = img.get('src')
                suffix = img.split('.')[-1].lower()
                if suffix != 'jpg' and  suffix != 'gif' and suffix != 'png' and suffix != 'bmp' and suffix != 'jpeg' :
                    logging.info('ERROR IMG :{}'.format(img))
                    continue
                    
                if os.path.basename(img) in BLACK_IMG:
                    continue

                if not img.startswith('http'):
                    logging.info('ERROR IMG :{}'.format(img))
                    continue

                bimg = fetch_data(img)
                if bimg==None:
                    continue

                imd5=hashlib.md5(bimg).hexdigest()
                if imd5 in done_imgs:
                    logging.info('DONE_IMGS :{}'.format(img))
                    continue
                done_imgs.add(imd5)

                if not os.path.isdir(dirname):
                    os.mkdir(dirname)
                
                with  open('{}/{}.{}'.format(dirname,img_idx,suffix), "wb") as f :
                    f.write(bimg)
                img_idx +=1
            
            done_urls.add(link)
            time.sleep(random.randint(3,10))
    except RuntimeError:
        logging.warn('PAGE process [{}] error.'.format(link))
    return done_imgs,done_urls

if __name__ =='__main__':
    if os.path.isfile('./data/md5'):
        with  open('./data/md5','rb') as fp:
            (page_idx,done_imgs,done_urls) = pickle.load(fp)
    else:
       page_idx = 1
       done_imgs= set()
       done_urls=set()


    #获取页面链接并保存
    pages,page_idx = fetch_pages(start_url,page_idx)

    done_imgs,done_urls = fetch_img(pages,done_imgs,done_urls)

    with  open('./data/md5','wb') as fp:
        pickle.dump((page_idx,done_imgs,done_urls),fp)
    
    
