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
    dynamics: { median: number | null; std: number | null };
    timbre: { logMedian: number | null; std: number | null };
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