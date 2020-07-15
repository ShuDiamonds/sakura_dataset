# Untitled - By: shuichi-fu - 木 5月 14 2020
import sensor,image,lcd
import KPU as kpu
import uos
import time
lcd.init()
lcd.rotation(2)
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.set_windowing((224, 224))
sensor.set_vflip(1)
sensor.run(1)

classes = ["sakura"]
print(uos.listdir("/sd/") )

task = kpu.load("/sd/YOLO_best_mAP_75.kmodel")
kpu.set_outputs(task, 0,7,7,30)#Reshape層の内容に応じて中身を変える必要がある #the actual shape needs to match the last layer shape of your model(before Reshape)

anchor = (0.57273, 0.677385, 1.87446, 2.06253, 3.33843, 5.47434, 7.88282, 3.52778, 9.77052, 9.16828)
kpu.init_yolo2(task, 0.3, 0.3, 5, anchor)
#kpu.init_yolo2(task, 0.8, 0.9, 5, anchor)
print("start")
code=""
while(True):
    img = sensor.snapshot()#.rotation_corr(z_rotation=90.0)
    #a = img.pix_to_ai()
    code = kpu.run_yolo2(task, img)
    if code:
        for i in code:
            a=img.draw_rectangle(i.rect(),color = (0, 255, 0))
            a = img.draw_string(i.x(),i.y(), classes[i.classid()], color=(255,0,0), scale=3)
        a = lcd.display(img)
    else:
        a = lcd.display(img)
a = kpu.deinit(task)
