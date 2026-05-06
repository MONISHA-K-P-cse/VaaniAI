import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";
import { getMessaging } from "firebase/messaging";

// Replace these placeholders with your actual Firebase config from the Firebase Console
const firebaseConfig = {
  apiKey: "AIzaSyDaOuGb7V6VKIUJUHHWTBlaPQiil54P4Q0",
  authDomain: "vaaniai-ba82a.firebaseapp.com",
  projectId: "vaaniai-ba82a",
  storageBucket: "vaaniai-ba82a.firebasestorage.app",
  messagingSenderId: "101371446408",
  appId: "1:101371446408:web:35d3c15ff9d5b6a79d0b3d",
  measurementId: "G-LKYS5LNFWH"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getFirestore(app);

// Messaging might fail in environments without browser support (like SSR or some CI)
export let messaging: any = null;
try {
    messaging = getMessaging(app);
} catch (e) {
    console.warn("Firebase Messaging could not be initialized:", e);
}

export default app;
