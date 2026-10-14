import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { colors } from '../constants/theme';

export default function ProgressBar({ registered, max, spotsLeft, isFull }) {
  const pct = Math.min(100, Math.round((registered / max) * 100));
  return (
    <View>
      <View style={s.track}><View style={[s.fill, { width: `${pct}%`, backgroundColor: isFull ? colors.danger : colors.primary }]} /></View>
      <View style={s.row}>
        <Text style={s.txt}>{registered} / {max} players</Text>
        <Text style={[s.txt, { fontWeight: '700', color: isFull ? colors.danger : colors.success }]}>
          {isFull ? 'FULL' : `${spotsLeft} spots left`}
        </Text>
      </View>
    </View>
  );
}
const s = StyleSheet.create({
  track: { height: 8, borderRadius: 4, backgroundColor: colors.border, overflow: 'hidden' },
  fill: { height: 8, borderRadius: 4 },
  row: { flexDirection: 'row', justifyContent: 'space-between', marginTop: 6 },
  txt: { fontSize: 12, color: colors.muted },
});
