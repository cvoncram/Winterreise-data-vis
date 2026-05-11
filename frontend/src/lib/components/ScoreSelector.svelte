<script lang="ts">
	type FileItem = {
		path: string;
		label: string;
		order?: number;
	};
	
	let { files, selectedFile, onFileSelect}: {files: FileItem[]; selectedFile: string | null; onFileSelect: (file: string) => void} = $props();
	
	
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
	
	// Auto-select first file when files arrive
	$effect(()=> {
		if (files.length > 0 && !selectedFile) {
			selectedFile = files[0].path;
			onFileSelect(selectedFile);
		}
	});
	
	// Map backend files to song titles with track numbers
	const filesWithTitles = $derived(
	files.map((file, idx) => ({
		...file,
		label: `${idx + 1}. ${winterreiseTitles[idx] || file.label}`
	}))
	);
</script>

<div class="flex w-full mt-4 justify-start">
	<div class="flex gap-6 max-w-4xl w-full">
		<div class="bg-base-100 p-4 rounded-lg shadow flex flex-col items-start overflow-visible">
			<label class="label w-full flex flex-col items-center">
				<span class="label-text mb-2 text-lg font-semibold">Select piece</span>
				<select
				class="select select-bordered w-full"
				bind:value={selectedFile}
				onchange={(e) => onFileSelect(e.currentTarget.value)}
				disabled={filesWithTitles.length === 0}
				>
				{#each filesWithTitles as file}
				<option value={file.path}>{file.label}</option>
				{/each}
			</select>
		</label>
	</div>
</div>
</div>