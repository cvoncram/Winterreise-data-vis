<script lang="ts">
	import IntroGallery from "$lib/components/partials/IntroGallery.svelte";

    let {title, description, pages, images, links, contents}: {title: string; description: string; pages: string[]; images: string[]; links: string[]; contents: string[]} = $props();
</script>

<div class="relative flex flex-col h-screen items-center px-[20%] mt-5 mb-5 overflow-hidden">
    <div
    class="fixed inset-0 bg-cover bg-center opacity-50 bg-base-200 mb-auto"
    style="background-image: url('/Winterreise_manuscript.jpg');">
    </div>   
    <div class="bg-base-100 p-10 rounded-md shadow-xl opacity-90 h-full">
        <h3 class="text-3xl mb-5">{title}</h3>
        <div class="text-xl whitespace-pre">
            <p>{description}</p>
        </div>
        <div class="mb-4 mt-4 flex w-full justify-center">
            <IntroGallery titles={pages} images={images} links={links} contents={contents}/>
        </div>
    </div>
</div>
