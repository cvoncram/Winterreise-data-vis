<script lang="ts">
    import LandingPage from "$lib/layouts/LandingPage.svelte";
    let title: string = "Visualizations";
    let description: string = "There are several different ways to visualize whole performances, single pieces, and passages of pieces.\n\n(More text to follow...)";
    let pages: string[] = ["Simple line graph representing a single parameter in one or several pieces", "Visualize the manifestation of three different parameters in a piece", "Create a network of performances based on Dynamic Time Warping"];
    let images: string[] = ["/Screenshot_Line-Graph.png", "Screenshot_Multi-parameter.png", "/Screenshot_DTWNetwork.png"];
    let links: string[] = ["/visualizations/line-graph", "/visualizations/multi-parameter", "/visualizations/dtw-network"]
</script>

<LandingPage title={title} description={description} pages={pages} images={images} links={links} />