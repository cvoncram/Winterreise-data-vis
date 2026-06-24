from typing import List, Optional, Dict, Tuple
import xml.etree.ElementTree as ET


MEI_NS = {"mei": "http://www.music-encoding.org/ns/mei",
          "xml": "http://www.w3.org/XML/1998/namespace"
          }


def parse_mei_to_rows(xml: str) -> List[Dict[str, Optional[float]]]:
    rows = []

    root = ET.fromstring(xml)

    # Measures
    measures = root.findall(".//mei:measure", MEI_NS)

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
            tempo_val = None
            if i < len(tempos):
                mm = tempos[i].attrib.get("mm")
                if mm is not None:
                    try:
                        tempo_val = float(mm)
                    except ValueError:
                        pass

            dyn_val = None
            if i < len(dyns):
                dyn_val = dyns[i].attrib.get("n")

            timbre_val = None
            if i < len(timbres):
                n = timbres[i].attrib.get("n")
                if n is not None:
                    try:
                        timbre_val = float(n)
                    except ValueError:
                        pass

            rows.append({
                "measure": f"{measure_num}.{i + 1}",
                "tempo": tempo_val,
                "dynamics": dyn_val,
                "timbre": timbre_val
            })

    return rows

def parse_measures_to_rows(
    xml: str, start: int, start_beat: int, end: int, end_beat: int
) -> List[Dict[str, Optional[float]]]:
    rows = []
    root = ET.fromstring(xml)

    # Measures
    measures = root.findall(".//mei:measure", MEI_NS)
    measures = [m for m in measures if start <= int(m.get("n")) <= end]

    for measure in measures:
        measure_num = int(measure.attrib.get("n", "0"))
        add = measure.find(".//mei:add", MEI_NS)
        if add is None:
            continue

        tempos = add.findall(".//mei:tempo", MEI_NS)
        dyns = add.findall(".//mei:dynam", MEI_NS)
        timbres = add.findall('.//mei:annot[@label="spectral centroid (Hz)"]', MEI_NS)

        max_beats = max(len(tempos), len(dyns), len(timbres))

        for i in range(max_beats):
            beat_num = i + 1  # sequential numbering within the measure

            # Skip beats before the start boundary
            if measure_num == start and beat_num < start_beat:
                continue
            # Skip beats after the end boundary
            if measure_num == end and beat_num > end_beat:
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
            if i < len(dyns):
                dyn_val = dyns[i].attrib.get("n")

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