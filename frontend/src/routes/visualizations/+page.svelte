<script lang="ts">
    import LandingPage from "$lib/layouts/LandingPage.svelte";
    let title: string = "Visualizing performances";
    let description: string = "This application offers a number of different ways to visualize whole performances, single pieces, and passages of pieces.\nEvery page offers the possibility of exporting the visualization itself as an SVG or the underlying data in the form of a CSV table.\n\nClick on any of the previews below to create a visualization:";
    let pages: string[] = ["Simple line graph representing a single parameter in one piece", "Visualize the manifestation of three different parameters in a piece", "Create a similarity network of performances based on Dynamic Time Warping"];
    let images: string[] = ["/Screenshot_Line-Graph.png", "Screenshot_Multi-parameter.png", "/Screenshot_DTWNetwork.png"];
    let links: string[] = ["/visualizations/line-graph", "/visualizations/multi-parameter", "/visualizations/dtw-network"];

    let contents: string[] = ["The time series or line graph is the most basic visualization. It visually represents the values of one parameter in a single song for one or several performances as a function of time, or more precisely, the values for each measure/beat.",
        "This semicircular graph maps all three parameters of one song in a performances onto a single visual representation. Every bar or \"slice\" represents one measure/beat; its width is determined by the tempo, its length by the dynamics, and its color by its spectral centroid value. It is possible to select passages of the performed song and compare it to other performances, as well as viewing the respective measures in the musical score, including notes by Fischer-Dieskau.",
        "Here, you can create a similarity network of performances on the level of a full or half cycle, single piece or selected measures. The underlying algorithm comparing the performance data is based on dynamic time warping, which calculates the optimal path \"between\" two performances and returns the cost of creating this path. A lower value means the performances are closer and therefore more similar, a larger value means greater differences."
    ]
</script>

<LandingPage title={title} description={description} pages={pages} images={images} links={links} contents={contents}/>