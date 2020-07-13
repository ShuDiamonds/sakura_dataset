# -*- coding: utf-8 -*-

import sys
import os
import re
from PIL import Image

if __name__ == '__main__':
    xmlfolderpath = "./../FishDB_annotations_png_xml/"
    #xmlfolderpath = "./../valid_xml/"

    #xmlfolderpath = "./../koura/xml/"
    #xmlfolderpath = "./../UnderwaterPhotography/xml/"
    imgfilepath = "./../FishDB_images_png/"
    #imgfilepath = "./../valid_img/"
    #imgfilepath = "./../koura/png/"
    #imgfilepath = "./../UnderwaterPhotography/nagisa_park/"

    imgfilepath = "./../smallfish/"
    xmlfolderpath = "./../smallfish_xml/"

    #outputxmlpath=xmlfolderpath+'output/'
    outputxmlpath=xmlfolderpath
    os.makedirs(outputxmlpath, exist_ok=True)

    xmlfiles = [ x.split(".")[0] for x in sorted(os.listdir(xmlfolderpath)) if x!=".DS_Store" and x!="output"]
    imgfiles = [ x.split(".")[0] for x in sorted(os.listdir(imgfilepath)) if x!=".DS_Store"]
    imgfiles_exts=[ x.split(".")[-1] for x in sorted(os.listdir(imgfilepath)) if x!=".DS_Store"]

    print(xmlfiles)
    #print(imgfiles)
    print("##################### check xml files")
    for i,xmlfilename in enumerate(xmlfiles):
        if not xmlfilename in imgfiles:
            print( "Error: "+xmlfilename+ "."+imgfiles_exts[i] +" are not found. Please search it, or delete "+xmlfilename)
        #######
        with open(xmlfolderpath+xmlfilename+".xml") as f:
            rawfile = f.read()
        #print(xmlfilename)
        #print(rawfile)
        #print(re.findall("<width>\d{1,4}</width>",rawfile))
        width=int(re.sub(r"\D", "", re.findall("<width>\d{1,4}</width>",rawfile)[0])  )
        height=int( re.sub(r"\D", "", re.findall("<height>\d{1,4}</height>",rawfile)[0]) )
        xmax=int(re.sub(r"\D", "", re.findall("<xmax>\d{1,4}</xmax>",rawfile)[0])  )
        ymax=int(re.sub(r"\D", "", re.findall("<ymax>\d{1,4}</ymax>",rawfile)[0])  )
        if width<xmax:
            print("Error annotation: width<xmax:")
        if height<ymax:
            print("Error annotation: height<ymax:")
        targetfilename=re.findall("<filename>.*</filename>",rawfile)[0]
        #print(targetfilename)
        #print(rawfile)
        ######### filename の変更
        rawfile=re.sub(r".png</filename>",r".jpg</filename>",rawfile)
        #print(rawfile)
        ######### <path>の削除
        rawfile=re.sub(r"<path>.*</path>","",rawfile)
        im = Image.open(imgfilepath+xmlfilename+"."+imgfiles_exts[i])
        #print(im.size)
        img_width=int(im.size[0])
        img_height=int(im.size[1])

        if width!=img_width:
            print("different width ({0},{1}): {2}".format(width,img_width,imgfilepath+xmlfilename) )
        if height!=img_height:
            print("different height ({0},{1}): {2}".format(height,img_height,imgfilepath+xmlfilename) )

        # ファイルの書き込み
        with open(outputxmlpath+xmlfilename+".xml",mode='w') as f:
            f.write(rawfile)


    print("##################### check img files")
    for i,imgfilename in enumerate(imgfiles):
        if not imgfilename in xmlfiles:
            print("Error: No annotation file. " + imgfilename + "."+imgfiles_exts[i]+  " will be deleted, [y/n] ")
            ans=input()
            if ans=="y":
                print(imgfilepath+imgfilename+"."+sorted(os.listdir(imgfilepath))[i].split(".")[1]+" is deleted.")
                os.remove( imgfilepath+imgfilename+"."+sorted(os.listdir(imgfilepath))[i].split(".")[1] )

            else:
                print(imgfilepath + imgfilename+"."+sorted(os.listdir(imgfilepath))[i].split(".")[1] + " is not deleted.")
