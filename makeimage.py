import subprocess
import os

outputpath="./outputimages_raw/"
os.makedirs(outputpath,exist_ok=True)

moviepath="./movie/4444b/190407/" # 最後の「/」を忘れない！
date=moviepath.split('/')[-2]
carnum=moviepath.split('/')[-3]
print(moviepath.split('/'))
moviefilelist=sorted( os.listdir(moviepath))
moviefilelist_title=[x.split('.')[0] for x in moviefilelist ]
print(moviefilelist_title)
outputimagepath="./rawimages/{0}/{1}/".format(carnum,date)
for moviefilename in moviefilelist:
    #ffmpeg -i ./movie/元動画.mp4 -ss 144 -t 148 -r 1 -f image2 %06d.jpg
    args = ['ffmpeg', '-y','-i', moviepath+moviefilename, "-r","1","-f","image2",outputpath+"{0}_{1}_%03d.jpg".format(carnum,moviefilename.split('.')[0])]
    try:
        #print(args)
        res = subprocess.check_call(args)
    except:
        print("Error.")

#
# args = ['ls', '-l', '-a']
# try:
#     res = subprocess.check_call(args)
# except:
#     print "Error."
#=> "ls -l -a" の実行結果
