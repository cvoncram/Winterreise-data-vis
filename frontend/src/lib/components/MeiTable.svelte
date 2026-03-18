<script lang="ts" context="module">
  export type PerformanceRow = {
    measure: string;
    tempo: number | null;
    dynamics: string | null;
    timbre: number | null;
  };
</script>

<script lang="ts">
  export let rows: PerformanceRow[] = [];
</script>

{#if rows.length > 0}
<div class="overflow-auto mt-4">
  <table class="table table-zebra w-full">
    <thead>
      <tr>
        <th>Measure</th>
        <th>Tempo</th>
        <th>Dynamics</th>
        <th>Spectral Centroid</th>
      </tr>
    </thead>
    <tbody>
      {#each rows as row}
        <tr>
          <td>{row.measure}</td>
          <td>{row.tempo ?? "-"}</td>
          <td>{row.dynamics ?? "-"}</td>
          <td>{row.timbre ?? "-"}</td>
        </tr>
      {/each}
    </tbody>
  </table>
</div>
{/if}