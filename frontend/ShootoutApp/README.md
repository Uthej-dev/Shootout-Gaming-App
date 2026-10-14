# ShootOut app (Expo)

These are the source folders only. Create the Expo project with current dependency versions, then drop them in:

```
npx create-expo-app@latest ShootoutApp --template blank
cd ShootoutApp
npx expo install axios expo-secure-store expo-status-bar @expo/vector-icons \
  react-native-screens react-native-safe-area-context \
  @react-navigation/native @react-navigation/native-stack @react-navigation/bottom-tabs
```
Copy `App.js`, `components/ screens/ navigation/ services/ context/ utils/ constants/ hooks/` and `.env.example` over the generated files (replace the generated App.js).
Then `cp .env.example .env`, set EXPO_PUBLIC_API_BASE_URL to `http://<your-computer-LAN-IP>:8000` and run `npx expo start`. Open it with Expo Go on your phone (same Wi-Fi as the backend).
