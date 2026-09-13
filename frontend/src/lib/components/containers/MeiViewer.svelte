<script lang="ts">
    import { onMount } from 'svelte';
    import PageControls from '../partials/PageControls.svelte';
	import type { HTMLAttributes } from 'svelte/elements';
    
    let {src, scale = $bindable(50), spacingPercent = $bindable(25), pageHeight = $bindable(1000),
         rendered = $bindable(false)}:
        {src: string; scale: number; spacingPercent: number; pageHeight: number;
         rendered?: boolean } = $props();

    let meiDocument: Document;
    
    let svg = $state('');
    let error = $state('');
    let currentPage = $state(1);
    let totalPages = $state(1);
    let toolkitReady = $state(false);
    let vrvToolkit: any;
    let pageWidth = $state(0)

    let meiIdMap = new Map<string, Element>();
    
    let viewportHeight = $state(0);
    
    const baseLayoutOptions = {
        spacingSystem: 0,
        spacingStaff: 5,
        adjustPageHeight: true,
        scaleToPageSize: true,
        footer: 'none',
        breaks: 'smart',
        breaksSmartSb: 1.0,
        spacingLinear: 1.0,
    };

    const capitalize = (s: string) =>
        s ? s[0].toUpperCase() + s.slice(1) : "";
    
    function buildMeiIdMap(meiDoc: Document) {

        meiIdMap.clear();

        const all = meiDoc.getElementsByTagName("*");

        let count = 0;

        for (const el of Array.from(all)) {
            const id = el.getAttribute("xml:id");
            if (id) {
                meiIdMap.set(id, el);
                count++;
            }
        }
    }

    // xml:id of an annotated element -> the annots pointing at it
    let annotMap = new Map<string, Element[]>();

    function buildAnnotMap(meiDoc: Document) {

        annotMap.clear();

        const all = Array.from(meiDoc.getElementsByTagName("*"));

        for (const annot of Array.from(meiDoc.getElementsByTagName("annot"))) {
            // annots inside add are handled in the addEl block
            if (annot.closest("add")) continue;

            const startEl = meiIdMap.get(annot.getAttribute("startid")?.replace("#", "") ?? "");
            const endEl = meiIdMap.get(annot.getAttribute("endid")?.replace("#", "") ?? "");
            const plist = annot.getAttribute("plist");

            let scope: Element[] = [];

            if (plist) {
                // c) all listed elements
                scope = plist.split(" ").map(ref => meiIdMap.get(ref.replace("#", ""))).filter(el => el !== undefined);
            } else if (startEl && endEl) {
                // b) start, end and everything in between in document order (endid sometimes precedes startid)
                const [from, to] = [all.indexOf(startEl), all.indexOf(endEl)].sort((a, b) => a - b);
                // only within the annot's staves: across a barline, the other staves' notes lie in between as well
                const staves = annot.getAttribute("staff")?.split(" ")
                    ?? [startEl, endEl].map(el => el.closest("staff")?.getAttribute("n") ?? el.getAttribute("staff") ?? "");

                scope = all.slice(from, to + 1).filter(el =>
                    el === startEl || el === endEl
                    || (el.localName !== "staff" && el.localName !== "measure"
                        // layer, beam or chord that open in between but close after the end
                        && !el.contains(all[to])
                        && staves.includes(el.closest("staff")?.getAttribute("n") ?? ""))
                );
            } else if (startEl) {
                // a) only this one element
                scope = [startEl];
            }

            for (const el of scope) {
                const id = el.getAttribute("xml:id") ?? "";
                annotMap.set(id, [...(annotMap.get(id) ?? []), annot]);
            }
        }
    }
    
    function clampCurrentPage() {
        totalPages = vrvToolkit.getPageCount();
        if (currentPage > totalPages) currentPage = totalPages;
        if (currentPage < 1) currentPage = 1;
    }
    

    /**
     * Creates a hidden div element which renders all pages to determine the maximum height of all pages at the current layout.
     */
    function computeMaxViewportHeight() {
        const pages = vrvToolkit.getPageCount();
        let maxHeight = 0;
        
        const container = document.createElement('div');
        container.style.position = 'absolute';
        container.style.visibility = 'hidden';
        container.style.height = 'auto';
        container.style.width = 'auto';
        document.body.appendChild(container);
        
        for (let i = 1; i <= pages; i++) {
            container.innerHTML = vrvToolkit.renderToSVG(i);
            const svgEl = container.querySelector('svg');
            if (svgEl) {
                const h = svgEl.getBoundingClientRect().height;
                if (h > maxHeight) maxHeight = h;
            }
        }
        
        document.body.removeChild(container);
        viewportHeight = maxHeight;
    }
    
    function initMEI() {
        try {
            if (!src) return;
            
            meiDocument = new DOMParser().parseFromString(src, "text/xml");

            buildMeiIdMap(meiDocument);
            buildAnnotMap(meiDocument);
            
            vrvToolkit.loadData(src);
            
        } catch (e: any) {
            error = e.message;
            console.error('MEI load error:', e);
        }

    }

    export function doLayout() {
        vrvToolkit.setOptions({
            ...baseLayoutOptions,
            scale,
            spacingNonLinear: spacingPercent / 100,
            pageWidth,
            pageHeight,
            svgAdditionalAttribute: ["add@source", "unclear@reason", "dir@type", "dir@label"]
        });
        
        vrvToolkit.redoLayout();
        clampCurrentPage();
        computeMaxViewportHeight(); 
        renderPage();
    }
    
    function renderPage() {
        svg = vrvToolkit.renderToSVG(currentPage);
        rendered = svg.length > 0;
    }

    let svgContainer: HTMLDivElement | undefined;

    // colour the annotated elements after every render ({@html} replaces the nodes); the annot bar stays
    $effect(() => {
        if (!svg) return;
        for (const id of annotMap.keys()) {
            svgContainer?.querySelector(`[id="${id}"]`)?.classList.add("annotated");
        }
    });

    // one function for all clicks (notes, annots, adds)
    let clickContent = $state("");
    let clickType = $state("");
    let clickElement: HTMLDialogElement;

    function handleClick(event: Event) {
        if (!meiDocument) return;

        const target = event.target as Element;

        // Determine what type of MEI SVG element was clicked
        const noteEl = target.closest("g.note") as HTMLElement;
        const annotEl = target.closest("g.annot.score") as HTMLElement;
        const addEl = target.closest("g.add") as HTMLElement;

        if (noteEl) {
            
            const meiNote = meiIdMap.get(noteEl.id) || null;
            if (!meiNote) return;

            const duration = () => {
                let dur = 0;
                let dots = 0;
                if (meiNote.getAttribute("dur")) {
                    dur = parseInt(meiNote.getAttribute("dur") ?? "");
                    dots = meiNote.getAttribute("dots") ? parseInt(meiNote.getAttribute("dots") ?? "") : 0;
                } else if (meiNote.parentElement?.tagName === "chord") {
                    dur = parseInt(meiNote.parentElement?.getAttribute("dur") ?? "");
                    dots = meiNote.parentElement?.getAttribute("dots") ? parseInt(meiNote.parentElement.getAttribute("dots") ?? "") : 0;
                };
                let durStr = "";
                switch (dur) {
                    case 1:
                        durStr = "whole";
                        break;
                    case 2:
                        durStr = "half";
                        break;
                    case 4:
                        durStr = "quarter";
                        break;
                    case 8:
                        durStr = "eighth";
                        break;
                    case 16:
                        durStr = "sixteenth";
                        break;
                    case 32:
                        durStr = "thirty-second";
                        break;
                    default:
                        durStr = dur + "th";
                        break;
                }
                if (dots > 0) durStr = (dots === 2 ? "double-dotted " : "dotted ") + durStr;

                if (meiNote.closest("graceGrp")) return durStr + " grace note";
                const tuplet = meiNote.closest("tuplet");
                if (tuplet) return durStr + "-note " + (tuplet.getAttribute("num") === "3" ? "triplet" : "tuplet");
                return durStr + " note";
            }
            
            const staffAndMeasure = () => {
                let staff = "";
                let measure = "";

                let parent = meiNote.parentElement;

                while (parent && parent.tagName.toLowerCase() !== "measure") {
                    parent = parent.parentElement;
                    if (parent && parent.tagName.toLowerCase() == "staff") {
                        staff = parent.getAttribute("n") ?? "";
                    }                    
                }
                if (parent) {
                    measure = parent.getAttribute("n") ?? "";
                }
                return [staff, measure];
            } 

            let syllable = "";
            if (staffAndMeasure()[0] == "1") {
                clickType = "Note and syllable in singing voice";
                syllable = meiNote.getElementsByTagName("syl")[0].innerHTML;
            } else {
                clickType = "Note in piano voice"
            };

            const pitch = meiNote.getAttribute("pname");
            const octave = meiNote.getAttribute("oct");

            // find and return accidentals
            let accid = "";
            let accidGes = false;
            let accidAttr = null;
            if (meiNote.getAttribute("accid.ges") != null) {
                accidAttr = meiNote.getAttribute("accid.ges");
                accidGes = true;
            } else if (meiNote.getElementsByTagName("accid")[0]?.getAttribute("accid")) {
                accidAttr = meiNote.getElementsByTagName("accid")[0]?.getAttribute("accid");
            } else if (meiNote.getElementsByTagName("accid")[0]?.getAttribute("accid.ges")) {
                accidAttr = meiNote.getElementsByTagName("accid")[0]?.getAttribute("accid.ges");
                accidGes = true;
            };
            switch (accidAttr) {
                case "s":
                    accid = "\u{266F}";
                    break;
                case "f":
                    accid = "\u{266D}";
                    break;
                case "n":
                    accid = "\u{266E}";
                    break;
                case "ff":
                    accid = "\u{1D12B}";
                    break;
                case "ss":
                case "x":
                    accid = "\u{1D12A}";
                    break;
            };

            // annots pointing at the note, its chord or its children (accid, verse, syl, artic);
            // Set, because a start/end range contains the note and its verse and syl alike
            const annots = new Set([meiNote, meiNote.closest("chord"), ...Array.from(meiNote.getElementsByTagName("*"))]
                .flatMap(el => annotMap.get(el?.getAttribute("xml:id") ?? "") ?? []));
            const annotText = Array.from(annots).map(a => a.textContent?.trim()).filter(Boolean).join("; ");

            clickContent = "Note: " + pitch + accid + octave + (accidGes? " (gestural accidental)" : "")
                + "\nLength: " + duration()
                + "\nMeasure: " + staffAndMeasure()[1] + (syllable !== "" ? "\nSyllable: " + syllable : "")
                + (annotText !== "" ? "\nAdditional information: " + annotText : "");
            clickElement?.showModal();

        } else if (annotEl) {
            clickType = "Annotation";

            const meiAnnot = meiIdMap.get(annotEl.id) || null;
            if (!meiAnnot) return;

            // Annotation content is taken directly from MEI text node
            clickContent = meiAnnot.textContent || "";
            clickElement?.showModal();

        } else if (addEl) {
            clickType = "Addition by Fischer-Dieskau";

            const meiAdd = meiIdMap.get(addEl.id) || null;
            if (!meiAdd) return;

            // First meaningful child (ignoring handShift markup elements)
            const child = Array.from(meiAdd.children)
                .find(el => el.localName !== "handShift" && el.localName !== "annot") || null;

            const firstDirChild = Array.from(meiAdd.children)
                .filter(el => el.localName === "dir")[0];

            // Classify type of musical addition based on first meaningful child
            let addClass = "";

            if (child?.localName == "dir") {
                addClass = "directive for interpretation";

            } else if (child?.localName == "hairpin") {
                if (child?.getAttribute("form") == "cres") {
                    addClass = "crescendo hairpin";
                } else if (child?.getAttribute("form") == "dim") {
                    addClass = "diminuendo hairpin";
                }

            } else if (child?.localName == "tempo") {
                addClass = "instruction for tempo";

            } else if (child?.localName == "dynam") {
                addClass = "instruction for dynamics";

            } else if (child?.localName == "trill" || child?.localName == "mordent") {
                addClass = "Trill/vibrato";

            } else if (child?.localName == "slur") {
                addClass = "slur";

            } else if (child?.localName == "fermata") {
                addClass = "fermata";
            }

            const handShift = meiAdd.querySelector("handShift");
            let addHandShift = "";

            if (handShift) {
                addHandShift = handShift.getAttribute("medium") || "";
            }

            const annot = meiAdd.querySelector("annot");
            let annotTag = "";

            if (annot) {
                annotTag = annot.textContent;
            }

            const addType = addClass;
            const medium = addHandShift.replace(/-/g, " ");
            const type = (firstDirChild?.getAttribute("type"))?.replace(/-/g, " ");
            const label = (firstDirChild?.getAttribute("label"))?.replace(/-/g, " ");

            // Some MEI additions may contain editorial uncertainty annotations
            const unclearReason = addEl.querySelector("tspan.unclear")?.getAttribute("data-reason");

            // Build modal content from available metadata fields
            clickContent = [
                capitalize(addType) + (unclearReason ? `, unclear (${unclearReason})` : ""),
                type ? `Type: ${type}` : "",
                label ? `Label: ${label}` : "",
                handShift ? `Medium: ${medium}` : "",
                annot ? `Additional information: ${annotTag}` : ""
            ]
                .filter(Boolean)
                .join("\n");

            clickElement?.showModal();

        } else {
            return;
        }
    }
    
    onMount(async () => {
        try {
            const createVerovioModule = (await import('verovio/wasm')).default;
            const { VerovioToolkit } = await import('verovio/esm');
            const VerovioModule = await createVerovioModule();
            vrvToolkit = new VerovioToolkit(VerovioModule);

            toolkitReady = true;
        } catch (e: any) {
            error = e.message;
            console.error(e);
        }
        
    });
    
    $effect(() => {
        if (!toolkitReady || !src) return;

        rendered = false;

        let frame = requestAnimationFrame(() => {
            frame = requestAnimationFrame(() => {
                initMEI();
                doLayout();
            });
        });
        return () => cancelAnimationFrame(frame);
    });

    function attachMeiContainer(node: HTMLDivElement) {
        node.addEventListener("click", handleClick);
        return () => node.removeEventListener("click", handleClick);
    }
    
