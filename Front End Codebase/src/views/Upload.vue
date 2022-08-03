<template>
    <div class="container mb-5">
        <h1>Upload a schedule</h1>
        <p> 
            Lorem ipsum dolor sit amet, consectetur adipisicing elit. Pariatur excepturi labore tempore expedita, et iste tenetur suscipit explicabo! Dolores, aperiam non officia eos quod asperiores
        </p>
    </div>

    <div class="container">
        <h2>Schedule Upload</h2>
        <p>Select a schedule json file</p>
        <UploadArea/>
    </div>
</template>

<script>
import UserInfoStore from '@/app/user-info-store';
import UploadArea from '@/components/UploadArea';

export default {
    components: {
        UploadArea
    },
    data: function() {
        return{
            userInfo: UserInfoStore.state.cognitoInfo
        }
    }
}
</script>

<style>
</style>