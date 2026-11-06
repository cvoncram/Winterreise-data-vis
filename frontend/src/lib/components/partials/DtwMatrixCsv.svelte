<script lang="ts">
    /** Exports the distance matrix as a full n × n CSV table; refused pairs stay empty. */
    import CsvTable from "./CsvTable.svelte";

    let { matrix, labels, filename = "dtw-matrix", label = "Download as CSV" }: {
        matrix: (number | null)[][];
        labels: string[];
        filename?: string;
        label?: string;
    } = $props();

    const headers = $derived(["", ...labels]);
    const rows = $derived(matrix.map((row, i) => [labels[i] ?? String(i), ...row]));
</script>

<CsvTable {headers} {rows} {filename} {label} />
