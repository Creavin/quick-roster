/* eslint-disable */
import { createWebHistory, createRouter } from "vue-router";

import Home from '@/views/Home'
import Manage from '@/views/Manage'
import CreateRoster from '@/views/CreateRoster'
import Upload from '@/views/Upload'
import List from '@/views/ListRosters'

import auth from '@/app/auth';
import UserInfoStore from '@/app/user-info-store';
import UserInfoApi from '@/app/user-info-api';

import ErrorComponent from '@/components/Error';
import LogoutSuccess from '@/components/LogoutSuccess';

function requireAuth(to, from, next) {
  if (!auth.auth.isUserSignedIn()) {
      UserInfoStore.setLoggedIn(false);
      next({
      path: '/login',
      query: { redirect: to.fullPath }
      });
  } else {
    UserInfoApi.getUserInfo().then(response => {
      UserInfoStore.setLoggedIn(true);
      UserInfoStore.setCognitoInfo(response);
      next();
    });
      
  }
}

const routes = [
  {
    path: "/",
    name: "Home",
    component: Home,
    meta: {title: 'Quick Roster'},
  },
  {
    path: "/manage",
    name: "Manage",
    component: Manage,
    beforeEnter: requireAuth
  },
  {
    path: "/create",
    component: CreateRoster,
    beforeEnter: requireAuth
  },
  {
    path: "/upload",
    component: Upload,
    beforeEnter: requireAuth
  },
  {
    path: "/list",
    component: List,
    beforeEnter: requireAuth
  },
  {
    path: '/login', beforeEnter(to, from, next){
      auth.auth.getSession();
    }
  },
  {
    path: '/login/oauth2/code/cognito', beforeEnter(to, from, next){
      var currUrl = window.location.href;
      
      //console.log(currUrl);
      auth.auth.parseCognitoWebResponse(currUrl);
      //next();
    }
  },
  {
    path: '/logout', component: LogoutSuccess,  beforeEnter(to, from, next){
      auth.logout();
      next();
    }

  },
  {
    path: '/error', component: ErrorComponent
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});


router.beforeEach((to, from, next) => {
  document.title = to.meta.title || 'Quick Roster';
  next();
});


export default router;