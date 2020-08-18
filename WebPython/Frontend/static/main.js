// custom javascript
function convertCSVtoArray(str){ // 読み込んだCSVデータが文字列として渡される
    var result = []; // 最終的な二次元配列を入れるための配列
    var tmp = str.split("\n"); // 改行を区切り文字として行を要素とした配列を生成

    // 各行ごとにカンマで区切った文字列を要素とした二次元配列を生成
    for(var i=0;i<tmp.length;++i){
        result[i] = tmp[i].split(',');
    }
    return result;

};
// GPSデータのクリーニング
function CleanGPSdata(gpsarray){ // 読み込んだCSVデータが文字列として渡される
    var TH=0.05;
    var resultgpsarray=[];
    var noise_flag=false;
    var lat,long;
    for(var i=0;i<gpsarray.length;i++){
      try{
        if(gpsarray[i][1]==0||gpsarray[i][2]==0){
          continue;
        }
        if( (gpsarray[i][1]<20)||(47<gpsarray[i][1]) ){ //北緯がおかしい時
          continue;
        }
        if( (gpsarray[i][2]<122)||(154<gpsarray[i][2]) ){//東経がおかしい時
          continue;
        }
        if( Math.abs(gpsarray[i][1]-gpsarray[i+1][1])>TH||Math.abs(gpsarray[i][2]-gpsarray[i+1][2])>TH ){//差分がおかしい時
          noise_flag=true;
          console.log("gpsflag TURE",gpsarray[i][1],gpsarray[i][2],gpsarray[i+1][1],gpsarray[i+1][2]);
          lat=gpsarray[i+1][1];
          long=gpsarray[i+1][2];
          continue;
        }
        if(noise_flag){//前回データにノイズが載っていた時
          if(Math.abs(gpsarray[i][1]-lat)<TH||Math.abs(gpsarray[i][2]-long)<TH ){
            console.log("gpslog",gpsarray[i][1],gpsarray[i][2]);
            continue;
          }else{
            noise_flag=false;//元に戻った場合
          }
        }
        if( Math.abs(gpsarray[i][1]-gpsarray[i+20][1])>4||Math.abs(gpsarray[i][2]-gpsarray[i+20][2])>4 ){
          continue;
        }
        resultgpsarray.push(gpsarray[i])
      }
      catch (e) {
        continue
      }
    }
    console.log(resultgpsarray)
    return resultgpsarray;
};

function get_col(array2,num){
  var result = [];
  for(var i=0;i<array2.length-1;i++){
    result[i]=array2[i][num]
  }
  return result;
};

// Ajax でのGET通信
function ajaxget(GETURL,param,ProcessFunc){
  var xhr = new XMLHttpRequest();
  xhr.open("GET",GETURL+'?'+param,true);
  xhr.send(null);
  xhr.onreadystatechange = function() {
      if(xhr.readyState === 4 && xhr.status === 200) {
        ProcessFunc(xhr.responseText);
      }
    }
  return xhr
}
//Ajax でのPOST通信
function ajaxpost(POSTURL,data,ProcessFunc){
  var xhr = new XMLHttpRequest();
  xhr.open('POST', POSTURL,true);
  xhr.setRequestHeader('content-type', 'application/x-www-form-urlencoded;charset=UTF-8');
  xhr.send(data);

  //xhr.send( unescape(encodeURIComponent('mac=d8a01d50a038&detailsFlag=True')) );
  xhr.onreadystatechange = function() {
      if(xhr.readyState === 4 && xhr.status === 200) {
        ProcessFunc(xhr.responseText);
      }
    }
  return xhr
}

// クエリの取得関数
function getUrlQueries() {
  var queryStr = window.location.search.slice(1);  // 文頭?を除外
      queries = {};
  // クエリがない場合は空のオブジェクトを返す
  if (!queryStr) {
    return queries;
  }
  // クエリ文字列を & で分割して処理
  queryStr.split('&').forEach(function(queryStr) {
    // = で分割してkey,valueをオブジェクトに格納
    var queryArr = queryStr.split('=');
    queries[queryArr[0]] = queryArr[1];
  });
  return queries;
}

// 桁調整の関数
function round(number, precision) {
  var shift = function (number, precision, reverseShift) {
    if (reverseShift) {
      precision = -precision;
    }
    var numArray = ("" + number).split("e");
    return +(numArray[0] + "e" + (numArray[1] ? (+numArray[1] + precision) : precision));
  };
  return shift(Math.round(shift(number, precision, false)), precision, true);
}
