import asyncio
import json
import firebase_admin
from firebase_admin import credentials, db
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
import cv2
import av
import time

# Initialize Firebase
cred = credentials.Certificate("serviceAccountKey.json")  # Your service account key
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
            await asyncio.sleep(0.1)
            return await self.recv()

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        video_frame = av.VideoFrame.from_ndarray(frame, format="rgb24")
        video_frame.pts = pts
        video_frame.time_base = time_base
        return video_frame

async def run():
    print("Streamer is waiting for viewer...")
    while True:
        offer_json = room_ref.child("offer").get()
        answer_json = room_ref.child("answer").get()

        if offer_json and not answer_json:
            print("Viewer offer detected. Creating peer connection...")
            pc = RTCPeerConnection()
            video_track = CameraStreamTrack()
            pc.addTrack(video_track)

            @pc.on("icecandidate")
            def on_icecandidate(event):
                if event.candidate:
                    room_ref.child("callerIce").push(json.dumps(event.candidate.to_dict()))

            @pc.on("connectionstatechange")
            async def on_connectionstatechange():
                print("Connection state:", pc.connectionState)
                if pc.connectionState in ["failed", "disconnected", "closed"]:
                    print("Viewer disconnected. Resetting...")
                    await pc.close()
                    room_ref.child("offer").set(None)
                    room_ref.child("answer").set(None)
                    room_ref.child("callerIce").set(None)
                    room_ref.child("calleeIce").set(None)

            # Set remote description
            offer = RTCSessionDescription(sdp=json.loads(offer_json)["sdp"], type="offer")
            await pc.setRemoteDescription(offer)

            # Create answer
            answer = await pc.createAnswer()
            await pc.setLocalDescription(answer)
            room_ref.child("answer").set(json.dumps({
                "type": pc.localDescription.type,
                "sdp": pc.localDescription.sdp
            }))

            # Handle ICE from viewer
            def handle_callee_ice(snapshot):
                for snap in snapshot.each():
                    data = json.loads(snap.val())
                    pc.addIceCandidate(data)
            room_ref.child("calleeIce").listen(handle_callee_ice)

            print("Streaming to viewer...")
            while True:
                if pc.connectionState in ["disconnected", "failed", "closed"]:
                    break
                await asyncio.sleep(1)
        else:
            await asyncio.sleep(1)

asyncio.run(run())
