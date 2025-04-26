// src/firebase.js
import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider, GithubAuthProvider, signInWithPopup } from "firebase/auth";

// Import the functions you need from the SDKs you need
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// Import the functions you need from the SDKs you need
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyDNPcHR8mu6iw8IW3c8Fk0B-SlnKN4KIs4",
  authDomain: "analyticrew-b8350.firebaseapp.com",
  projectId: "analyticrew-b8350",
  storageBucket: "analyticrew-b8350.firebasestorage.app",
  messagingSenderId: "303103197310",
  appId: "1:303103197310:web:9ecfa0db8171908f2ad82f"
};


// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

const googleProvider = new GoogleAuthProvider();
const githubProvider = new GithubAuthProvider();

const signInWithGoogle = () => signInWithPopup(auth, googleProvider);
const signInWithGithub = () => signInWithPopup(auth, githubProvider);
export { auth, signInWithGoogle, signInWithGithub };