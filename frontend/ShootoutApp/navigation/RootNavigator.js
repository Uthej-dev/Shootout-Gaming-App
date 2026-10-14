import React from 'react';
import { ActivityIndicator, View } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../context/AuthContext';
import { colors } from '../constants/theme';
import LoginScreen from '../screens/LoginScreen';
import RegisterScreen from '../screens/RegisterScreen';
import ForgotPasswordScreen from '../screens/ForgotPasswordScreen';
import HomeScreen from '../screens/HomeScreen';
import BgmiScreen from '../screens/BgmiScreen';
import BgmiTdmScreen from '../screens/BgmiTdmScreen';
import FreeFireScreen from '../screens/FreeFireScreen';
import MatchesScreen from '../screens/MatchesScreen';
import RoomScreen from '../screens/RoomScreen';
import EarnScreen from '../screens/EarnScreen';
import YouTubeScreen from '../screens/YouTubeScreen';
import ProfileScreen from '../screens/ProfileScreen';

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

const ICONS = { Earn: 'gift', YouTube: 'logo-youtube', Controller: 'game-controller', Matches: 'trophy', Profile: 'person' };

function Tabs() {
  return (
    <Tab.Navigator
      initialRouteName="Controller"
      screenOptions={({ route }) => ({
        headerShown: false,
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.muted,
        tabBarIcon: ({ color, focused }) => (
          <Ionicons name={focused ? ICONS[route.name] : `${ICONS[route.name]}-outline`} size={route.name === 'Controller' ? 30 : 24} color={color} />
        ),
      })}
    >
      <Tab.Screen name="Earn" component={EarnScreen} />
      <Tab.Screen name="YouTube" component={YouTubeScreen} />
      {/* Controller shows Home content for now. Behaviour may change later. */}
      <Tab.Screen name="Controller" component={HomeScreen} options={{ tabBarLabel: 'Home' }} />
      <Tab.Screen name="Matches" component={MatchesScreen} />
      <Tab.Screen name="Profile" component={ProfileScreen} />
    </Tab.Navigator>
  );
}

export default function RootNavigator() {
  const { token, loading } = useAuth();
  if (loading) return <View style={{ flex: 1, justifyContent: 'center' }}><ActivityIndicator size="large" color={colors.primary} /></View>;
  return (
    <NavigationContainer>
      {token ? (
        <Stack.Navigator>
          <Stack.Screen name="Tabs" component={Tabs} options={{ headerShown: false }} />
          <Stack.Screen name="Bgmi" component={BgmiScreen} options={{ title: 'BGMI' }} />
          <Stack.Screen name="BgmiTdm" component={BgmiTdmScreen} options={{ title: 'BGMI TDM' }} />
          <Stack.Screen name="FreeFire" component={FreeFireScreen} options={{ title: 'Free Fire' }} />
          <Stack.Screen name="Room" component={RoomScreen} options={({ route }) => ({ title: route.params?.title || 'Room' })} />
        </Stack.Navigator>
      ) : (
        <Stack.Navigator screenOptions={{ headerShown: false }}>
          <Stack.Screen name="Login" component={LoginScreen} />
          <Stack.Screen name="Register" component={RegisterScreen} />
          <Stack.Screen name="ForgotPassword" component={ForgotPasswordScreen} />
        </Stack.Navigator>
      )}
    </NavigationContainer>
  );
}
