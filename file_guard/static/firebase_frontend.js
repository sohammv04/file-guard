// firebase_frontend.js
// Embed via PyQtWebEngine or use firebase_rest_api.py from Python backend.

const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_PROJECT.firebaseapp.com",
  projectId: "YOUR_PROJECT_ID",
};

firebase.initializeApp(firebaseConfig);
const auth = firebase.auth();

function sendSMSOTP(mobileNumber) {
  const phoneNumber = mobileNumber.startsWith("+") ? mobileNumber : `+91${mobileNumber}`;
  const appVerifier = new firebase.auth.RecaptchaVerifier("recaptcha-container", { size: "invisible" });

  return firebase.auth().signInWithPhoneNumber(phoneNumber, appVerifier)
    .then((confirmationResult) => confirmationResult.verificationId)
    .catch((error) => {
      throw error;
    });
}

function verifySMSOTP(verificationId, otp) {
  const credential = firebase.auth.PhoneAuthProvider.credential(verificationId, otp);
  return firebase.auth().signInWithCredential(credential)
    .then(() => true)
    .catch(() => false);
}
