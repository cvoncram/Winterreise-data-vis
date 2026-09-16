// primitives
export type SongInfo = {
    path: string;
    label: string;
    nbInOrder: number;
};

export type PerformanceRow = {
    measure: string;
    tempo: number | null;
    dynamics: number | null;
    timbre: number | null;
};

export type PerformanceMetadata = {
    sampleRate: number;
    mfValue: number;
    dynamicStep: number;
};

export type NormalizationReference = {
    dynamics: { center: number | null; scale: number | null };
    timbre: { logCenter: number | null; scale: number | null };
    available?: boolean;
    method?: "mean" | "median";
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
    /** From performances.json, matched to the folder by the backend. */
    year?: number | null;
    pianist?: string | null;
    city?: string | null;
    recordingContext?: string | null;
}

export type PerformanceDetailed = {
    year: number;
    date: string;
    place: string;
    placeAddendum: string;
    coordinates: number[];
    pianist: string;
    recordingContext: RecordingContext;
    onlineInfo: string;
    gndNo: number;
    misc: string
}

// analysis
export type SingleParameterAnalysis = {
    performances: CyclePerformance[];
    parameter: Parameter;
};