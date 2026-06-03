from fastapi import APIRouter, Query
from github_auth import get_installation_token
from services.meiParser import parse_mei_to_rows, parse_mei_metadata
from services.dtwCalc import calculate_dtw_matrix
import requests
import base64
from config import OWNER, REPO, BRANCH

router = APIRouter()

@router.get("/db/analysis")
def calculate_dtw(
    parameter: str,
    piece: int,
    paths: list[str] = Query(...)
):
    token = get_installation_token()
    headers = {"Authorization": f"token {token}"}
    
    performances = []
    for path in paths:
        folder_name = path.split('/')[-1]
        file_path = f"{path}/{folder_name}_{piece}_Audio_Data.xml"
        url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{file_path}?ref={BRANCH}"
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        xml = base64.b64decode(r.json()["content"]).decode()
        performances.append({
            "data": parse_mei_to_rows(xml),
            "metadata": parse_mei_metadata(xml)
        })
    
    result = calculate_dtw_matrix(parameter, piece, performances)
    return result