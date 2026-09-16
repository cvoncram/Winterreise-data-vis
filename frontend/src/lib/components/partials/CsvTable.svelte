<script lang="ts">
    /**
     * Downloads any table as CSV: one header row, then rows of plain values.
     *
     * Kept generic because the alternative is a near-identical component per
     * table. Text is quoted, numbers are written as they are, and a missing
     * value stays empty rather than becoming a zero, which would read as a
     * measurement.
     */
    let { headers, rows, filename = "table", label = "Download as CSV" }: {
        headers: string[];
        rows: (string | number | null | undefined)[][];
        filename?: string;
        label?: string;
    } = $props();

    function cell(value: string | number | null | undefined) {
        if (value == null) return "";
        return typeof value === "number" ? String(value) : `"${value.replace(/"/g, '""')}"`;
    }

    function writeCsv() {
        return [headers, ...rows].map(row => row.map(cell).join(",")).join("\n") + "\n";
    }

    function downloadCsv() {
        const blob = new Blob([writeCsv()], { type: "text/csv;charset=utf-8;" });
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

<button class="btn btn-active btn-sm" onclick={downloadCsv} disabled={rows.length === 0}>{label}</button>
