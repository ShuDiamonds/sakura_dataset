

// ここからギャラリーの表示
Vue.use(VueLazyload, {
  preLoad: 1.3,
  error: 'https://dummyimage.com/130x120/ccc/999.png&text=Not+Found',
  loading: 'https://dummyimage.com/130x120/dcdcdc/999.png&text=Now loading',
  attempt: 1
});

const LightBox = window.Lightbox.default;

Vue.component('light-box', LightBox);

var AICAMapp = new Vue({
  el: '#AICAMapp',
  data: {
    images: [
      {
        thumb: 'https://dummyimage.com/150x150/fcc/000.png&text=thumb1',
        src: 'https://dummyimage.com/600x600/fcc/000.png&text=Uploaded1',
        caption: 'キャプション1'
      },
      {
        thumb: 'https://dummyimage.com/150x150/fcc/000.png&text=thumb2',
        src: 'https://dummyimage.com/600x600/fcc/000.png&text=Uploaded2',
        caption: 'キャプション2'
      },
      {
        thumb: 'https://dummyimage.com/150x150/fcc/000.png&text=thumb3',
        src: 'https://dummyimage.com/600x600/fcc/000.png&text=Uploaded3',
        caption: 'キャプション3'
      }
    ]
  },
  methods: {
    show: function(index){
      this.$refs.lightbox.showImage(index)
    }
  }
});


//
function process_AICAM_os(resulttext){
      console.log("resulttext",resulttext)
      jsondata = JSON.parse(resulttext);
      console.log(jsondata);
      imgfilenames=jsondata
      imgvuedata=[]
      for(var i=0;i<imgfilenames.length;i++){
        imgvuedata.push(
          {
            thumb: '/static/reciv_data/'+imgfilenames[i],
            src:'/static/reciv_data/'+imgfilenames[i],
            caption: imgfilenames[i]
          }
        )
      }
      console.log(this.AICAMapp.images)
      this.AICAMapp.images=imgvuedata
      console.log("AICAMapp.images",this.AICAMapp.images)



}

xhrprocess_AICAM_os=ajaxget('/os/','detailsFlag=1',process_AICAM_os);
