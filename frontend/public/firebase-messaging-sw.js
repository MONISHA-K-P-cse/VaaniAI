importScripts('https://www.gstatic.com/firebasejs/10.7.1/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.7.1/firebase-messaging-compat.js');

// These should match your config in firebase.ts
const firebaseConfig = {
  apiKey: "AIzaSyDaOuGb7V6VKIUJUHHWTBlaPQiil54P4Q0",
  authDomain: "vaaniai-ba82a.firebaseapp.com",
  projectId: "vaaniai-ba82a",
  storageBucket: "vaaniai-ba82a.firebasestorage.app",
  messagingSenderId: "101371446408",
  appId: "1:101371446408:web:35d3c15ff9d5b6a79d0b3d",
  measurementId: "G-LKYS5LNFWH"
};

firebase.initializeApp(firebaseConfig);
const messaging = firebase.messaging();

messaging.onBackgroundMessage((payload) => {
  console.log('[firebase-messaging-sw.js] Received background message ', payload);
  const notificationTitle = payload.notification.title;
  const notificationOptions = {
    body: payload.notification.body,
    icon: '/vite.svg' // You can replace this with your app icon
  };

  self.registration.showNotification(notificationTitle, notificationOptions);
});
