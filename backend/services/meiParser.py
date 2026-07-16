from typing import List, Optional, Dict
import xml.etree.ElementTree as ET
from config import MEI_NS
from fastapi import Response


def parse_rows(
    xml: str,
    start: Optional[int] = None,
    start_beat: Optional[int] = None,
    end: Optional[int] = None,
    end_beat: Optional[int] = None,
) -> List[Dict[str, Optional[float]]]:
    """
    Parse MEI performance data into per-beat rows. If start/end are given,
    restrict to that measure/beat range (start_beat/end_beat bound the first
    and last measure of the range).
    """
    rows = []
    root = ET.fromstring(xml)

    # Measures
    measures = root.findall(".//mei:measure", MEI_NS)
    if start is not None:
        measures = [m for m in measures if start <= int(m.get("n")) <= end]

    for measure in measures:
        measure_num = measure.attrib.get("n", "?")

        add = measure.find(".//mei:add", MEI_NS)
        if add is None:
            continue

        tempos = add.findall(".//mei:tempo", MEI_NS)
        dyns = add.findall(".//mei:dynam", MEI_NS)
        timbres = add.findall('.//mei:annot[@label="spectral centroid (Hz)"]', MEI_NS)

        max_beats = max(len(tempos), len(dyns), len(timbres))

        for i in range(max_beats):
            beat_num = i + 1  # sequential numbering within the measure

            if start is not None:
                measure_num_int = int(measure_num)
                # Skip beats before the start boundary
                if measure_num_int == start and beat_num < start_beat:
                    continue
                # Skip beats after the end boundary
                if measure_num_int == end and beat_num > end_beat:
                    continue

            tempo_val = None
            if i < len(tempos):
                mm = tempos[i].attrib.get("mm")
                if mm is not None:
                    try:
                        tempo_val = float(mm)
                    except ValueError:
                        pass

            dyn_val = None
            intpr_dyn = None
            if i < len(dyns):
                dyn_val = dyns[i].attrib.get("n")
                intpr_dyn = dyns[i].attrib.get("label")

            timbre_val = None
            if i < len(timbres):
                n = timbres[i].attrib.get("n")
                if n is not None:
                    try:
                        timbre_val = float(n)
                    except ValueError:
                        pass

            rows.append({
                "measure": f"{measure_num}.{beat_num}",
                "tempo": tempo_val,
                "dynamics": dyn_val,
                "interpreted dynamics": intpr_dyn,
                "timbre": timbre_val
            })

    return rows



def parse_mei_metadata(xml: str) -> dict[str, float | int]:
    root = ET.fromstring(xml)

    metadata_element = root.find(
        './/mei:application[@xml:id="sv_to_mei"]',
        MEI_NS
    )

    sampleRateElement = metadata_element.find(
        './/mei:annot[@type="sampleRate"]',
        MEI_NS
    )
    sampleRate = float(sampleRateElement.get("value"))

    mfDBCalibrationElement = metadata_element.find(
        './/mei:annot[@type="mf_dB_calibration"]',
        MEI_NS
    )
    mfDBCalibration = float(mfDBCalibrationElement.get("value"))

    dynamicStepElement = metadata_element.find(
        './/mei:annot[@type="dB_per_dynamic_level"]',
        MEI_NS
    )
    dynamicStep = float(dynamicStepElement.get("value"))

    return {
        "sampleRate": sampleRate,
        "mfValue": mfDBCalibration,
        "dynamicStep": dynamicStep
    }

def return_relevant_measures(xml: str, start: int, end: int):
    root = ET.fromstring(xml)

    # Remove every measure outside the requested range
    for section in root.findall(".//mei:section", MEI_NS):
        for measure in list(section.findall("mei:measure", MEI_NS)):
            n = measure.get("n")
            if not n:
                continue

            try:
                numbers = [int(x.strip()) for x in n.split(",")]
            except ValueError:
                continue

            if not any(start <= num <= end for num in numbers):
                section.remove(measure)

    ET.register_namespace("", MEI_NS["mei"])
    return ET.tostring(root, encoding="unicode")