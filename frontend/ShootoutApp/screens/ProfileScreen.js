import React, { useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import useFocusFetch from '../hooks/useFocusFetch';
import * as userService from '../services/userService';
import { useAuth } from '../context/AuthContext';
import { colors, radius } from '../constants/theme';
import Button from '../components/Button';

export default function ProfileScreen() {
  const { logout, user } = useAuth();
  const [me, setMe] = useState(user);
  useFocusFetch(async () => { setMe(await userService.me()); return []; }, []);
  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: '#fff' }} edges={['top']}>
      <View style={{ padding: 24 }}>
        <View style={s.avatar}><Text style={s.initial}>{me?.username?.[0]?.toUpperCase()}</Text></View>
        <Text style={s.name}>{me?.username}</Text>
        <Text style={s.mobile}>{me?.mobileNumber}</Text>
        <View style={s.wallet}><Text style={s.wl}>Wallet balance</Text><Text style={s.wv}>₹{me?.walletBalance ?? 0}</Text></View>
        <Button title="Logout" variant="outline" onPress={logout} style={{ marginTop: 24 }} />
      </View>
    </SafeAreaView>
  );
}
const s = StyleSheet.create({
  avatar: { width: 84, height: 84, borderRadius: 42, backgroundColor: colors.primary, alignItems: 'center', justifyContent: 'center', alignSelf: 'center' },
  initial: { color: '#fff', fontSize: 34, fontWeight: '800' },
  name: { textAlign: 'center', fontSize: 22, fontWeight: '800', marginTop: 12, color: colors.text },
  mobile: { textAlign: 'center', color: colors.muted, marginTop: 2 },
  wallet: { backgroundColor: colors.surface, borderRadius: radius.lg, padding: 18, marginTop: 24 },
  wl: { color: colors.muted }, wv: { fontSize: 30, fontWeight: '800', color: colors.text, marginTop: 4 },
});
