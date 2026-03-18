<script lang="ts">
  import { onMount } from 'svelte';
  import PerformanceSelector from '$lib/components/PerformanceSelector.svelte';
  import ScoreSelector from '$lib/components/ScoreSelector.svelte';
  import MeiTable from '$lib/components/MeiTable.svelte';
  import type { PerformanceRow } from '$lib/components/MeiTable.svelte';

  type FileItem = { path: string; label: string; order?: number };

  let recordings: FileItem[] = [];
  let selectedRecording: string | null = null;

  let pieces: FileItem[] = [];
  let selectedPiece: string | null = null;

  let tableRows: PerformanceRow[] = [];
  let error = '';

  // Fetch recordings with enriched labels
  onMount(async () => {
    try {
      const res = await fetch('/db/performances');
      if (!res.ok) throw new Error('Could not fetch recordings');
      recordings = await res.json(); // now already {path, label}
    } catch (e: any) {
      error = e.message;
      console.error(e);
    }
  });

  async function handleRecordingSelect(path: string) {
    selectedRecording = path;
    pieces = [];
    selectedPiece = null;
    tableRows = [];

    try {
      const res = await fetch(`/db/performance-files?performance=${encodeURIComponent(path)}`);
      if (!res.ok) throw new Error('Could not fetch pieces for recording');
      pieces = await res.json(); // now already {path, label, order}
    } catch (e: any) {
      error = e.message;
      console.error(e);
    }
  }

  async function handlePieceSelect(path: string) {
    selectedPiece = path;
    tableRows = [];

    try {
      const res = await fetch(`/db/file?path=${encodeURIComponent(path)}`);
      if (!res.ok) throw new Error('Could not fetch MEI file');
      const data = await res.json();
      tableRows = parseMeiToRows(data.content);
    } catch (e: any) {
      error = e.message;
      console.error(e);
    }
  }

  // Temporary frontend MEI parser
  function parseMeiToRows(xml: string): PerformanceRow[] {
    const parser = new DOMParser();
    const doc = parser.parseFromString(xml, "application/xml");
    const rows: PerformanceRow[] = [];

    const measures = Array.from(doc.querySelectorAll("measure"));
    for (const measure of measures) {
      const measureNum = measure.getAttribute("n") || "?";
      const add = measure.querySelector("add");
      if (!add) continue;

      const tempos = add.querySelectorAll("tempo");
      const dyns = add.querySelectorAll("dynam");
      const timbres = add.querySelectorAll('annot[label="spectral centroid (Hz)"]');

      const maxBeats = Math.max(tempos.length, dyns.length, timbres.length);
      for (let i = 0; i < maxBeats; i++) {
        rows.push({
          measure: `${measureNum}.${i + 1}`,
          tempo: tempos[i]?.getAttribute("mm") ? parseFloat(tempos[i].getAttribute("mm")!) : null,
          dynamics: dyns[i]?.getAttribute("n") || null,
          timbre: timbres[i]?.getAttribute("n") ? parseFloat(timbres[i].getAttribute("n")!) : null
        });
      }
    }

    return rows;
  }
</script>

<div class="flex flex-col gap-6 p-4">
  {#if error}
    <p class="text-error">{error}</p>
  {/if}

  <PerformanceSelector
    {recordings}
    selectedRecording={selectedRecording}
    onSelect={handleRecordingSelect}
  />

  {#if selectedRecording && pieces.length > 0}
    <ScoreSelector
      files={pieces}
      selectedFile={selectedPiece}
      onFileSelect={handlePieceSelect}
    />
  {/if}

  <MeiTable rows={tableRows} />
</div>