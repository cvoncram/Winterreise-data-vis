// primitives
export type SongInfo = {
    path: string;
    label: string;
    nbInOrder: number;
};

export type PerformanceRow = {
    measure: string;
    tempo: number;
    dynamics: string;
    timbre: number;
};

export type PerformanceMetadata = {
    sampleRate: number;
    mfValue: number;
    dynamicStep: number;
};

export type NormalizationReference = {
    /**
     * `scale` is a scaled median absolute deviation, pooled across all
     * recordings at the level the request asked for — within the piece when a
     * single piece is shown, across the cycle otherwise.
     */
    dynamics: { median: number | null; scale: number | null };
    timbre: { logMedian: number | null; scale: number | null };
    /**
     * False when a figure could not be resolved — the visualization then
     * falls back to neutral values rather than showing normalized ones.
     * Not surfaced in the UI yet.
     */
    available?: boolean;
};

export type Parameter = 
    keyof Pick<PerformanceRow, "tempo" | "dynamics" | "timbre">;

// entities
export type Score = {
    song: SongInfo;
    meiData: string;
};

export type SongPerformance = {
    song: SongInfo | null;
    rows: PerformanceRow[];
};

export type CyclePerformance = {
    songPerformances: SongPerformance[];
    metadata: PerformanceMetadata;
    normalizationReference?: NormalizationReference;
    path: string;
    label: string;
}

// analysis
export type SingleParameterAnalysis = {
    performances: CyclePerformance[];
    parameter: Parameter;
};