<script lang="ts">
    /**
     * Exports the distance matrix as a conventional n x n table.
     *
     * The triangle on screen shows each pair once, which is all a reader
     * needs; a file is read by other programs, and those expect the full
     * square with its header row and column. Pairs the backend refused to
     * compare stay empty rather than becoming a zero, which would read as
     * "identical".
     */
    let { matrix, labels, filename = "dtw-matrix" }: {
        matrix: (number | null)[][];
        labels: string[];
        filename?: string;
    } = $props();

    function quote(value: string) {
        return `"${value.replace(/"/g, '""')}"`;
    }

    function writeCsv(matrix: (number | null)[][], labels: string[]) {
        let csv = '""';
        for (const label of labels) csv += `,${quote(label)}`;
        csv += "\n";

        for (let i = 0; i < matrix.length; i++) {
            csv += quote(labels[i] ?? String(i));
            for (let j = 0; j < matrix.length; j++) {
                const value = matrix[i]?.[j];
                csv += `,${value == null ? "" : value}`;
            }
            csv += "\n";
        }
        return csv;
    }

    function downloadCsv() {
        const csv = writeCsv(matrix, labels);
        const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
        const url = URL.createObjectURL(blob);

        const a = document.createElement("a");
        a.href = url;
        a.download = filename.endsWith(".csv") ? filename : `${filename}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);

        URL.revokeObjectURL(url);
    }
</script>

<button class="btn btn-active" onclick={downloadCsv} disabled={matrix.length === 0}>
    Download as CSV
</button>
