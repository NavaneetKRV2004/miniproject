
import cv2
import firebase_admin
from firebase_admin import credentials, db
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
import asyncio
import json
import numpy as np
from av import VideoFrame

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://video-feed-ee737-default-rtdb.asia-southeast1.firebasedatabase.app'
})

room_ref = db.reference("streamRoom")

class CameraStreamTrack(VideoStreamTrack):
    def __init__(self):
        super().__init__()
        self.cap = cv2.VideoCapture(0)

    async def recv(self):
        pts, time_base = await self.next_timestamp()
        ret, frame = self.cap.read()
        if not ret:
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
        new_frame = VideoFrame.from_ndarray(frame, format="bgr24")
        new_frame.pts = pts
        new_frame.time_base = time_base
        return new_frame

async def run():
    pc = RTCPeerConnection()
    track = CameraStreamTrack()
    pc.addTrack(track)

    @pc.on("icecandidate")
    def on_icecandidate(event):
        if event.candidate:
            room_ref.child("callerIce").push(json.dumps(event.candidate.to_sdp()))

    offer = await pc.createOffer()
    await pc.setLocalDescription(offer)
    room_ref.child("offer").set(json.dumps({
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type
    }))
    print("Offer sent, waiting for viewer...")

    while True:
        answer = room_ref.child("answer").get()
        if answer:
            break
        await asyncio.sleep(1)

    answer = json.loads(answer)
    await pc.setRemoteDescription(RTCSessionDescription(
        sdp=answer["sdp"], type=answer["type"]))
    print("Viewer connected")

    def on_callee_ice(snapshot,_):
        val = snapshot.val()
        if val:
            candidate = json.loads(val)
            pc.addIceCandidate(candidate)
    

    room_ref.child("calleeIce").listen(on_callee_ice)

    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(run())
