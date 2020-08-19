# m5stickV のファームウェアバージョン
from machine import UART
from board import board_info
from fpioa_manager import fm
from Maix import GPIO
import KPU as kpu
import sensor, lcd
import time
import uos
import sys


lcd.init()
lcd.rotation(2) #Rotate the lcd 180deg

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
#sensor.set_vflip(1)
#sensor.set_hmirror(1)
sensor.set_windowing((224, 224))
sensor.run(1)
sensor.skip_frames()

modelpath="/sd/fish_detect_v01.kmodel"

fm.register(35, fm.fpioa.UART1_TX, force=True)
fm.register(34, fm.fpioa.UART1_RX, force=True)
uart = UART(UART.UART1, 1152000,8,0,0, timeout=1000, read_buf_len=4096)

def CreateDatapacket(datasize,filename="hoge.jpg"):
    #print("CreateDatapacket")
    data_size1 = (datasize& 0xFF0000)>>16
    data_size2 = (datasize& 0x00FF00)>>8
    data_size3 = (datasize& 0x0000FF)>>0
    tmp=filename.encode()
    padding=list(tmp)+[0x00]*(40-len(tmp))
    tmp=[0xFF,0xD8,0xEA,0x01,data_size1,data_size2,data_size3,0x00,0x00,0x00]+padding
    #print("padding",len(tmp),tmp)
    data_packet = bytearray([0xFF,0xD8,0xEA,0x01,data_size1,data_size2,data_size3,0x00,0x00,0x00]+padding)
    return data_packet

classes = ["smallfish","mebaru","azi","hugu","ishidai","kasago","bera","kawahagi","tai","hamati","kurodai","kisu","gure","sayori","suzuki"]
print(uos.listdir("/sd/") )

# KPU setting
#kpu.deinit(task)
try:
    task = kpu.load(modelpath)
except:
    kpu.deinit(task)
    task = kpu.load(modelpath)
kpu.set_outputs(task, 0,7,7,100)#Reshape層の内容に応じて中身を変える必要がある #the actual shape needs to match the last layer shape of your model(before Reshape)
anchor = (0.57273, 0.677385, 1.87446, 2.06253, 3.33843, 5.47434, 7.88282, 3.52778, 9.77052, 9.16828)
kpu.init_yolo2(task, 0.3, 0.3, 5, anchor)

pic_filepath="/sd/fish_pic"
try:
    uos.mkdir(pic_filepath)
except:
    print(uos.listdir(pic_filepath) )

cnt=0
while(True):
    try:
        img = sensor.snapshot()
        code = kpu.run_yolo2(task, img)
    except:
        continue
    if code:
        fishnames=""
        for fishobj in code:
            a=img.draw_rectangle(fishobj.rect(),color = (0, 255, 0))
            a = img.draw_string(fishobj.x(),fishobj.y(), classes[fishobj.classid()], color=(255,0,0), scale=3)
            fishnames=fishnames+classes[fishobj.classid()]+"_"
        a = lcd.display(img)
        filename = pic_filepath+"/{0}__{1}.jpg".format(fishnames,cnt) # 00000000.jpg から連番
        print(filename)
        img.save(filename,quality=30)
        cnt=cnt+1
    #lcd.display(img)
    mpt = uart.read()
    if mpt == b'P':
        filename = "/sd/fish_pic/{0:0=8}.jpg".format(i) # 00000000.jpg から連番
        print(filename)
        img.save(filename,quality=30)
        i=i+1
    if mpt == b'A':
        print("mpt",mpt)
        img_buf = img.compress(quality=50)
        data_packet=CreateDatapacket(img.size())
        uart.write(data_packet)
        lcd.draw_string(100,50,"write img_buf", lcd.RED, lcd.WHITE)    #LCDに文字描画
        time.sleep(0.01)
        uart.write(img_buf)
        #time.sleep(3)
    if mpt == b'L':
        print("mpt",mpt)
        try:
            filelistbuf = ",".join( uos.listdir("/sd/") )
        except:
            filelistbuf="No file is found"
            print("No file is found")
        print(filelistbuf)
        print("sizeof:", len(filelistbuf.encode()) )
        uart.write(CreateDatapacket( len(filelistbuf.encode()) ) )
        time.sleep(0.01)
        uart.write(filelistbuf)
    if mpt == b'G':
        print("mpt",mpt)
        time.sleep(0.2)
        filesizecnt=0
        targetfilename=uos.listdir(pic_filepath)[0]
        try:
            openfile=pic_filepath+'/'+targetfilename
            #openfile="sample.jpg"
            f = open(openfile,"r")
            while 1:
                avifile=f.read(3000)
                avifilelen=len(avifile.encode())
                filesizecnt=filesizecnt+avifilelen
                uart.write(CreateDatapacket( avifilelen,targetfilename ) )
                print("endCreateDatapacket")
                time.sleep(0.03)
                uart.write(avifile)
                print("avifilelen",avifilelen)
                if avifilelen < 1:
                    print("end sending ",filesizecnt)

                    break
                time.sleep(0.3)
                count =0
                breakflag=False
                while uart.read()!=b'+':
                    time.sleep(0.01)
                    count=count+1
                    if count>500:
                        print("count up")
                        breakflag=True
                        break
                if breakflag:
                    print("count up breakflag")
                    breakflag=False
                    break
            f.close()
            uos.remove(openfile)
        except Exception as e:
            avifile="No file is found"
            print("No file is found",e)



a = kpu.deinit(task)



