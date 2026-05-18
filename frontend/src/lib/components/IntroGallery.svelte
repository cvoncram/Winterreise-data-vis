<script lang="ts">
let hovered1 = $state(false);
let hovered2 = $state(false);
let hovered3 = $state(false);
</script>

<div class="flex flex-row">
<a href="/scores" class="hover-3d min-w-[33%] cursor-pointer" onmouseenter={() => hovered1=true} onfocus={() => hovered1=true} onmouseleave={() => hovered1=false} onblur={()=> hovered1=false}>

<!-- content -->
<div class="min-w-85 max-h-100 card">
    <div class="card-body">
        <img class:opacity-50={hovered1} class="rounded-xl h-full object-cover w-full" src="/screenshot_scores_1.png" alt="Screenshot from scores page" />
        <h2 class:invisible={!hovered1} class="absolute top-[50%] left-[50%] text-6xl text-success translate-[-50%]">Scores</h2>
    </div>
</div>
<!-- 8 empty divs needed for the 3D effect -->
<div></div>
<div></div>
<div></div>
<div></div>
<div></div>
<div></div>
<div></div>
<div></div>
</a>

<a href="/performances" class="hover-3d min-w-[33%] cursor-pointer" onmouseenter={() => hovered2=true} onfocus={() => hovered2=true} onmouseleave={() => hovered2=false} onblur={()=> hovered2=false}>

<!-- content -->
<div class="min-w-85 max-h-100 card">
    <div class="card-body">
        <img class:opacity-50={hovered2} class="rounded-xl object-cover h-full w-full" src="/screenshot_perfs.png" alt="Screenshot from performances page" />
        <h2 class:invisible={!hovered2} class="absolute top-[50%] left-[50%] text-6xl text-success translate-[-50%]">Performances</h2>
    </div>
</div>
<!-- 8 empty divs needed for the 3D effect -->
<div></div>
<div></div>
<div></div>
<div></div>
<div></div>
<div></div>
<div></div>
<div></div>
</a>

<a href="/analysis" class="hover-3d min-w-[33%] cursor-pointer" onmouseenter={() => hovered3=true} onfocus={() => hovered3=true} onmouseleave={() => hovered3=false} onblur={()=> hovered3=false}>

<!-- content -->
<div class="min-w-85 max-h-100 card">
    <div class="card-body">
        <img class:opacity-50={hovered3} class="rounded-xl object-cover h-full w-full" src="/screenshot_scores_3.png" alt="Screenshot from analysis page" />
        <h2 class:invisible={!hovered3} class="absolute top-[50%] left-[50%] text-6xl text-success translate-[-50%]">Analysis</h2>
    </div>
</div>
<!-- 8 empty divs needed for the 3D effect -->
<div></div>
<div></div>
<div></div>
<div></div>
<div></div>
<div></div>
<div></div>
<div></div>
</a>
</div>

