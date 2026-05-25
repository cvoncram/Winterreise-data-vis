<script lang="ts">
    import LandingPage from "$lib/layouts/LandingPage.svelte";
    let title: string = "Visualizations";
    let description: string = "There are several different ways to visualize whole performances, single pieces, and passages of pieces.\n\n(More text to follow...)";
    let pages: string[] = ["Single parameter", "Multiple parameters"];
    let images: string[] = ["/Winterreise_manuscript.jpg", "screenshot_perfs.png"];
    let links: string[] = ["/visualizations/single-parameter", "/visualizations/multi-parameter"]
</script>

<LandingPage title={title} description={description} pages={pages} images={images} links={links} />