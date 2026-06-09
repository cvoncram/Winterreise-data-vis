<script lang="ts">
	import type {SongInfo} from "$lib/types"
	
	let { files, selectedFile, onFileSelect}: 
		{files: SongInfo[]; selectedFile: SongInfo | null; onFileSelect: (file: SongInfo) => void} = $props();
	
	
	const winterreiseTitles = [
	"Gute Nacht",
	"Die Wetterfahne",
	"Gefror'ne Tränen",
	"Erstarrung",
	"Der Lindenbaum",
	"Wasserflut",
	"Auf dem Flusse",
	"Rückblick",
	"Irrlicht",
	"Rast",
	"Frühlingstraum",
	"Einsamkeit",
	"Die Post",
	"Der greise Kopf",
	"Die Krähe",
	"Letzte Hoffnung",
	"Im Dorfe",
	"Der stürmische Morgen",
	"Täuschung",
	"Der Wegweiser",
	"Das Wirtshaus",
	"Mut",
	"Die Nebensonnen",
	"Der Leiermann"
	];
	
	// Map backend files to song titles with track numbers
	const filesWithTitles = $derived(
		files.map((file, idx) => ({
			...file,
			label: `${idx + 1}. ${winterreiseTitles[idx] || file.label}`
		}))
	);
</script>

<div class="flex w-full mt-2 justify-start">
	<div class="flex gap-6 max-w-4xl w-full">
		<div class="bg-base-100 p-4 rounded-lg shadow flex flex-col items-start overflow-visible">
			<label class="label w-full flex flex-col items-center">
				<span class="label-text mb-2 text-lg font-semibold">Select piece</span>
				<select
				class="select select-bordered w-full"
				onchange={(e) => {
					const selected = filesWithTitles.find(f => f.path === e.currentTarget.value);
					if (selected) onFileSelect(selected);
				}}>
				<option value="" disabled selected={!selectedFile}>Select a piece...</option>
				{#each filesWithTitles as file}
					<option value={file.path} selected={selectedFile?.path === file.path}>{file.label}</option>
				{/each}
				</select>
			</label>
		</div>
	</div>
</div>