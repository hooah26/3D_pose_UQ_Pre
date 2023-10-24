from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
import extract_keypoints

app = FastAPI()

class KeypointsResult(BaseModel):
    keypoints_data: str

@app.post("/evaluate_keypoints", response_model=KeypointsResult)
async def evaluate_keypoints(video: UploadFile = File(...)):
    video_path = f"temp/{video.filename}"
    output_path = "keypoints_data.json"

    with open(video_path, "wb") as buffer:
        buffer.write(await video.read())

    extract_keypoints.extract_keypoints_from_video(video_path, output_path)

    with open(output_path, "r") as infile:
        keypoints_data = infile.read()

    return {"keypoints_data": keypoints_data}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)