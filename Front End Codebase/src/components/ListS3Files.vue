<template>
  <div v-if="fileNames">
    <ul>
     <li @click="downloadFile(fileName)" v-for="fileName in fileNames" :key="fileName">
        {{fileName}}

        <button type="button" class="btn btn-link"> Download </button>
      </li>
    </ul>
  </div>
  <div v-else>
      No files. 
  </div>

  <div v-if="isTruncated">
    <button class="btn btn-secondary" @click="listFiles(this.token)">List more files</button>
  </div>
  <div v-else>
    <button class="btn btn-secondary disabled">List more files</button>
  </div>


</template>

<script>
/* eslint-disable */
import AWS from 'aws-sdk'
import UserInfoStore from '@/app/user-info-store';


var bucketName = process.env.VUE_APP_S3_BUCKET_NAME
var bucketRegion = process.env.VUE_APP_AWS_REGION
var IdentityPoolId = process.env.VUE_APP_COGNITO_IDENTITY_POOL_ID

AWS.config.update({
  region: bucketRegion,
  credentials: new AWS.CognitoIdentityCredentials({
    IdentityPoolId: IdentityPoolId
  })
});

var s3 = new AWS.S3();

function isJson(fileName) {
  return fileName.split('.').pop() == "json"
}

export default {
  data: function() {
    return {
      fileNames: [],
      isTruncated: false,
      token: ""
    }
  },
  mounted() {
    this.listFiles()
  },
  props: {
    dir: String
  },
  methods: {
    downloadFile(fileName) {
      var username = UserInfoStore.state.cognitoInfo.username
      var key = username + '/' + this.dir + '/' + fileName
      var params = {
        Bucket: bucketName,
        Key: key
      }

      s3.getObject(params).promise()
        //.then(data => console.log(data.Body))
        .then(data => {
          var fileContents = data.Body.toString();
          return new Blob([fileContents], {type : 'application/json'})
        })
        .then(data => {
          const url = window.URL.createObjectURL(data);
          const a = document.createElement('a');
          a.style.display = 'none';
          a.href = url;
          a.download = fileName;
          document.body.appendChild(a);
          a.click();
          window.URL.revokeObjectURL(url);
        })
        .catch((err) => {
          throw err
      })
    },
    // todo unpaginate
    listFiles: async function (token = "") {
      console.log("Token is", token)
      console.log("DIR prop = ", this.dir)
      if (this.dir === "") throw new Error("S3 directory not defined")

      console.log('Upload clicked')
      var username = UserInfoStore.state.cognitoInfo.username
      console.log("Username:", username)

      var params = {
        Bucket: bucketName, 
        Prefix: username + "/" + this.dir + "/", 
        MaxKeys: 5
      };

      if(token) params.ContinuationToken = token;


      const allKeys = []
      const prom = s3.listObjectsV2(params).promise();
      prom.then(function(data){
        console.log("Data", data)
        var contents = data.Contents;
        contents.forEach(function (content) {
          var filePath = content.Key
          var fileName = filePath.replace(params.Prefix, "")
          if (isJson(fileName)) allKeys.push(fileName);

        });
         
        return data

      }).then((data) => {
        this.fileNames = this.fileNames.concat(allKeys),
        this.isTruncated = data.IsTruncated
        this.token = data.NextContinuationToken
      })
    }
  }
}



/*
var allKeys = [];
function listAllKeys(token, cb)
{
  var opts = { Bucket: s3bucket };
  if(token) opts.ContinuationToken = token;

  s3.listObjectsV2(opts, function(err, data){
    allKeys = allKeys.concat(data.Contents);

    if(data.IsTruncated)
      listAllKeys(data.y, cb);
    else
      cb();
  });
}

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



*/
</script>
