<script lang="ts">
    type tableRow = {
        measure: string,
        values: number[];
    }
    let {rows, labels}: {rows: tableRow[], labels: string[]} = $props();
    
    
    function writeCsv(rows: tableRow[], labels: string[]){
        let csv = '"Measure"';
        for (let i = 0; i < labels.length; i++) {
            csv += `,"${labels[i]}"`
        }
        csv += '\n';

        for (let i = 0; i < rows.length; i++) {
            const rowsValues = () => {
                let str = '';
                for (let j = 0; j < rows[i].values.length; j++) {
                    str += `,${rows[i].values[j]}`                
                }
                return str;
            };
            csv += `"${rows[i].measure}"${rowsValues()}\n`
        }
        return csv;
    }
    
    function downloadCsv() {
        const csv = writeCsv(rows, labels);
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