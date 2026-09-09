<script lang="ts">
  
    import {onMount} from "svelte";
    import type { Action } from 'svelte/action';
       
    let headings = new Map<string, HTMLHeadingElement>();
    let headingsList: HTMLHeadingElement[] = $state([]);
    let labels = $state(["1"]);
    let indent = $state([0]);
    
    const registerHeading: Action<HTMLHeadingElement> = (node) => {
        let key = node.textContent?.trim().toLowerCase().replace(/\s+/g, '-') ?? '';

        let suffix = 1;
        const baseKey = key;
        while (headings.has(key)) {
            key = `${baseKey}-${suffix}`;
            suffix++;
        }

        headings.set(key, node);

        return {
            destroy() {
            headings.delete(key);
            }
        };
    };
    
    function createContentTable(headings: HTMLHeadingElement[]) {
        headings[0].setAttribute("id", `${headings[0].innerHTML.replaceAll(" ", "_")}`);
        headings[0].setAttribute("no", "1_0_0");
        headings[0].innerHTML = `${labels[0]}. ${headings[0].innerHTML}`;
        headings[0].setAttribute("style", "text-decoration: underline;")

        let no = [0, 0, 0];

        for (let i = 1; i < headings.length; i++) {
            if (headings[i].localName === "h2") {
                no[0] = parseInt((headings[i-1].getAttribute("no"))?.split("_")[0] ?? "") + 1;
                no[1] = 0;
                no[2] = 0;
            } else if (headings[i].localName === "h3") {
                no[1] = parseInt((headings[i-1].getAttribute("no"))?.split("_")[1] ?? "") + 1; 
                no[2] = 0;
            } else if (headings[i].localName === "h4") {
                no[2] = parseInt((headings[i-1].getAttribute("no"))?.split("_")[2] ?? "") + 1; 
            }

            headings[i].setAttribute("no", `${no[0]}_${no[1]}_${no[2]}`);
            headings[i].setAttribute("id", `${headings[i].innerHTML.replaceAll(" ", "_")}`);
            labels[i] = `${no[0]}.${no[1] != 0 ? no[1] : ""}${no[2] != 0 ? "." + no[2] : ""}`;
            indent[i] = (() => {
                let x = 0;
                if (no[1] == 0 && no[2] == 0){
                    x = 0;
                } else if (no[1] != 0 && no[2] == 0){
                    x = 5;
                } else {
                    x = 10;
                }
                return x;
            })();
            headings[i].innerHTML = `${labels[i]} ${headings[i].innerHTML}`;
            headings[i].setAttribute("style", "text-decoration: underline;")
        }
        return headings;
    }

    
    onMount(() => {
        $inspect(Array.from(headings.values()));
        headingsList = createContentTable(Array.from(headings.values()));
    })
    
    
</script>

