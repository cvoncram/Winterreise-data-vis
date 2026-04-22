from typing import List, Optional, Dict
import xml.etree.ElementTree as ET


MEI_NS = {"mei": "http://www.music-encoding.org/ns/mei"}


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