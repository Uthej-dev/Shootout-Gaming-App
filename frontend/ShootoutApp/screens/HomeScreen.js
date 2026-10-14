import React from 'react';
import { ScrollView, StyleSheet, Text } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useAuth } from '../context/AuthContext';
import { GAMES, colors } from '../constants/theme';
import GameCard from '../components/GameCard';

export default function HomeScreen({ navigation }) {
  const { user } = useAuth();
  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: '#fff' }} edges={['top']}>
      <ScrollView contentContainerStyle={{ padding: 20 }}>
        <Text style={s.hi}>Hi, {user?.username}</Text>
        <Text style={s.h}>Choose your game</Text>
        {GAMES.map((g) => <GameCard key={g.key} game={g} onPress={() => navigation.navigate(g.route)} />)}
      </ScrollView>
    </SafeAreaView>
  );
}
const s = StyleSheet.create({
  hi: { color: colors.muted, fontSize: 14 },
  h: { fontSize: 28, fontWeight: '800', color: colors.text, marginBottom: 20 },
});
