<script lang="ts">
	import { onMount } from "svelte";

    let {titles, images, links}: {titles: string[]; images: string[]; links: string[]} = $props();

    let hovered: boolean[] = $state([]);
    
    onMount(() => {
    hovered = new Array(titles.length).fill(false);
    });
</script>

<div class="flex flex-row">

    {#each titles as title, i}
    <a href={links[i]} style:max-width="{100 / images.length}%" class="hover-3d cursor-pointer" onmouseenter={() => hovered[i]=true} onfocus={() => hovered[i]=true} onmouseleave={() => hovered[i]=false} onblur={()=> hovered[i]=false}>

        <!-- content -->
        <div class="min-w-85 min-h-60 max-h-100 card">
            <div class="card-body">
                <img class:opacity-50={hovered[i]} class="rounded-xl h-full object-cover w-full" src={images[i]} alt="Screenshot" />
                <h2 class:invisible={!hovered[i]} class="absolute top-[50%] left-[50%] text-6xl text-primary translate-[-50%]">{title}</h2>
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
    {/each}

</div>

