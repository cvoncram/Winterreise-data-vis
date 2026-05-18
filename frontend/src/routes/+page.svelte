<script lang="ts">
    import IntroGallery from "$lib/components/IntroGallery.svelte";
    import Footer from "$lib/components/Footer.svelte";
</script>

<div class="relative flex flex-col items-center px-[20%] overflow-hidden">
    <div 
        class="absolute inset-0 bg-cover bg-center opacity-50"
        style="background-image: url('/Winterreise_manuscript.jpg');">
    </div>    
    <div class="relative bg-base-100 p-10 rounded-md shadow-xl opacity-85">
        <h3 class="text-3xl mb-5">MEI Performance Visualization Tool</h3>
        <div class="text-xl">
            <p>This project is an interactive web application for visualizing and comparing
                performance data from multiple MEI files of the same musical work.</p>
            <p>It renders a MEI score with Verovio and visualizes performance data
                (tempo, dynamics, timbre) extracted dynamically from a GitHub
                repository containing performance MEI files.</p>
            <p>The system is designed for musicological / digital humanities analysis of
                performance differences across many recordings of the same piece.</p><br>
        </div>
        <div class="mb-4 mt-4 flex w-full justify-center">
            <IntroGallery />
        </div>
        <div class="text-xl">
            <h4 class="text-2xl mb-2">About and Credits</h4>
            <p>Frontend framework: SvelteKit<br>UI components and animations: TailwindCSS, DaisyUI, and GSAP<br>
                Visualizations: D3.JS<br>Backend framework: FastAPI<br>MEI engraving engine: Verovio</p><br>
            <h4 class="text-2xl mb-2">About this application</h4>
            <p>This application was created by Clemens von Cramon as part of the M.A. thesis in <i>Digital 
                Humanities</i> at <i>Johannes Gutenberg University</i> in Mainz.</p><br>
            <p>Note on the use of Generative AI:<br> Generative AI was used to help create 
                some of the frontend components and parts of the backend routes.
                Additionally, it was used to translate parts of the application logic from 
                pseudocode to machine-readable python code.</p><br>
        </div>
        <Footer />


    </div>
</div>

