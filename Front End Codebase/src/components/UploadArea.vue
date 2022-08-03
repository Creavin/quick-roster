<template>
  <div class="input-group mb-3">
    <div class="custom-file">
      <input @change="onFileChange" type="file" class="custom-file-input" id="inputGroupFile01">

      <div v-if="!file">
        <label class="custom-file-label" for="inputGroupFile01">Choose file</label>
      </div>
      <div v-else>
        <label class="custom-file-label" for="inputGroupFile01">{{fileName}}</label>
      </div>

    </div>
    <div class="input-group-prepend">
      <span class="btn btn-secondary" @click="uploadFile">Upload</span>
    </div>
  </div>
</template>

<script>
/* eslint-disable */
import AWS from 'aws-sdk'
import UserInfoStore from '@/app/user-info-store';



var bucketName = process.env.VUE_APP_S3_BUCKET_NAME
var bucketRegion = process.env.VUE_APP_AWS_REGION
var IdentityPoolId = process.env.VUE_APP_COGNITO_IDENTITY_POOL_ID
var inputDir = process.env.VUE_APP_S3_INPUT_DIR
console.log("inputdir:", inputDir)

AWS.config.update({
  region: bucketRegion,
  credentials: new AWS.CognitoIdentityCredentials({
    IdentityPoolId: IdentityPoolId
  })
});

function isJson(fileName) {
  return fileName.split('.').pop() == "json"
}

export default {
    data: function() {
      return {
        file: null,
        fileName: null,
      }
    },
    methods: {
      onFileChange (e) {
        let files = e.target.files || e.dataTransfer.files
        if (!files.length) return
        let file = files[0]

        console.log("New file received:", file.name)
        if (isJson(file.name)) {
          this.file = file;
          this.fileName = this.file.name
        } else {
          alert("Invalid file type. Acceptable file types: JSON")
        }

      },
      removeFile: function (event) {
        this.file = null,
        this.fileName = null,
        console.log('Remove clicked:', event)
      },
      uploadFile: async function () {
        console.log('Upload clicked')
        var username = UserInfoStore.state.cognitoInfo.username
        console.log("Username:", username)
        console.log("inputdir: acc upload file", inputDir)

        var upload = new AWS.S3.ManagedUpload({
                    params: {
                      Bucket: bucketName,
                      Key: username + "/" + inputDir + "/" + this.file.name,
                      Body: this.file
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
}
</script>