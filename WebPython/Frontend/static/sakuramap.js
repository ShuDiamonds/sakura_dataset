//地図の表示
var map = L.map('sakura_map').setView([34.7326198,135.7340145], 15);
//描画する(Copyrightは消しちゃダメよ)
var tileLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{
  attribution: '© <a href="http://osm.org/copyright">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>',
  maxZoom: 19
});
tileLayer.addTo(map);

//
function process_AICAM_os(resulttext){
      console.log("resulttext",resulttext)
      jsondata = JSON.parse(resulttext);
      console.log(jsondata);
      imgfilenames=jsondata
      imgvuedata=[]
      for(var i=0;i<imgfilenames.length;i++){
        // ファイル名の例：5002918F0F84/azi___55_0.00_0.00_0.jpg
        gpstmp=imgfilenames[i].split('_');
        sakura_lat=parseFloat(gpstmp[4]);
        sakura_long=parseFloat(gpstmp[5]);
        mac=imgfilenames[i].split('/')[0];
        console.log(gpstmp,sakura_lat,sakura_long);
        if( isNaN(sakura_lat)|| isNaN(sakura_long)){
          continue;
        }
        L.marker([sakura_lat, sakura_long]).addTo(map).bindPopup('sakura'+mac).openPopup();
        // imgvuedata.push(
        //   {
        //     thumb: '/static/reciv_data/'+imgfilenames[i],
        //     src:'/static/reciv_data/'+imgfilenames[i],
        //     caption: imgfilenames[i]
        //   }
        // )
      }
      map.setView([sakura_lat, sakura_long],15);




}

xhrprocess_AICAM_os=ajaxget('/os/','detailsFlag=1',process_AICAM_os);
