# project/user/views.py


#################
#### imports ####
#################

import datetime

from flask import render_template, Blueprint, url_for, \
    redirect, flash, request
from flask_login import login_user, logout_user, \
    login_required, current_user

#from project.models import myserverip
from project.token import generate_confirmation_token, confirm_token
from project.decorators import check_confirmed
from project import db, bcrypt
#from .forms import LoginForm, RegisterForm, ChangePasswordForm, ForgotForm
#add
from flask import Flask, render_template, send_from_directory, session
from flask import jsonify
from werkzeug.utils import secure_filename
################
#### config ####
################
import project
from project import ipsettingfilepath,dbpath
AICAM_blueprint = Blueprint('AICAM', __name__,)
import requests as requests_fromserver


################
#### routes ####
################

# ここでACCとGPSの全体データの表示
@AICAM_blueprint.route('/AICAM/')
def home():
    if current_user.is_authenticated:
        DeviceInfo=project.get_DeviceInfo(current_user,devicetype='aic')
        return render_template('AICAM/index.html', current_user=current_user,DeviceInfo=DeviceInfo)
    else: #login していない時の処理
        print("@/AICAM/ : Not logined ")
        return render_template('AICAM/index.html', current_user=current_user)


@AICAM_blueprint.route('/AICAM/img/<mac_ad>/<pic_name>',methods=["GET"])
def AICAM_img(mac_ad,pic_name):
    if len(mac_ad)!=12:
        return ""
    if not(current_user.is_authenticated):
        return ""
    serveripadress=project.get_serveripfromsettingfile()
    # print('http://{0}:44444/gps/one/?{1}'.format(serveripadress,request.query_string.decode()))
    return redirect('http://{0}:44445/static/{1}/{2}'.format(serveripadress,mac_ad,pic_name ))


@AICAM_blueprint.route('/AICAM_os/',methods=["POST"])
def AICAMos():
    if not(current_user.is_authenticated):
        return ""
    serveripadress=project.get_serveripfromsettingfile()
    print("AICAM_os:",serveripadress)
    #POSTパラメータは二つ目の引数に辞書で指定する
    try:
        response = requests_fromserver.post(
            'http://{0}:44445/os/'.format(serveripadress),
            {"mac": request.form["mac"]})
    except :
        print("error post")
        return "[[]]"
    #レスポンスオブジェクトのjsonメソッドを使うと、
    #JSONデータをPythonの辞書オブジェクトに変換して取得できる
    return response.text
