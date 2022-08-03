<template>
    
    <div v-for="index in 10" :key="index"  v-bind:id="index">
        <label>Label text {{index}}</label>
        <input :id="'row-' + index" type="text" />
    </div>

</template>
<script>
export default {
    mounted: function(){
    }
}
</script>