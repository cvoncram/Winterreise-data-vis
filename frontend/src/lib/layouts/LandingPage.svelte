<script lang="ts">
	import IntroGallery from "$lib/components/IntroGallery.svelte";

    let {title, description, pages, images, links}: {title: string; description: string; pages: string[]; images: string[]; links: string[]} = $props();
</script>

<div class="relative flex flex-col h-screen items-center px-[20%] overflow-hidden">
    <div 
        class="absolute inset-0 bg-cover bg-center opacity-50 bg-base-200">
    </div>    
    <div class="bg-base-100 p-10 rounded-md shadow-xl opacity-85 h-full">
        <h3 class="text-3xl mb-5">{title}</h3>
        <div class="text-xl whitespace-pre">
            <p>{description}</p>
        </div>
        <div class="mb-4 mt-4 flex w-full justify-center">
            <IntroGallery titles={pages} images={images} links={links} />
        </div>
    </div>
</div>
