<script lang="ts">
    import LandingPage from "$lib/layouts/LandingPage.svelte";
    let title: string = "Analysis";
    let description: string = "You can use this tool to create several different analyses.\n\n(More text to follow...)";
    let pages: string[] = ["Simple", "Multiple parameters"];
    let images: string[] = ["/Winterreise_manuscript.jpg", "screenshot_perfs.png"];
    let links: string[] = ["/analysis/simple", "/visualizations/multi-parameter"]
</script>

<LandingPage title={title} description={description} pages={pages} images={images} links={links} />