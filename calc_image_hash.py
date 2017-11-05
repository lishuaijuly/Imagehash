#!/usr/bin/env python
import sys
import cv2
import numpy  as np 
import os
import glob
import json
import time

def read_img(fname):
    return cv2.imread(fname,cv2.IMREAD_GRAYSCALE)

def calc_ahash(img,col_size=8,row_size=8):
    im =cv2.resize(img,(col_size,row_size),cv2.INTER_LINEAR)
    avg = im.mean()
    diff = im > avg
    return diff.flatten()

def calc_phash(img,col_size=8,row_size=8):
    im =cv2.resize(img,(col_size*4,row_size*4),cv2.INTER_LINEAR)
    dct = cv2.dct(np.float32(im))
    dct = dct[:col_size,:row_size]
    avg =  (dct.sum() - dct[0,0]) /(col_size* row_size)
    diff = dct > avg 
    return diff.flatten()

def calc_dhash(img,col_size=8,row_size=8):
    im =cv2.resize(img,(col_size+1,row_size),cv2.INTER_LINEAR)
    diff = im[:, :-1] > im[:, 1:]
    return diff.flatten()

"""
Demo of hashing
"""
def find_similar_images(userpath, hashfunc):
    images={}
    ori_images={}
    for f in glob.glob(userpath+"/ori/*"):
        if not f.endswith(".png") and  not f.endswith(".jpg") and not  f.endswith(".gif"):
            continue
        img = read_img(f)
        hash = np.array(hashfunc(img),dtype=np.int32)
        ori_images[os.path.basename(f)] = hash

    for f in glob.glob(userpath+"/*"):
        if not f.endswith(".png") and  not f.endswith(".jpg") and not  f.endswith(".gif"):
            continue
        img = read_img(f)
        hash = np.array(hashfunc(img),dtype=np.int32)
        images[os.path.basename(f)] = hash
        #print(hash)

    thres=0.75
    for img,hash in images.items():
        for ori,ori_hash in ori_images.items():
            if np.sum(np.equal(hash,ori_hash))/len(hash)> thres:
                print("{:30} : {:30} :{:10}".format(ori,img,round(np.sum(np.equal(hash,ori_hash))/len(hash),4))    )


def calc_dir_hash(userpath):
    image_hashs=[]
    a_time=0
    p_time=0
    d_time=0
    r_time=0
    for f in glob.glob(userpath+"/*"):
        if not f.endswith(".png") and  not f.endswith(".jpg") and not  f.endswith(".gif")  and not  f.endswith(".bmp"):
            continue
        one_image={}
        one_image['FileName'] = f

        btime=time.time()
        img = read_img(f)
        r_time=r_time+ time.time()-btime

        btime=time.time()
        hash =  np.array(calc_phash(img),dtype=np.int8)
        p_time=p_time+ time.time()-btime
        one_image['Phash'] = hex(int("".join([str(i) for i in hash]),2))[2:]


        
        btime=time.time()
        hash = np.array(calc_ahash(img),dtype=np.int8)
        a_time=a_time+ time.time()-btime
        one_image['Ahash'] = hex(int("".join([str(i) for i in hash]),2))[2:]

        btime=time.time()
        hash =  np.array(calc_dhash(img),dtype=np.int8)
        d_time=d_time+ time.time()-btime
        one_image['Dhash'] = hex(int("".join([str(i) for i in hash]),2))[2:]
        image_hashs.append(one_image)

    js = {}
    js['ImageFingerPrint']=image_hashs
    js['Key']='DEMO'
    js['version']='0.01'

    print("r-time:{},a-time:{},p-time:{},d-time:{}".format(r_time,a_time,p_time,d_time))
    with open('image_hash.json',mode='w') as fp:
        json.dump(js,fp,indent=2)    


if __name__ == '__main__':
    userpath = sys.argv[1] if len(sys.argv) > 1 else "."
    
    calc_dir_hash(userpath)
    
    print('\n\nahash:')
    #find_similar_images(userpath, calc_ahash)

    print('\n\nphash:')
    #find_similar_images(userpath, calc_phash)

    print('\n\ndhash:')
    #find_similar_images(userpath, calc_dhash)


