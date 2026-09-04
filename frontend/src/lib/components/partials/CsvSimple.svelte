<script lang="ts">
    import type { PerformanceRow } from "$lib/types"; 
    let {table}: {table: PerformanceRow[]} = $props();
    
    
    function writeCsv(table: PerformanceRow[]){
        let csv = '"Measure","Tempo","Dynamics","Spectral centroid"\n';
        for (let i = 0; i < table.length; i++) {
            const measure = table[i].measure ?? "-";
            const tempo = table[i].tempo ?? "-";
            const dynamics = table[i].dynamics ?? "-";
            const timbre = table[i].timbre ?? "-";
            csv += `${measure},${tempo},${dynamics},${timbre}\n`
        }
        return csv;
    }
    
    function downloadCsv() {
        const csv = writeCsv(table);
        const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement("a");
        a.href = url;
        a.download = "table.csv";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        
        URL.revokeObjectURL(url);
    }
    
</script>

<button class="btn btn-active" onclick={downloadCsv}>Download as CSV</button>