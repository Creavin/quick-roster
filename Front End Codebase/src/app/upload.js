
const MAX_IMAGE_SIZE = 1000000;
var albumBucketName = "creavt-qr-upload";
var bucketRegion = "eu-west-1";
var IdentityPoolId = "eu-west-1:0d4bd86d-95a0-437e-af81-871f920c4365";

AWS.config.update({
  region: bucketRegion,
  credentials: new AWS.CognitoIdentityCredentials({
    IdentityPoolId: IdentityPoolId
  })
});

var s3 = new AWS.S3({
  apiVersion: "2006-03-01",
  params: { Bucket: albumBucketName }
});

s3.listObjects({ Delimiter: "/" }, function(err, data) {
  if (err) {
    return alert("There was an error listing your albums: " + err.message);
  } else {
      var albums = data.CommonPrefixes.map(function(commonPrefix) {
      var prefix = commonPrefix.Prefix;
      var albumName = decodeURIComponent(prefix.replace("/", ""));
      console.log(albumName);
    });
}})


new Vue({
  el: "#app",
  data: {
    newFile: '',
    fileJsonData: '',
    image: '',
    uploadURL: ''
  },
  methods: {
    onFileChange (e) {
      let files = e.target.files || e.dataTransfer.files
      if (!files.length) return
      this.newFile = files[0];
      console.log("New file received:", this.newFile.name)

      this.createImage(files[0])
    },
    createImage (file) {

      const blob = new Blob([file], {type:"application/json"});
      const fr = new FileReader();

      fr.addEventListener("load", e => {
        console.log(e.target.result, JSON.parse(fr.result))
        //this.rawText = JSON.parse(fr.result)
        this.fileJsonData = JSON.parse(fr.result)
      });

      fr.readAsText(blob);


      let reader = new FileReader()
      reader.onload = (e) => {
        console.log('length: ', e.target.result.includes('application/json'))

        /*
        if (!e.target.result.includes('data:.json')) {
          return alert('Wrong file type - JPG only.')
        }
        if (e.target.result.length > MAX_IMAGE_SIZE) {
          return alert('Image is loo large.')
        }
        */
        this.image = e.target.result
      }
      reader.readAsDataURL(file)
    },
    removeImage: function (e) {
      console.log('Remove clicked')
      this.image = ''
    },
    uploadImage: async function (e) {
      console.log('Upload clicked')

      var upload = new AWS.S3.ManagedUpload({
                  params: {
                    Bucket: albumBucketName,
                    Key: this.newFile.name,
                    Body: this.newFile
                  }
                });

      var promise = upload.promise();

      promise.then(
        function(data) {
          alert("Successfully uploaded file.");
        },
        function(err) {
          return alert("There was an error uploading your file: ", err.message);
        }
      );

    }
  }
})
