<script lang="ts">
    /**
     * Exports the distance matrix as a conventional n x n table.
     *
     * The triangle on screen shows each pair once, which is all a reader
     * needs; a file is read by other programs, and those expect the full
     * square with its header row and column. Pairs the backend refused to
     * compare stay empty rather than becoming a zero, which would read as
     * "identical" — CsvTable does that for every table alike.
     */
    import CsvTable from "./CsvTable.svelte";

    let { matrix, labels, filename = "dtw-matrix" }: {
        matrix: (number | null)[][];
        labels: string[];
        filename?: string;
    } = $props();

    const headers = $derived(["", ...labels]);
    const rows = $derived(matrix.map((row, i) => [labels[i] ?? String(i), ...row]));
</script>

<CsvTable {headers} {rows} {filename} />
