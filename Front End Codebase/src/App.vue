<template>

  <nav class="navbar navbar-light bg-secondary mb-3">
    <a class="navbar-brand" href="/" style="color: white">
      <img src="./assets/larry_white_stroke.svg" width="30" height="30" class="d-inline-block align-top" alt="">
      Quick Roster
    </a>
  </nav>
  <router-view/>
</template>

<script>
export default {
  name: 'App',
}
</script>

<style lang="scss">
#app {} // Required to apply scss to app
</style>