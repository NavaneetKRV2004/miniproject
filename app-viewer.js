
const firebaseConfig = {
  apiKey: "AIzaSyChF68eEb_-Py1SAgS_t6EILVL-c6ahwEc",
  authDomain: "video-feed-ee737.firebaseapp.com",
  databaseURL: "https://video-feed-ee737-default-rtdb.asia-southeast1.firebasedatabase.app",
  projectId: "video-feed-ee737",
  storageBucket: "video-feed-ee737.firebasestorage.app",
  messagingSenderId: "873788394054",
  appId: "1:873788394054:web:eed5e17f965ec18c1c5847",
  measurementId: "G-8EDXZV9GNS"
};

firebase.initializeApp(firebaseConfig);
const db = firebase.database();
const roomRef = db.ref("streamRoom");

let pc;
let remoteStream;



roomRef.child("answer").remove();
roomRef.child("calleeIce").remove();
  
  
function showLog(msg, isError = false) {
  const logBox = document.getElementById("logBox");
  const p = document.createElement("p");
  p.textContent = msg;
  p.style.color = isError ? "red" : "green";
  logBox.appendChild(p);
  console.log(msg);
}

function connectToStream() {
  showLog("[Viewer] Button clicked. Starting connection...");

  pc = new RTCPeerConnection({
    iceServers: [{ urls: "stun:stun.l.google.com:19302" }]
  });
  showLog("[Viewer] Peer connection created.");

  remoteStream = new MediaStream();
  const videoElem = document.getElementById("remoteVideo");
  if (!videoElem) {
    showLog("[Viewer] ERROR: No <video id='remoteVideo'> found in HTML!", true);
    return;
  }
  videoElem.srcObject = remoteStream;
  showLog("[Viewer] Remote video element hooked up.");

  pc.ontrack = event => {
    showLog("[Viewer] Remote track received.");
    event.streams[0].getTracks().forEach(track => {
      showLog(`[Viewer] Adding track: ${track.kind}`);
      remoteStream.addTrack(track);
    });
  };

  pc.onicecandidate = event => {
    if (event.candidate) {
      showLog("[Viewer] Sending ICE candidate to Firebase.");
      roomRef.child("calleeIce").push(JSON.stringify(event.candidate));
    }
  };

  showLog("[Viewer] Waiting for offer from streamer...");
  roomRef.child("offer").once("value").then(async snapshot => {
    const data = snapshot.val();
    if (!data) {
      showLog("[Viewer] No offer found — streamer may not be online.", true);
      alert("Streamer is not online yet.");
      return;
    }

    showLog("[Viewer] Offer received from Firebase.");
    const offer = JSON.parse(data);
    await pc.setRemoteDescription(new RTCSessionDescription(offer));
    showLog("[Viewer] Remote description set.");

    const answer = await pc.createAnswer();
    await pc.setLocalDescription(answer);
    showLog("[Viewer] Created and set local answer.");
    await roomRef.child("answer").set(JSON.stringify(answer));
    showLog("[Viewer] Sent answer to Firebase.");

    roomRef.child("callerIce").on("child_added", snapshot => {
      const candidate = JSON.parse(snapshot.val());
      showLog("[Viewer] ICE candidate received from streamer.");
      pc.addIceCandidate(new RTCIceCandidate(candidate));
    });
  }).catch(err => {
    showLog("[Viewer] Error fetching offer: " + err.message, true);
  });
}

window.connectToStream = connectToStream;