<div class="relative flex flex-col h-full items-center px-[20%] overflow-hidden">
    <div
    class="fixed inset-0 bg-cover bg-center opacity-50 bg-base-200 mb-auto"
    style="background-image: url('/Winterreise_manuscript.jpg');">
    </div>


    <div class="bg-base-100 p-10 pt-5 rounded-md shadow-xl opacity-85 h-full mt-5 mb-5">

        <h2>Documentation page</h2>
        <p>This project is an interactive web application for visualizing and comparing performance data from multiple MEI files of the same musical work.</p>
        <p>It renders a MEI score with Verovio and visualizes performance data (tempo, dynamics, timbre) extracted dynamically from a GitHub repository containing performance MEI files.</p>
            
        <div class="bg-base-200 rounded-xl p-4 m-2">
            <h3>Table of contents</h3>
            {#each headingsList as heading, i}
            <a style="color:#668ba4; text-decoration:underline; text-indent: calc(var(--spacing) * {indent[i]})" href={"#" + heading.getAttribute("id")}>
                <p>{heading.innerHTML}</p>
            </a>
            {/each}
        </div>
    
        <h2 use:registerHeading>About this application</h2>
        <p>This application was created by Clemens von Cramon as part of the M.A. thesis in <i>Digital Humanities</i> at <i>Johannes Gutenberg University</i> in Mainz.</p>
        
        <h2 use:registerHeading>How to use the application</h2>
        <p>The application has two halves. The score viewer shows the notated text with Dietrich Fischer-Dieskau's handwritten entries; the visualizations show what was actually played, measured beat by beat from 26 recordings made between 1948 and 1990. Both draw on the same encoded material, and both are reached from the navigation bar.</p>
        <p>Nothing needs to be installed or uploaded. The data are fetched as you work, so the first request on a page takes a moment while the files arrive.</p>

        <h3 use:registerHeading>Browsing the score</h3>
        <p>The score viewer engraves one song at a time. Choose a song from the dropdown; the notation is then typeset in your browser, which is why a large song takes a second or two to appear.</p>
        <p>Four sliders control the engraving: scale, spacing, page width and page height. They act immediately, without reloading anything, because the typesetting happens locally. Page height sets a minimum: the viewer measures every page of the current song and adopts the tallest, so that turning pages does not make the layout jump.</p>

        <h4 use:registerHeading>Reading the handwritten entries</h4>
        <p>Entries taken from Fischer-Dieskau's working copies are shown in violet, and turn orange when you hover over them. Elements that the edition supplies rather than the source are shown in green. Clicking any element opens a panel with what is known about it.</p>
        <p>For a note, the panel gives pitch, octave and measure. For an entry, it names the kind of marking — a directive for interpretation, a crescendo or diminuendo hairpin, a tempo or dynamics instruction, a trill, a slur, a fermata — together with the writing medium, since Fischer-Dieskau annotated in several pencils and a blue pen. Where the reading of a marking was uncertain, the reason for that uncertainty is shown as well. This is editorial information carried in the encoding, not an interpretation added by the application.</p>

        <h3 use:registerHeading>Comparing one parameter across recordings</h3>
        <p>The line graph is the simplest of the three visualizations. Choose a song, one parameter, and any number of recordings; each recording is drawn as a line, all on the same pair of axes, with a key naming the colours.</p>
        <p>Use it when you already know where to look. It answers questions of the form "how does this passage differ between these readings", and it is the natural next step after the similarity network has drawn your attention to a pair.</p>
        <p>The same selection can be shown as a data table instead of a graph, with a button to save it as a CSV file.</p>

        <h3 use:registerHeading>The multi-parameter view</h3>
        <p>This view shows a single recording of a single song, and encodes all three parameters at once. It is laid out as a semicircle divided into as many segments as there are measured beats.</p>
        <p>Each segment carries three quantities. Its width is the duration of that beat, so a slower passage takes up more of the semicircle. Its radial extent comes from the dynamics: a longer slab was played louder. Its colour comes from the timbre, with brighter meaning a higher spectral centroid, that is, a brighter sound.</p>
        <p>The colour scale can be changed in the sidebar. Viridis is the default because it renders differences in value as differences in perceived brightness, which keeps it legible in greyscale and under the common forms of colour blindness.</p>

        <h4 use:registerHeading>Selecting a passage</h4>
        <p>Two modes are available. In the first, clicking a segment shows the exact measured values for that beat. In the second, dragging across the ribbon selects a range of beats.</p>
        <p>Once a range is selected you can either restrict the display to it, so that the passage fills the whole semicircle, or carry it over to the comparison view.</p>

        <h4 use:registerHeading>Comparing several recordings of a passage</h4>
        <p>The comparison view shows the same passage from several recordings, one below the other. The ribbons are laid out linearly rather than as semicircles, because a shared horizontal axis is what makes the readings comparable at a glance.</p>
        <p>That axis carries elapsed time in seconds, and its scale is set by the longest of the selected recordings. A slower reading is therefore visibly wider and ends further to the left of the right-hand edge. The recording you started from stays at the top of the list however many others you add.</p>
        <p>The score for the selected measures can be shown beside the ribbons.</p>

        <h3 use:registerHeading>The similarity network</h3>
        <p>The network compares whole recordings rather than passages. It computes a numerical distance between every pair of selected recordings and arranges the result as a graph, in which more similar recordings are drawn closer together.</p>
        <p>Its purpose is orientation. With twenty recordings there are already 190 pairs, which no one can compare by eye; the graph shows the overall shape of the field and points at the pairs worth examining more closely. It does not say in what respect two recordings differ — that is what the other two visualizations are for.</p>

        <h4 use:registerHeading>Choosing the scope</h4>
        <p>Four scopes are available: the whole cycle, one half of it, a single song, or a range of measures within a song. The choice matters analytically, because similarity means different things at different levels. Across the cycle it measures an overall stance; within a song, the shaping of that one piece; within a few measures, the treatment of a particular moment.</p>
        <p>The half-cycle option follows the transmitted division into the first and second Abtheilung, songs 1 to 12 and 13 to 24.</p>

        <h4 use:registerHeading>Parameters metric and weights</h4>
        <p>Any combination of the three parameters can be selected. Choosing more than one does not simply add information: only those beats are used for which every selected parameter has a usable value, so an additional parameter can shrink the basis of the comparison.</p>
        <p>Two distance measures are offered. The Euclidean distance treats the parameters as independent. The Mahalanobis distance takes their correlation into account, so that a deviation following the usual relationship between the parameters counts for less than one running against it.</p>
        <p>With more than one parameter and the Euclidean measure, a slider appears beside each selected parameter. The weights are relative and are scaled before being sent, so you set proportions rather than absolute values; the percentage shown is the share each parameter actually contributes. Under the Mahalanobis measure the sliders are hidden, because weighting provably cancels out there and offering it would suggest an effect it cannot have.</p>

        <h4 use:registerHeading>Reading the result as a matrix</h4>
        <p>The same result can be shown as a triangular matrix instead of a graph. Every pair appears exactly once, coloured by distance, with the recording names running along the diagonal. Pointing at a cell names the pair and gives the figure.</p>
        <p>The matrix is the exact view: unlike the graph it embeds nothing and therefore approximates nothing. Pairs that could not be compared appear as dashed empty cells rather than as a value. A button saves the full square table as a CSV file.</p>

        <h3 use:registerHeading>Saving what you see</h3>
        <p>Each visualization can be saved as an SVG file, which scales without loss and can be edited in a vector graphics program. Tables and matrices can additionally be saved as CSV.</p>
        <p>Note that colours set through the interface are preserved in the SVG, but effects that exist only while you interact — the highlight under the pointer, for instance — are not, since a saved file is a static document.</p>

        <h2 use:registerHeading>How to read the visualizations</h2>
        <p>Everything shown here rests on three measured quantities per beat: the tempo in beats per minute, the dynamics as a level in decibels relative to full scale, and the timbre as the spectral centroid in hertz. Before any of them can be compared between recordings they have to be prepared, and understanding that preparation is what separates a reading of these displays from a misreading.</p>

        <h3 use:registerHeading>Why the raw numbers cannot be compared</h3>
        <p>Two obstacles stand in the way of comparing measured values directly.</p>
        <p>The first is the circumstances of recording. Some of these are studio productions, others are concert recordings of varying quality. The absolute level depends on microphone placement, gain, mastering and the transmission chain, so two recordings could be played equally loudly and still differ by twenty decibels. The spectral centroid is unaffected by level alone, but it reacts to frequency response and bandwidth limitation: a recording from 1948 has a lower centroid than one from 1990 for reasons that have nothing to do with singing. Tempo is the one parameter free of this, because it is derived from time intervals, which the recording chain does not systematically distort.</p>
        <p>The second obstacle is the incompatibility of the scales. Tempo values lie roughly between 40 and 160, dynamics between minus 40 and 0, spectral centroids between 400 and 5000. Combining all three into one measure without preparation would let the timbre dominate simply because its numbers are larger.</p>

        <h3 use:registerHeading>How the values are normalized</h3>
        <p>Two steps address these obstacles: the values are centred, and then scaled.</p>

        <h4 use:registerHeading>Centring</h4>
        <p>Centring removes the offset caused by the recording. For dynamics and timbre, each recording's own median is subtracted, so that what remains is how a beat relates to the normal level of that recording rather than to an absolute one.</p>
        <p>The median is used rather than the mean because it is robust against outliers, and this material has them: a single fortissimo chord can sit fifteen decibels above the perceived level, and a note held under a fermata can drag the measured tempo far down. Either would pull a mean disproportionately.</p>
        <p>Tempo is deliberately not centred per recording. That one performance is generally faster than another is an interpretive statement, not a recording artefact, and centring would remove exactly that information. Its reference point is therefore drawn from the whole corpus and is the same for every recording — which also means it cancels out of any comparison between two of them.</p>

        <h4 use:registerHeading>Scaling</h4>
        <p>Scaling makes the parameters commensurable. Each centred value is divided by a measure of typical spread, so the result says by how many typical units a beat lies above or below what is normal for its recording.</p>
        <p>The measure used is the median absolute deviation rather than the standard deviation. The reasoning is the same as for the median: a standard deviation is defined around the mean and squares its deviations, so it is pulled by the same outliers. Combining a robust centre with a non-robust spread would mix two incompatible views of what counts as typical. The figure is multiplied by 1.4826, which puts it on the same scale a standard deviation would have for normally distributed data, so that a value of two continues to mean what it used to.</p>
        <p>Every scale figure is pooled across all recordings, so that one unit means the same thing everywhere. Only in that way can a deviation in one recording be set against a deviation in another.</p>

        <h4 use:registerHeading>Why the scale depends on the scope</h4>
        <p>What varies is the level at which the deviations are formed, and it has to match the question being asked.</p>
        <p>When a single song or a range of measures is examined, only the variation within that song is at stake, and the scale is built from deviations against the level of that song, kept apart for each of the twenty-four. When the whole cycle or a half of it is examined, the differences between loud and quiet songs belong to the question, and the scale is built from deviations against the overall level of the recording.</p>
        <p>Using the wrong one has visible consequences. A song that is quiet in the context of the cycle, measured against a cycle-wide reference, would have all its values far below the reference point; since the display is clamped at two units, much of it would fall into the clipped region and appear uniform. Exactly the internal gradation one wants to see would be lost. The application selects the appropriate scale automatically from the scope you chose.</p>

        <h3 use:registerHeading>Reading the ribbons</h3>
        <p>In the semicircular ribbon, the width of a segment is proportional to the duration of that beat in seconds, not to its position in the score. A passage taken slowly therefore occupies more of the semicircle than a fast one of the same number of beats. The sum of all widths is the semicircle, so the ribbon shows the proportions within one performance rather than absolute durations.</p>
        <p>The radial extent encodes the normalized dynamics and the colour the normalized timbre. Both are mapped to the interval from zero to one, which requires clamping the normalized values at two units in either direction. Without that clamp a single extreme beat would compress everything else into a narrow band around the middle; the clamp trades resolution at the extremes for resolution in the range where the great majority of values lie. Beats beyond two units are shown at the limit and are not distinguishable from one another.</p>
        <p>In the linear ribbons of the comparison view the horizontal axis is elapsed time, shared by all recordings and scaled to the longest of them. Here the absolute duration is therefore readable, and a slower reading is visibly wider.</p>

        <h3 use:registerHeading>Reading the line graph</h3>
        <p>The horizontal axis of the line graph carries measure and beat labels, not elapsed time. The points are evenly spaced, so a slow passage takes up no more room than a fast one. It is a position axis, and reading tempo from the spacing would be a mistake.</p>
        <p>The vertical axis spans the range the data actually occupy and does not necessarily begin at zero. For dynamics this is unavoidable, since the values are negative decibels; for the other parameters it means the visible variation is shown at full resolution rather than compressed against a zero that no measurement approaches.</p>
        <p>Beats without a usable value are omitted while their measure labels are retained, so that lines with gaps stay aligned with one another. Were the values simply removed and drawn by index, every subsequent point of that recording would shift by one and the comparison would be worthless.</p>

        <h3 use:registerHeading>Reading the similarity network</h3>
        <p>The network positions recordings by a force simulation, in which each edge acts as a spring whose rest length is proportional to the computed distance. The arrangement therefore approximates the distances rather than reproducing them.</p>

        <h4 use:registerHeading>What the layout can and cannot show</h4>
        <p>With more than three recordings, arbitrary distance relationships generally cannot be realised exactly in the plane. Two nodes may sit close together although their distance is middling, simply because the remaining constraints allowed no better arrangement. The residual distortion is not displayed, and the spatial arrangement should be read as an indication rather than a measurement. The matrix view is the remedy: it shows every figure exactly.</p>
        <p>The edge widths are a deliberate redundancy. Since the arrangement cannot reproduce the distances exactly, the width provides a second, independent encoding of the same quantity.</p>

        <h4 use:registerHeading>The similarity percentage</h4>
        <p>Clicking an edge shows a percentage. It is computed relative to the largest distance in the current graph, so the least similar pair always reads as zero per cent.</p>
        <p>This figure is purely relative and must be read with care. It changes for a given pair as soon as another, less similar recording is added, because the reference changes with it. With exactly two recordings selected it is always zero per cent, which says nothing about those two. The distance itself, shown beside it, is the figure to rely on.</p>

        <h3 use:registerHeading>Reading the distance matrix</h3>
        <p>The matrix shows the same figures without any embedding. Its colour scale runs from light to dark in a single hue, light meaning similar; the two ends of the scale are labelled with the smallest and largest distance in the current selection, so the colours are relative to what is on screen while the numbers behind them are not.</p>
        <p>The distance itself is an average deviation per beat, measured in the normalized units described above. A value of 1.5 over three parameters means that the two recordings differ, on average, by roughly nine tenths of a typical unit in each parameter. Because it is an average per beat rather than a sum, it remains comparable between songs and between scopes — unlike the raw accumulated figure, which grows with the number of beats compared.</p>
        <p>Dashed empty cells mark pairs the application refused to compare. This happens when the two recordings do not line up: when a song is missing from one of them, or when the beat counts of a song differ by more than three. Rather than compute a figure that would look like any other, the comparison is declined and the reason given above the display.</p>

        <h3 use:registerHeading>What the figures do not tell you</h3>
        <p>A distance reduces the whole course of two performances to a single number, and that number says nothing about where they diverge. Two recordings may differ moderately throughout or agree closely everywhere except in one passage, and arrive at the same figure.</p>
        <p>Nor does a small distance mean two performances sound alike. The comparison runs on three measured quantities; articulation, diction, vibrato, phrasing and everything below the resolution of a single beat are not part of it. The aggregation to one value per beat is itself a loss: a beat that begins with a sharp accent and a beat of even level can yield the same measurement.</p>
        <p>What the figures do provide is a reliable way to decide which of many recordings are worth listening to closely, and a means of substantiating an impression that would otherwise remain an assertion.</p>

        <h2 use:registerHeading>Technical description</h2>
        <p>This chapter describes where the data come from, how they were prepared, and how the comparisons are computed. It is not needed to work with the application, but it is needed to judge what the results are worth.</p>

        <h3 use:registerHeading>Where the data come from</h3>
        <p>The application has no database in the conventional sense. All material lives in a private GitHub repository, which the application only ever reads, through the GitHub programming interface. The volume is small enough that the arguments usually made for a database do not apply: 26 recordings of 24 songs amount to some thirty megabytes, alongside twenty-four score files of about seven megabytes in total.</p>
        <p>The arrangement brings with it properties a research dataset needs and a version control system supplies by itself: a complete and immutable history of changes, a content-based identity for every version of every file, differences between any two points in time, and an established access model. The cost is a certain latency, since every request reaches out to an external service, and the absence of a query language.</p>
        <p>Everything is encoded in the format of the Music Encoding Initiative, an XML-based standard that has become the reference format in digital musicology. Its capacity to mark editorial additions as such and attribute them to a source is what makes the handwritten entries and the measured values expressible in the same document.</p>

        <h3 use:registerHeading>The three measured parameters</h3>
        <p>The measurements were made in Sonic Visualiser. The first and most laborious step is the manual setting of beat markers while listening. This cannot readily be automated: beat detection in art music with strongly fluctuating tempo, free agogics and a partly veiled metre is difficult for automatic methods, and in song accompaniment, where rubato is a constitutive device, automatic beat trackers give unreliable results.</p>
        <p>The tempo follows from these markers directly. If a beat falls at one point in time and the next at another, the interval between them is the duration of that beat, and sixty divided by that duration is the local tempo in beats per minute. Tempo is thus not measured but derived, which is why it is invariant against everything the recording chain does.</p>
        <p>The dynamics come from a smoothed power curve, expressed as a level in decibels relative to full scale. Smoothing over a time window is unavoidable, since the instantaneous amplitude of an audio signal oscillates with the waveform; the length of that window is a compromise between preserving transients and obtaining a steady reading.</p>
        <p>The timbre is captured by the spectral centroid, the magnitude-weighted mean of the frequencies in a short-time spectrum. It is a serviceable approximation of perceived brightness. Two limitations should be kept in mind. It reacts to the frequency response and bandwidth of the recording chain, which is why absolute values from different eras are not comparable. And because voice and piano are not on separate tracks in any of these recordings, what is measured is the timbre of the combined sound, not that of the voice alone.</p>
        <p>These per-beat values are written into MEI files that mirror the structure of the score, so that every measured beat can be located in the notation. Since MEI has no element for the beat as such, the values are carried by tempo, dynam and annot elements within an add block, one per measure.</p>

        <h3 use:registerHeading>The statistics pipeline</h3>
        <p>The reference figures for normalization are not computed by the application. They are produced in the database repository itself, by a script that a continuous integration job runs on every change to the performance data, and are stored there as JSON files alongside the material they describe.</p>
        <p>There are three reasons for this arrangement. All files are available locally to that script, so a complete recomputation takes seconds and needs no incremental bookkeeping. The figures are a property of the data rather than of the display, and change exactly when the data change. And they are versioned along with the material, so that for any state of the data the corresponding state of the statistics can be inspected.</p>
        <p>The same run produces a data quality report. It records files that could not be read, songs in which a substantial share of measurements is missing, and songs whose beat counts differ markedly between recordings. These are the conditions that would otherwise distort comparisons unnoticed.</p>
        <p>The application reads these figures and keeps them briefly in memory, so that a display involving ten recordings does not issue ten requests.</p>

        <h3 use:registerHeading>How distances are computed</h3>
        <p>Two performances of the same piece are never temporally congruent. Even at the same average tempo, stretches and accelerations are distributed differently, so the nth measured beat of one recording need not correspond to the same musical moment as the nth of the other.</p>

        <h4 use:registerHeading>Alignment</h4>
        <p>Dynamic time warping addresses this by optimising the correspondence rather than assuming it. From the two sequences it builds a matrix of local distances between every pair of beats, and then finds the path through that matrix with the lowest total cost, subject to three conditions: it runs from the first pair to the last, it never moves backwards in either sequence, and it advances in single steps. The total cost of that path is the distance.</p>
        <p>The local distances come from SciPy and the alignment from the dtw-python package, a port of a widely cited R package. Neither is implemented here. The choice is deliberate: an own implementation would require standing behind every detail of its behaviour, whereas a citable library makes the result reproducible for others.</p>

        <h4 use:registerHeading>The step pattern and the band</h4>
        <p>Of the available step patterns the application uses the one that charges each step once, which keeps the alignment close to the diagonal and departs from it only where the data force it. This matches the purpose here: the recordings follow the same score, so beat i corresponds to beat i, and the alignment exists to absorb the last measurement errors that careful checking has left, not to discover a correspondence.</p>
        <p>The path is additionally confined to a band around the diagonal, three beats wide over and above whatever the difference in length already requires. Without it the alignment wanders: measured on two recordings of a song of 273 beats, an unconstrained alignment strayed up to 64 beats from the diagonal and thereby matched passages that have nothing to do with one another.</p>
        <p>Where the scope covers several songs, each song is aligned against its own counterpart and the results are summed, rather than concatenating everything into one long sequence. Concatenation would let the path cross the boundary between two songs, matching the close of one against the opening of the next, and would let a difference in length early in the cycle displace everything after it.</p>

        <h4 use:registerHeading>Refused comparisons</h4>
        <p>A band that grew without limit would still find a path where none is meaningful. If two recordings of the same song differ by a hundred beats, any figure computed across that difference would be worthless, and producing one would conceal a defect in the data.</p>
        <p>The application therefore declines rather than computes. If the beat counts of a song differ by more than three, if a song is missing from one recording, or if a song carries no usable values, that pair receives no figure and the reason is displayed. The tolerance of three follows from the material: across the corpus, beat counts of the same song differ by nought to two beats.</p>

        <h4 use:registerHeading>The two distance measures</h4>
        <p>The Euclidean distance treats the parameters as mutually independent. Where they are not — where louder passages tend also to be slower, for instance — the shared component is counted twice.</p>
        <p>The Mahalanobis distance corrects this by taking the covariance into account. It amounts to an ordinary Euclidean distance after a transformation that decorrelates the data and brings every direction to unit variance. Musically it means that a deviation following the usual relationship between the parameters counts for less than one running against it.</p>
        <p>One limitation should be named. The covariance is estimated from the data of the current request, not from the whole corpus, so the measure depends on which recordings happen to be selected; two requests with overlapping but different selections strictly use different measures.</p>

        <h4 use:registerHeading>The reported figure</h4>
        <p>The accumulated distance grows with the number of beats compared, so two recordings of the whole cycle necessarily have a larger distance than the same two of a single song. Within one request this is harmless, since all distances are computed under the same scope; between requests a comparison of the raw figures would simply be wrong.</p>
        <p>The application therefore divides by the number of beats compared and reports that average. The denominator is fixed before the computation and does not depend on the path the optimisation took, which is what makes the figure comparable between songs and scopes.</p>

        <h3 use:registerHeading>Architecture</h3>
        <p>The application is divided into a backend written in Python with FastAPI and a frontend written in TypeScript with SvelteKit. As much of the processing as possible happens on the server: parsing the XML, normalizing the series and computing the distance matrices, whose cost grows with the square of the sequence length. A browser tab runs its scripts in a single thread that is also responsible for drawing, so a lengthy computation there would freeze the interface.</p>
        <p>The one substantial exception is the engraving of the notation, which Verovio performs in the browser. Doing it on the server would either yield images that are no longer interactive, or require a request for every change of a layout setting.</p>
        <p>Purely presentational options — the colour scheme, node size, edge width — are deliberately arranged to need no recomputation and take effect immediately.</p>
        
        <h2 use:registerHeading>About and Credits</h2>
        <h3 use:registerHeading>Used frameworks and libraries</h3>
        <table>
            <tbody>
                <tr>
                    <td class="a">Frontend framework</td>
                    <td class="b"><a href="https://svelte.dev/docs/kit/introduction">SvelteKit</a></td>
                </tr>
                <tr>
                    <td class="a">UI components and animations</td>
                    <td class="b"><a href="https://tailwindcss.com/">TailwindCSS</a><br><a href="https://daisyui.com">DaisyUI</a><br><a href="https://gsap.com">GSAP</a></td>
                </tr>
                <tr>
                    <td class="a">Visualizations</td>
                    <td class="b"><a href="https://d3js.org">d3.js</a></td>
                </tr>
                <tr>
                    <td class="a">Map</td>
                    <td class="b"><a href="https://leafletjs.com/">Leaflet</a><br><a href="https://sveaflet.vercel.app/">Sveaflet</a></td>
                </tr>
                <tr>
                    <td class="a">Backend framework</td>
                    <td class="b"><a href="https://fastapi.tiangolo.com/">FastAPI</a></td>
                </tr>
                <tr>
                    <td class="a">MEI engraving</td>
                    <td class="b"><a href="https://www.verovio.org/index.xhtml">Verovio</a></td>
                </tr>
            </tbody>
        </table>
 
        <h3 use:registerHeading>Note on the use of Generative AI</h3>
        <p>Generative AI was used to help create some of the frontend components and parts of the backend routes. Additionally, it was used to translate parts of the application logic from pseudocode to machine-readable Python code.
        </p>

        <h3 use:registerHeading>MIT Licence</h3>        
        <p>Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights
            to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is urnished to do so, subject to the following conditions:
        </p>
        <p>The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.</p>
        <p>THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
            FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
            LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
        </p>

    </div>
</div>

<style>
    /* svelte-ignore css-unused-selector */
    h1 { 
        font-size: var(--text-4xl);
        line-height: var(--tw-leading, var(--text-4xl--line-height));
        margin-bottom: calc(var(--text-4xl) / 3);
        margin-top: calc(var(--text-4xl) / 3);
    }

    h2 { 
        font-size: var(--text-3xl);
        line-height: var(--tw-leading, var(--text-3xl--line-height));
        margin-bottom: calc(var(--text-3xl) / 3);
        margin-top: calc(var(--text-3xl) / 3);
    }

    h3 { 
        font-size: var(--text-2xl);
        line-height: var(--tw-leading, var(--text-2xl--line-height));
        margin-bottom: calc(var(--text-2xl) / 3);
        margin-top: calc(var(--text-2xl) / 3);
    }

    h4 { 
        font-size: var(--text-xl);
        line-height: var(--tw-leading, var(--text-xl--line-height));
        margin-bottom: calc(var(--text-xl) / 3);
        margin-top: calc(var(--text-xl) / 3);
    }

    p { 
        font-size: var(--text-lg);
        line-height: var(--tw-leading, var(--text-lg--line-height));
        margin-bottom: calc(var(--text-lg) / 3);
        margin-top: calc(var(--text-lg) / 3);
    }

    table {
        margin-top: calc(var(--spacing) * 3);
        width: 75%
    }

    td {
        width: 50%;
        border: 1px dotted #668ba4;
        padding: calc(var(--spacing) * 2);
        font-size: var(--text-lg);
        border-radius: 12px;
    }

    td a {
        text-decoration: underline;
        color: #668ba4;
    }




    
</style>