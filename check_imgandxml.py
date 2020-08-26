# -*- coding: utf-8 -*-

import sys
import os
import re
from PIL import Image

if __name__ == '__main__':
    xmlfolderpath = "./ano_tmp/"

    imgfilepath = "./images/"


    outputxmlpath=xmlfolderpath+'output/'
    #os.makedirs(outputxmlpath, exist_ok=True)

    xmlfiles = [ x.split(".")[0] for x in sorted(os.listdir(xmlfolderpath)) if x!=".DS_Store" and x!="output"]
    imgfiles = [ x.split(".")[0] for x in sorted(os.listdir(imgfilepath)) if x!=".DS_Store"]
    imgfiles_exts=[ x.split(".")[-1] for x in sorted(os.listdir(imgfilepath)) if x!=".DS_Store"]

    #print(xmlfiles)
    #print(imgfiles)
    print("##################### check xml files")
    print(len(xmlfiles),len(imgfiles))
    for i,xmlfilename in enumerate(xmlfiles):
        if not xmlfilename in imgfiles:
            print( "Error: "+xmlfilename+ "."+imgfiles_exts[i] +" are not found. Please search it, or delete "+xmlfilename)
        #######
        with open(xmlfolderpath+xmlfilename+".xml") as f:
            rawfile = f.read()
        #print(xmlfilename)
        #print(rawfile)
        #print(re.findall("<width>\d{1,4}</width>",rawfile))
        print(re.findall("<xmax>\d{1,4}</xmax>",rawfile))
        if len(re.findall("<xmax>\d{1,4}</xmax>",rawfile))==0:
            print("ERROR: xml file exists, but No anottation on ",xmlfilename)
        width=int(re.sub(r"\D", "", re.findall("<width>\d{1,4}</width>",rawfile)[0])  )
        height=int( re.sub(r"\D", "", re.findall("<height>\d{1,4}</height>",rawfile)[0]) )
        xmax=int(re.sub(r"\D", "", re.findall("<xmax>\d{1,4}</xmax>",rawfile)[0])  )
        ymax=int(re.sub(r"\D", "", re.findall("<ymax>\d{1,4}</ymax>",rawfile)[0])  )
        if width<xmax:
            print("Error annotation: width<xmax:")
        if height<ymax:
            print("Error annotation: height<ymax:")
        targetfilename=re.findall("<filename>.*</filename>",rawfile)[0]

        ######### filename の変更
        rawfile=re.sub(r".png</filename>",r".jpg</filename>",rawfile)
        ######### <path>の削除
        rawfile=re.sub(r"<path>.*</path>","",rawfile)
        im = Image.open(imgfilepath+xmlfilename+"."+imgfiles_exts[i])
        img_width=int(im.size[0])
        img_height=int(im.size[1])

        if width!=img_width:
            print("different width ({0},{1}): {2}".format(width,img_width,imgfilepath+xmlfilename) )
        if height!=img_height:
            print("different height ({0},{1}): {2}".format(height,img_height,imgfilepath+xmlfilename) )

        # ファイルの書き込み
        # with open(outputxmlpath+xmlfilename+".xml",mode='w') as f:
        #     f.write(rawfile)


    print("##################### check img files")
    for i,imgfilename in enumerate(imgfiles):
        if not imgfilename in xmlfiles:
            print("Error: No annotation file. " + imgfilename + "."+imgfiles_exts[i]+  " will be deleted, [y/n] ")
            ans=input()
            if ans!="n":
                print(imgfilepath+imgfilename+"."+imgfiles_exts[i]+" is deleted.")
                os.remove( imgfilepath+imgfilename+"."+imgfiles_exts[i] )

            else:
                print(imgfilepath + imgfilename+"."+imgfiles_exts[i] + " is not deleted.")
