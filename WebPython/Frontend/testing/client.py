#!/usr/bin/env python
# -*- coding: utf-8 -*-
# https://qiita.com/__init__/items/5c89fa5b37b8c5ed32a4
# https://nine-num-98.blogspot.com/2020/03/ai-socket-03.html
import socket
import os, sys
import time

# サーバーIPアドレス定義
host = "192.168.0.14"
host = "0.0.0.0"
# サーバー待ち受けポート番号定義
port = 44446


def main():
    # 送信画像ファイルパス引数の取得
    if not len(sys.argv)==2:
        print('使用法: python client.py 画像ファイル名')
        sys.exit()
    image_file = sys.argv[1]

    # ファイルをバイナリデータとして読み込み
    with open(image_file, 'rb') as f:
        binary = f.read()

    # ソケットクライアント作成
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # 送信先サーバーに接続
        s.connect((host, port))

        # サーバーにバイナリデータを送る
        print(image_file + 'をサーバーに送信')
        filename=image_file.encode()
        #filedata=[0] * 100
        s.sendall(filename)
        time.sleep(0.005)
        s.sendall("d8a01d50a038,0hqhf0j==fak;=0fq".encode())
        time.sleep(0.005)
        s.sendall(binary)
        # データ送信完了後、送信路を閉じる
        s.shutdown(1)

    except Exception as e:
        # 例外が発生した場合、内容を表示
        print(e)

    finally:
        # ソケットを閉じて終了
        s.close()


if __name__ == '__main__':
    main()
