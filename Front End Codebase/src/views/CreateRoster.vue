<template>
    <div class="container">
        <h1>Create a Roster</h1>
        <p> A roster is composed of days, tracks, shifts, and skills.</p>
    
        
        <p> 
            Lorem ipsum dolor sit amet, consectetur adipisicing elit. Pariatur excepturi labore tempore expedita, et iste tenetur suscipit explicabo! Dolores, aperiam non officia eos quod asperiores
        </p>

        
        <RosterBuilder/>

        <p> 
            Lorem ipsum dolor sit amet, consectetur adipisicing elit. Pariatur excepturi labore tempore expedita, et iste tenetur suscipit explicabo! Dolores, aperiam non officia eos quod asperiores
        </p>

        <RosterConfigInfo/>

        <router-link to="/logout"> Logout </router-link>
    </div>
</template>

<script>
import UserInfoStore from '@/app/user-info-store';
import RosterConfigInfo from '@/components/RosterConfigInfo';
import RosterBuilder from '@/components/RosterBuilder';

export default {
    components: {
        RosterConfigInfo,
        RosterBuilder
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
