<template>
    <div class="position-relative overflow-hidden p-3 p-md-5 m-md-3 text-center bg-light">
      <div class="col-md-5 p-lg-5 mx-auto my-5">
        <h1 class="display-4 font-weight-normal">Quick Roster</h1>
        <p class="lead font-weight-normal"> Lorem ipsum dolor sit amet, consectetur adipisicing elit.</p>

        <div class="d-grid gap-2 d-md-block">   
            <router-link to="/manage" class="btn btn-primary btn-md" tabindex="-1" role="button">Start Rostering</router-link>
        </div>
      </div>
    </div>

    <div class="container">
        <div class="row">
            <h1>About Quick Roster</h1>
            <p>
                Lorem ipsum dolor sit amet, consectetur adipisicing elit. Error doloremque omnis animi, eligendi magni a voluptatum, vitae, consequuntur rerum illum odit fugit assumenda rem dolores inventore iste reprehenderit maxime! Iusto.
            </p>
        </div>
    </div>




    <div class="container">
        <router-link to="/logout">
            Logout
        </router-link>
    </div>


</template>

<script>
import UserInfoStore from '../app/user-info-store';
console.log(UserInfoStore.state.cognitoInfo)
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