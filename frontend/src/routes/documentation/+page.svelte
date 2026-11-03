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
    
    /** Numbers the headings, sets their ids and returns them for the table of contents. */
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
        <p>This application compares 26 recordings of Schubert's <i>Winterreise</i> by Dietrich Fischer-Dieskau, made between 1948 and 1990 with twelve different pianists. It renders the annotated MEI score with Verovio and visualizes three quantities measured for every beat of every recording: tempo, dynamics and timbre.</p>
        <p>This page describes what each part of the application is for, how it works, and what it can and cannot show.</p>
            
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

        <h2 use:registerHeading>Overview</h2>
        <p>The application has two halves. The score viewer shows the notated text together with Fischer-Dieskau's handwritten entries. The visualizations show what was played, measured beat by beat. Both are reached from the navigation bar.</p>
        <p>All data are fetched on demand from a private GitHub repository. Nothing needs to be installed or uploaded; the first request on a page takes a moment while the files arrive.</p>

        <h3 use:registerHeading>The measured parameters</h3>
        <p><b>Tempo</b> in beats per minute. Beat markers were set by hand while listening; the tempo of a beat is sixty divided by the time to the next marker.</p>
        <p><b>Dynamics</b> as a sound level in decibels relative to full scale (dBFS), taken from a smoothed power curve.</p>
        <p><b>Timbre</b> as the spectral centroid in hertz, the magnitude-weighted mean frequency of the spectrum. Voice and piano are not separated, so it describes the combined sound.</p>
        <p>The values are stored in MEI files that mirror the structure of the score. Each beat is labelled by measure and beat number, for example 12.2 for the second beat of measure 12; measure 0 is the pickup.</p>

        <h3 use:registerHeading>Raw and normalized values</h3>
        <p>The line graph, the data tables and the information panels show raw values in their units. The ribbons and the similarity network use normalized values: each value minus a centre, divided by a scale. Tempo and timbre are log-transformed first.</p>
        <p>The centre for dynamics and timbre is the mean of the recording itself, so these values describe how a beat relates to the usual level of its recording. The centre for tempo is the same for all recordings, so a generally faster or slower performance remains visible. The scale is the standard deviation pooled across all recordings, so one unit means the same in every recording. A normalized value of 1 lies one standard deviation above the centre.</p>
        <p>Centres and scales depend on the scope. For a single song or a range of measures they are taken from that song; for half the cycle or the whole cycle from the complete recording. The backend can use median and median absolute deviation instead of mean and standard deviation (<code>normalization=median</code>); the interface uses mean and standard deviation.</p>
        <p>Normalization makes recordings comparable but removes information. Differences in overall loudness and brightness between recordings disappear, whether they come from the recording technique or from the performance. Raw dynamics and timbre values of recordings from different decades cannot be compared directly, since microphones, transfer and mastering influence them.</p>

        <h2 use:registerHeading>The components</h2>

        <h3 use:registerHeading>Timeline and map</h3>
        <p>The landing page shows the recordings either on a timeline or on a map, switched with a toggle. On the timeline each bar is one recording; clicking it opens date, pianist (with a link to the GND authority record), place, recording context and, where available, a link to further information. On the map each place carries one marker; its popup lists all recordings made there.</p>
        <p>Use it to get an overview of the corpus. It shows metadata only, no measurements.</p>

        <h3 use:registerHeading>Score viewer</h3>
        <p>Choose a song from the dropdown; the score is engraved in your browser. Three sliders change scale, spacing and minimum page height; they take effect without reloading. The page controls below the score turn the pages.</p>

        <h4 use:registerHeading>Colours and the information panel</h4>
        <p>Entries from Fischer-Dieskau's working copies are violet and turn orange under the pointer. Elements supplied by editors are green and turn brown under the pointer. Elements an editorial annotation refers to are dark cyan.</p>
        <p>Clicking an element opens a panel. For a note it shows pitch with accidental (marked if the accidental is only gestural, that is, sounding but not written), duration, measure, the syllable for notes of the voice, and any annotations attached to it. For one of Fischer-Dieskau's entries it shows the kind of marking (directive for interpretation, crescendo or diminuendo hairpin, tempo or dynamics instruction, trill, slur, fermata), its type and label, the writing medium, the reason if the reading is uncertain, and an annotation if there is one. For an annotation it shows its text.</p>

        <h4 use:registerHeading>What the score viewer can and cannot do</h4>
        <p>It shows Fischer-Dieskau's entries in the context of the printed text, together with the editorial information carried in the encoding.</p>
        <p>It is not linked to the recordings: it shows no measured values and plays no audio. An entry is classified by its first encoded element only. Large songs take a second or two to engrave.</p>

        <h3 use:registerHeading>Line graph</h3>
        <p>Choose a song, one parameter and any number of recordings. Each recording is drawn as a line of raw values in the parameter's unit. The horizontal axis carries the beat labels of the first selected recording at even spacing; the vertical axis spans the range of the data and does not necessarily start at zero. Beats without a value are left out. The legend can be dragged; its position is kept in the exported image. "Show data table" lists the same values, with CSV export.</p>

        <h4 use:registerHeading>What the line graph can and cannot do</h4>
        <p>It shows exact values and is the most precise way to compare one passage across several recordings. It is the natural next step once the similarity network has pointed at a pair or a song.</p>
        <p>It shows one parameter at a time. The horizontal axis is a position axis, not a time axis: a slow passage takes no more room than a fast one. Recordings are matched by beat label, not aligned, so a beat missing from the first selected recording is not shown. Because the values are raw, dynamics and timbre also reflect the recording technique. With many recordings the lines overlap.</p>

        <h3 use:registerHeading>Multi-parameter ribbon</h3>
        <p>Choose a recording and a song. The performance is drawn as a semicircle with one segment per beat, and each segment encodes all three parameters:</p>
        <p><b>Angle:</b> the duration of the beat as a share of the whole performance. A slower beat is a wider segment.<br>
        <b>Length:</b> the normalized dynamics. A longer segment is louder.<br>
        <b>Colour:</b> the normalized timbre. A lighter colour is a brighter sound.</p>
        <p>Length and colour show normalized values limited to two standard deviations in either direction. Beats without a value are drawn at the middle of the range. The colour scheme can be changed (Viridis, Inferno, Cividis, blue, green or red shades); the choice applies to all ribbon views.</p>

        <h4 use:registerHeading>Selecting a passage</h4>
        <p>In "Select single beat" mode, clicking a segment shows the raw values of that beat. In "Draw selection of beats" mode, dragging across the ribbon selects a range. The selection can then be shown on its own ("Visualize only these beats"), carried over to the comparison view ("Compare with other performances", with an animated transition), or discarded. "Back to complete performance" restores the full song. "Show data table" lists the raw values.</p>

        <h4 use:registerHeading>What the ribbon can and cannot do</h4>
        <p>It shows all three parameters of a performance at once, so the overall shape of a song (where it slows down, swells or brightens) is visible at a glance.</p>
        <p>It shows one recording only. Angles show proportions within the performance, not absolute durations. Values beyond two standard deviations are drawn at the limit and cannot be told apart. Length and colour can be read only approximately; exact values are available by clicking. Perceived colour differences depend on the scheme.</p>

        <h3 use:registerHeading>Comparison view</h3>
        <p>The passage selected in the ribbon is shown as linear ribbons, one per recording, one below the other. The horizontal axis is elapsed time in seconds, shared by all ribbons and scaled to the longest of them. Width, height and colour of a segment encode duration, normalized dynamics and normalized timbre. The recording you started from stays at the top; others are added in the sidebar. "Display score measures" shows the score of the passage beside the ribbons.</p>
        <p>Clicking a beat shows its values. With "Same measure in each performance" the same beat is selected in every ribbon; with "Each performance individually" each ribbon keeps its own selection.</p>

        <h4 use:registerHeading>What the comparison view can and cannot do</h4>
        <p>It compares the timing of a passage directly, including absolute duration, and shows where readings diverge in all three parameters.</p>
        <p>The beats are not aligned: the same beat appears at a different horizontal position in each recording, and long passages become narrow. The limit of two standard deviations applies here too.</p>

        <h3 use:registerHeading>Similarity network</h3>
        <p>The network compares whole recordings, or passages of them. It computes a distance and a rank correlation for every pair of selected recordings and shows the result as a graph or as a matrix.</p>

        <h4 use:registerHeading>Settings</h4>
        <p><b>Scope:</b> the whole cycle, one half (Erste Abtheilung, songs 1–12, or Zweite Abtheilung, songs 13–24), a single song, or a range of measures within a song given by start and end measure and beat.</p>
        <p><b>Parameters:</b> any combination of tempo, dynamics and timbre. Only beats with a value for every selected parameter are used, so adding a parameter can reduce the number of beats compared.</p>
        <p><b>Weights:</b> with more than one parameter and the Euclidean metric, a slider for each parameter sets its relative weight; the percentage shows its share.</p>
        <p><b>Metric:</b> Euclidean treats the parameters as independent. Mahalanobis takes their correlation into account, using the covariance of the whole corpus (or of the current selection where corpus figures are missing); weights do not apply.</p>
        <p><b>Recordings:</b> any selection. "Generate Network" starts the computation; a progress bar shows loading and comparing, with an estimate of the remaining time.</p>

        <h4 use:registerHeading>How the distance is computed</h4>
        <p>Two performances never run in parallel beat for beat. Dynamic time warping (DTW) therefore aligns them: it finds the path through all pairs of beats with the lowest total cost, from the first pair to the last, never moving backwards. The cost of a pair of beats is the distance between their normalized values.</p>
        <p>Each song is aligned separately, within a band around the diagonal of the difference in beat counts plus two beats. For several songs the costs are summed. The application reports the total cost and the cost per beat (total divided by the number of beats of the longer recording per song); the network and the matrix use the cost per beat.</p>
        <p>A pair is not compared if a song is missing in one recording, has no usable beats, or if the beat counts of a song differ by more than three. Such pairs have no value, and the reasons are listed above the result.</p>

        <h4 use:registerHeading>Kendall's tau and its floor</h4>
        <p>Kendall's τ is computed along the same alignment path. It measures whether two performances rise and fall together, regardless of how far apart their values are: 1 means the same rank order throughout, 0 no relation. It is computed per parameter and combined with the same weights as the distance; over several songs it is averaged, weighted by the length of each song's path.</p>
        <p>Music with repeated material yields a positive τ even without any real correspondence between performances. The floor estimates this: τ between one recording and the other rotated by 12, 25, 33 and 50 percent of the song, taking the highest value. Strophic songs have high floors. Only the difference between τ and its floor is informative, and it cannot be compared between songs.</p>

        <h4 use:registerHeading>The network</h4>
        <p>Each node is a recording, each link a compared pair. A force simulation places the nodes, with link length proportional to the cost per beat; links are wider for more similar pairs. Nodes can be coloured by recording year, pianist or recording context, with a legend in the top left corner. Sliders change node size and link width. Nodes can be dragged; the view can be zoomed and panned.</p>
        <p>Clicking a node shows its label. Clicking a link shows the total DTW cost and τ of the pair; "More information" opens the pair details.</p>

        <h4 use:registerHeading>The matrix</h4>
        <p>The matrix shows every pair once, as a lower triangle. The colour shows the cost per beat in seven steps from light (similar) to dark (different); the legend gives the smallest and largest value of the current selection. Hovering over a cell shows the pair and its value, clicking opens the pair details. Pairs that were not compared appear as dashed empty cells. The full matrix can be exported as CSV.</p>

        <h4 use:registerHeading>Pair details</h4>
        <p>The detail view summarises a pair: total cost and cost per beat, τ and its floor, and the number of beats and songs compared.</p>
        <p><b>Largest differences:</b> stretches of about eight beats along the alignment path, non-overlapping, at most ten per parameter, ordered by the difference in normalized units. Each row gives song, parameter, measures, the recording with the higher value, and both recordings' mean raw values (bpm, dBFS, Hz).</p>
        <p><b>For a single song:</b> τ, floor and their difference per parameter, and the beat counts of both recordings.</p>
        <p><b>For several songs:</b> a table per song with τ, floor, their difference (highlighted below 0.1), and cost per beat, sortable by song or by τ minus floor. Songs present in only one of the recordings are listed. All tables can be exported as CSV.</p>

        <h4 use:registerHeading>What the network can and cannot do</h4>
        <p>It gives an overview where comparing by eye is impossible: twenty recordings already form 190 pairs. It shows groupings, and points to the pairs, songs and passages worth examining in the other views. Colouring by metadata shows whether groupings follow year, pianist or context. Distance and τ complement each other: the distance measures how far apart two performances are, τ whether they are shaped alike.</p>
        <p>The layout approximates the distances; with more than three recordings they generally cannot be represented exactly in the plane, and the positions change from run to run. The matrix shows the exact values. Matrix colours are relative to the current selection. A single value per pair does not say where two performances differ: a moderate difference throughout and a single divergent passage can give the same figure. Only three parameters per beat enter the comparison; articulation, diction, vibrato and anything shorter than a beat do not. With more than ten pianists, colours repeat. Large selections over the whole cycle take some time to compute.</p>

        <h3 use:registerHeading>Saving what you see</h3>
        <p>Each visualization can be saved as an SVG file, which scales without loss and can be edited in a vector graphics program. Tables, the matrix and the pair details can be saved as CSV. Highlights that exist only during interaction are not part of the saved file.</p>

        <h2 use:registerHeading>Technical description</h2>

        <h3 use:registerHeading>Data source</h3>
        <p>All material lives in a private GitHub repository, which the application reads through the GitHub API as a GitHub App. Scores and performance data are encoded in MEI (Music Encoding Initiative). There is no separate database. The backend keeps fetched files in memory for ten minutes and statistics for five.</p>

        <h3 use:registerHeading>Statistics pipeline</h3>
        <p>A script in the database repository runs on every change to the performance data. It computes means, standard deviations, medians and median absolute deviations per recording, per song and for the corpus, and the covariance of the three parameters, and stores them as JSON files. It also writes a data quality report listing unreadable files, songs with many missing values and songs whose beat counts differ between recordings.</p>

        <h3 use:registerHeading>Architecture</h3>
        <p>The backend is written in Python with FastAPI. It fetches and parses the MEI files, normalizes the series and computes distances, using SciPy for the local costs and dtw-python for the alignment. The frontend is written in TypeScript with SvelteKit; it engraves the score with Verovio in the browser and draws the visualizations with d3. The network computation is streamed to the browser with progress updates. Display options such as colours and sizes take effect without recomputation.</p>

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
        <p>Generative AI was used to translate parts of the application logic from pseudocode to machine-readable Python code as well as assisting in the creation of frontend components and generating documentation files. 
        </p>

        <h3 use:registerHeading>MIT Licence</h3>        
        <p>Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights
            to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
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