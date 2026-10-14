import React from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { radius, shadow } from '../constants/theme';

// Swap the icon for a game image later: <Image source={require('../assets/bgmi.png')} />
export default function GameCard({ game, onPress }) {
  return (
    <Pressable onPress={onPress} style={({ pressed }) => [s.card, { backgroundColor: game.color }, pressed && { transform: [{ scale: 0.98 }] }]}>
      <View style={s.iconWrap}><Ionicons name={game.icon} size={34} color="#fff" /></View>
      <View style={{ flex: 1 }}>
        <Text style={s.title}>{game.title}</Text>
        <Text style={s.sub}>{game.subtitle}</Text>
      </View>
      <Ionicons name="chevron-forward" size={24} color="#fff" />
    </Pressable>
  );
}
const s = StyleSheet.create({
  card: { flexDirection: 'row', alignItems: 'center', borderRadius: radius.lg, padding: 20, marginBottom: 16, ...shadow },
  iconWrap: { width: 60, height: 60, borderRadius: 30, backgroundColor: 'rgba(255,255,255,0.22)', alignItems: 'center', justifyContent: 'center', marginRight: 16 },
  title: { color: '#fff', fontSize: 22, fontWeight: '800' },
  sub: { color: 'rgba(255,255,255,0.9)', fontSize: 13, marginTop: 2 },
});