</script>

<div class="viewer-container w-full" style="--viewport-height: {viewportHeight}px">
    {#if error}
        <p class="text-error">{error}</p>
    {/if}
    <div class="mei-svg w-full" bind:this={svgContainer} bind:clientWidth={pageWidth} {@attach attachMeiContainer}>
        {@html svg}
    </div>

    <dialog bind:this={clickElement} class="modal">
        <div class="modal-box">
            <form method="dialog">
                <button class="btn btn-sm btn-circle btn-ghost absolute right-2 top-2">✕</button>
            </form>
            <h3 class="text-lg font-bold">{clickType}</h3>
            <p style="white-space: pre-line;">{clickContent}</p>
        </div>
        <form method="dialog" class="modal-backdrop">
            <button>close</button>
        </form>
    </dialog>
    
    <div class="page-controls">
        <PageControls
        {currentPage}
        {totalPages}
        onPrev={() => { currentPage--; renderPage(); }}
        onNext={() => { currentPage++; renderPage(); }}
        />
    </div>
    
</div>

<style>
    .viewer-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 1.5rem;
        padding: 1rem;
        min-width: 400px;
        margin: 0 auto;
        border-radius: 8px;
    }
    
    .mei-svg {
        width: 100%;
        height: 100%;
        overflow: hidden;
        display: flex;
        justify-content: center;
        align-items: flex-start;
        
    }
    
    .mei-svg :global(svg) {
        transform-origin: top center;
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: rgba(254, 255, 223, .5);
    }
    
    .mei-svg :global(g.note) {
        transition: fill 0.15s ease, stroke 0.15s ease;
    }
    
    .mei-svg :global(g.note:hover) {
        fill: red;
        stroke: red;
        cursor: pointer;
    }
    
    .mei-svg :global(g.supplied) {
        color: yellowgreen;
        stroke: yellowgreen;
        fill: yellowgreen;
        
    }
    
    .mei-svg :global(g.supplied:hover) {
        color: brown;
        stroke: brown;
        fill: brown;

    }

    .mei-svg :global(g.annotated) {
        color: darkcyan;
        stroke: darkcyan;
        fill: darkcyan;
    }
    
    .mei-svg :global(g[data-source="#dwdfdc9075d0e-7aaa-4a82-bfa0-06eb81584587"]) {
        color: blueviolet;
        stroke: blueviolet;
        fill: blueviolet;
        cursor: pointer  
    }
    
    .mei-svg :global(g[data-source="#dwdfdc9075d0e-7aaa-4a82-bfa0-06eb81584587"]:hover) {
        color: orange;
        stroke: orange;
        fill: orange;
    }

    .modal-box {
        line-height: 3vh;
    }
    
    .page-controls {
        display: flex;
        flex-direction: column;
        align-items: center;
    }
</style>