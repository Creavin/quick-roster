<template>
    <div class="container">
        <h1>My files</h1>
        <p> 
            Lorem ipsum dolor sit amet, consectetur adipisicing elit. Pariatur excepturi labore tempore expedita, et iste tenetur suscipit explicabo! Dolores, aperiam non officia eos quod asperiores
        </p>

        <div class="mb-3">
            <h3> Schedules</h3>
            <ListFilesArea dir="input"></ListFilesArea>
        </div>
        
        <div class="mb-3">
            <h3> Rosters </h3>
            <ListFilesArea dir="output"></ListFilesArea>
        </div>

    </div>
</template>

<script>
import UserInfoStore from '@/app/user-info-store';
import ListFilesArea from '@/components/ListS3Files';

export default {
    components: {
        ListFilesArea 
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