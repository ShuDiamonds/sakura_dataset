# manage.py


import os
import datetime
from flask import Flask
from flask import render_template, Blueprint, url_for, \
    redirect, flash, request
from flask_cors import CORS # <-追加


import socket
import sys
import base64, json
import select
import threading

# ここでACCとGPSの全体データの表示
app = Flask(__name__)
CORS(app) # <-追加

@app.route('/')
def home():
    return render_template('AICAM/index.html')

@app.route('/os/')
def filelist_os():
    try:
        jsonlist=list()
        macadresslists = os.listdir("./static/reciv_data/")
        for MacAdress in macadresslists:
            filelists = [MacAdress+"/"+x for x in os.listdir("./static/reciv_data/{0}/".format(MacAdress))]
            jsonlist.extend(filelists)

        return json.dumps(jsonlist)
    except Exception as e:
        print(e)
        return "os ERROR"


@app.route('/AICAM/img/<mac_ad>/<pic_name>',methods=["GET"])
def AICAM_img(mac_ad,pic_name):
    if len(mac_ad)!=12:
        return ""
    return redirect('http://{0}:44445/static/{1}/{2}'.format(serveripadress,mac_ad,pic_name ))


def Flask_main():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
    print("flask start on Flask_main")


######### ここから　TCPで画像を受け取るサーバの処理
# サーバーIPアドレス定義
TCP_imgserver_host = "0.0.0.0"
# サーバーの待ち受けポート番号定義
TCP_imgserver_port = 44446

# 受信画像保存ディレクトリ
sc_dir = 'static/reciv_data/'
os.makedirs(sc_dir,exist_ok=True)
# 受信画像ファイル名
sc_file = 'sc_file.jpg'
def recv_client_data(clientsock,address):
    print(" ########## recv_client_data ##########")
    def RaiseError(msg,clientsock):
        print("ERROR: dofferent pass")
        clientsock.close()
        exit()
    # 受信データ保存用変数の初期化
    all_data = bytes()
    try:
        # ソケット接続開始後の処理
        fileinfo = clientsock.recv(100)
        try:
            print("filename",fileinfo)
            sc_file=fileinfo.decode()
        except:
            sc_file=str(fileinfo)
            sc_file=sc_file.split(".jpg")[0][2:]+".jpg"
            print("EEror:sc_file",sc_file)
        if not(sc_file.split('.')[-1] in ["jpg","avi"]):
            RaiseError("error filename, close thread.",clientsock)
        # print("filenameb64",sc_file)
        #MACアドレスとパスワードを確認
        try:
            MACandPASS = clientsock.recv(30)
            print("MACandPASS:",str(MACandPASS))
            MACandPASS=MACandPASS.decode()
            print("MACandPASS",MACandPASS)
            macadress=MACandPASS.split(",")[0]
            if len(macadress)!=12 or  '.' in macadress:
                RaiseError("ERROR: dofferent MAC",clientsock)
            PASSword=MACandPASS.split(",")[-1]
            if PASSword!="0hqhf0j==fak;=0fq":
                RaiseError("ERROR: dofferent pass",clientsock)

            imgfilepath=sc_dir+macadress+"/"
            os.makedirs(imgfilepath,exist_ok=True)

        except Exception as e:
            print(u'ERROR:MACandPASS')
            print(e)

        while True:
            # データ受信。受信バッファサイズ1024バイト
            data = clientsock.recv(1024)
            # 全データ受信完了（受信路切断）時に、ループ離脱
            if not data:
                break
            # 受信データを追加し繋げていく
            all_data += data
        if len(all_data)==0:
            RaiseError("ERROR: None image data",clientsock)
        # 受信画像ファイル保存
        with open(imgfilepath + sc_file, 'wb') as f:
            # ファイルにデータ書込
            f.write(all_data)
            print("Write file:"+imgfilepath + sc_file)
    except Exception as e:
        print('Recieve ERROR occured')
        print(e)
    finally:
        # コネクション切断
        print("Finish process, close thread.")
        clientsock.close()


def TCP_imgserver_main():
    # ソケット定義(IPv4,TCPによるソケット)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # 次の実行に備え、ソケットをTIME-WAIT切れを待つことなく、再利用できるようにしてお>く
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #sock.settimeout(3);

        # IPとPORTを指定してバインド（ソケットに紐づけ）
        s.bind((TCP_imgserver_host,TCP_imgserver_port))
        # 10 ユーザまで接続を許可
        s.listen(10)
        clients = []
        while True:
            # ソケット接続受信待ち
            try:
                print('クライアントからの接続待ち...')
                # 接続が来たら対応する新しいソケットオブジェクト作成、接続先アドレスを格納
                clientsock, client_address = s.accept()

            # 接続待ちの間に強制終了が入った時の例外処理
            except KeyboardInterrupt:
                print(u'Ctrl + C により強制終了')
                s.close()
                exit()


            # 接続待ちの間に強制終了なく、クライアントからの接続が来た場合
            else:
                # アドレス確認
                print(u"[ADRESS]=>{}".format(client_address[0]))
                print(u"[PORT]=>{}".format(client_address[1]))
                print("\r\n")
                # タイムアウトの設定
                clientsock.settimeout(5)
                # 待受中にアクセスしてきたクライアントを追加
                clients.append((clientsock, client_address))
                # スレッド作成
                thread = threading.Thread(target=recv_client_data, args=(clientsock, client_address), daemon=True)
                # スレッドスタート
                thread.setDaemon(True)
                thread.start()


    except Exception as e:
        print(e)

    finally:
        # ソケットを閉じる
        s.close()

if __name__ == '__main__':
    # スレッドオブジェクト生成
    t1 = threading.Thread(target=Flask_main)
    t2 = threading.Thread(target=TCP_imgserver_main)
    # デーモン化
    t1.setDaemon(True)
    t2.setDaemon(True)
    t1.start()
    t2.start()

    while True:
        n = input()
        if n == "q":
            print("終了")
            sys.exit()
    # Flask_main()
    # TCP_imgserver_main()
