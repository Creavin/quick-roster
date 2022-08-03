<template>
    <form>
        <div class="mb-3">
            <label for="days" class="form-label">Number of Days</label>
            <input type="number" class="form-control" id="num-days" placeholder="Enter number of days" min="1" max="28">
            <div class="form-text">The number of days to roster.</div>
        </div>
        <div class="mb-3">
            <label for="tracks" class="form-label">Number of Tracks</label>
            <input type="number" class="form-control" id="num-tracks" placeholder="Enter number of tracks" min="1" max="28">
            <div class="form-text">The number of tracks to roster.</div>
        </div>
        <div class="mb-3">
            <label for="shifts" class="form-label">Number of Shifts</label>
            <input type="number" class="form-control" id="num-shifts" placeholder="Enter number of shifts" min="1" max="28">
            <div class="form-text">The number of shifts to roster.</div>
        </div>
        <div class="mb-3">
            <label for="skills" class="form-label">Number of Skills</label>
            <input type="number" class="form-control" id="num-skills" placeholder="Enter number of skills" min="1" max="28">
            <div class="form-text">The number of skills to roster.</div>
        </div>
        <button type="submit" class="btn btn-primary">Submit</button>
    </form>

</template>
<script>
export default {
    mounted: function(){
        
    }
}
</script>