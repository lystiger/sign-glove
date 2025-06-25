from fastapi import APIRouter, UploadFile, File
from processors.data_processor import read_data, write_data, initialize_csv
from core.config import RAW_DATA, CLEAN_DATA, DEFAULT_NOISE_CONFIG

router = APIRouter()

@router.post("/upload")
async def upload_data(file: UploadFile = File(...)):
    raw_path = "backend/data/raw_data.csv"
    clean_path = "backend/data/clean_data.csv"

    contents = await file.read()
    with open(raw_path, 'wb') as f:
        f.write(contents)

    initialize_csv(clean_path)
    new_data, header = read_data(raw_path, use_noise_reduction=True)
    write_data(clean_path, new_data, header)

    return {"message": "Data uploaded and processed", "rows": len(new_data)}
