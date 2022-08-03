<template>
    <div class="container">
        <h1>Manage</h1>
        <h3>Welcome, {{userInfo.username}} </h3>
        <!--<div class="alert alert-info"> {{userInfo}} </div>-->


        <div class="d-grid gap-2 col-6 mx-auto mb-5">   
            <router-link to="/upload" class="btn btn-primary" role="button">
                Upload a schedule
            </router-link>
            <router-link to="/list" class="btn btn-primary"  role="button">
                My files
            </router-link>
            <router-link to="/create" class="btn btn-primary disabled" role="button">
                Tutorial
            </router-link>
            <router-link to="/create" class="btn btn-primary" role="button">
                Create a roster
            </router-link>
            <router-link to="/create" class="btn btn-primary disabled"  role="button">
                Sign up to a roster
            </router-link>
            <router-link to="/create" class="btn btn-primary disabled"  role="button">
                My account
            </router-link>
        </div>

        <h3>More information</h3>
        <p>
        Lorem ipsum dolor sit amet, consectetur adipisicing elit. Pariatur excepturi labore tempore expedita, et iste tenetur suscipit explicabo! Dolores, aperiam non officia eos quod asperiores
        </p>
        <router-link to="/logout"> Logout </router-link>
    </div>
</template>

<script>
import UserInfoStore from '@/app/user-info-store';

export default {
    name: 'Manage',
    data: function() {
        return{
            userInfo: UserInfoStore.state.cognitoInfo
        }
    }
}
</script>

<style>
</style>