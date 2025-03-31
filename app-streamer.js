

const firebaseConfig = {
	apiKey: "AIzaSyChF68eEb_-Py1SAgS_t6EILVL-c6ahwEc",
	authDomain: "video-feed-ee737.firebaseapp.com",
	databaseURL: "https://video-feed-ee737-default-rtdb.asia-southeast1.firebasedatabase.app",
	projectId: "video-feed-ee737",
	storageBucket: "video-feed-ee737.appspot.com",
	messagingSenderId: "873788394054",
	appId: "1:873788394054:web:eed5e17f965ec18c1c5847",
	measurementId: "G-8EDXZV9GNS"
  };
  
  firebase.initializeApp(firebaseConfig);
  const db = firebase.database();
  const roomRef = db.ref("streamRoom");
  
  let pc;
  let localStream;
  
  function showLog(msg, isError = false) {
	const logBox = document.getElementById("logBox");
	const p = document.createElement("p");
	p.textContent = msg;
	p.style.color = isError ? "red" : "black";
	logBox.appendChild(p);
	console.log(msg);
  }
  
  navigator.mediaDevices.getUserMedia({ video: true, audio: true }).then(stream => {
	localStream = stream;
	document.getElementById('localVideo').srcObject = stream;
	showLog("[Streamer] Local stream started.");
  
	createPeerConnection();
	sendOffer();
	listenForAnswer();
  });
  
  function createPeerConnection() {
	pc = new RTCPeerConnection({ iceServers: [{ urls: "stun:stun.l.google.com:19302" }] });
  
	localStream.getTracks().forEach(track => pc.addTrack(track, localStream));
  
	pc.onicecandidate = event => {
	  if (event.candidate) {
		roomRef.child("callerIce").push(JSON.stringify(event.candidate));
		showLog("[Streamer] Sent ICE candidate.");
	  }
	};
  
	roomRef.child("calleeIce").off(); // Ensure old listeners are removed
	roomRef.child("calleeIce").on("child_added", snapshot => {
	  const data = JSON.parse(snapshot.val());
	  pc.addIceCandidate(new RTCIceCandidate(data));
	  showLog("[Streamer] Received ICE from viewer.");
	});
  }
  
  function listenForAnswer() {
	roomRef.child("answer").on("value", async snapshot => {
	  const data = snapshot.val();
  
	  if (data && !pc.currentRemoteDescription) {
		const answer = new RTCSessionDescription(JSON.parse(data));
		await pc.setRemoteDescription(answer);
		showLog("[Streamer] ✅ Received and set remote answer.");
	  }
  
	  if (!data && pc?.connectionState !== "new") {
		showLog("[Streamer] ⚠️ Viewer disconnected. Resetting connection...");
		resetConnection();
	  }
	});
  }
  
  async function sendOffer() {
	await roomRef.remove()
	  .then(() => showLog("✅ Stream room data cleared."))
	  .catch(error => showLog("❌ Error clearing data: " + error.message, true));
  
	const offer = await pc.createOffer();
	await pc.setLocalDescription(offer);
	await roomRef.child("offer").set(JSON.stringify(offer));
	showLog("[Streamer] Sent offer to Firebase.");
  }
  
  function resetConnection() {
	if (pc) pc.close();
	createPeerConnection();
	sendOffer();
  }
  