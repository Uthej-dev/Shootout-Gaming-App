import React, { useCallback, useState } from 'react';
import { ActivityIndicator, StyleSheet, Text, View } from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import * as matchService from '../services/matchService';
import { colors, radius } from '../constants/theme';

export default function RoomScreen({ route }) {
  const [room, setRoom] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  useFocusEffect(useCallback(() => {
    setLoading(true);
    matchService.getRoom(route.params.matchId).then(setRoom).catch((e) => setError(e.message)).finally(() => setLoading(false));
  }, [route.params.matchId]));

  if (loading) return <ActivityIndicator style={{ marginTop: 60 }} color={colors.primary} />;
  return (
    <View style={s.wrap}>
      {room ? (
        <View style={s.box}>
          <Text style={s.label}>Room ID</Text><Text style={s.value} selectable>{room.roomId}</Text>
          <Text style={[s.label, { marginTop: 16 }]}>Password</Text><Text style={s.value} selectable>{room.roomPassword}</Text>
        </View>
      ) : <Text style={s.msg}>{error || 'Room details not available.'}</Text>}
    </View>
  );
}
const s = StyleSheet.create({
  wrap: { flex: 1, padding: 24, backgroundColor: '#fff' },
  box: { backgroundColor: colors.surface, borderRadius: radius.lg, padding: 24 },
  label: { color: colors.muted, fontSize: 13 }, value: { fontSize: 26, fontWeight: '800', color: colors.text, marginTop: 4 },
  msg: { textAlign: 'center', color: colors.muted, marginTop: 60 },
});
