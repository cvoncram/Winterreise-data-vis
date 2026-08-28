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
    dynamics: { median: number | null; scale: number | null };
    timbre: { logMedian: number | null; scale: number | null };
    available?: boolean;
};

export type Parameter = keyof Pick<PerformanceRow, "tempo" | "dynamics" | "timbre">;

export type RecordingContext = "Recital" | "Studio" | "Radio Broadcast" | "TV Production";

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

export type PerformanceDetailed = {
    year: number;
    date: string;
    place: string;
    placeAddendum: string;
    coordinates: number[];
    pianist: string;
    recordingContext: RecordingContext;
    misc: string
}

// analysis
export type SingleParameterAnalysis = {
    performances: CyclePerformance[];
    parameter: Parameter;
};