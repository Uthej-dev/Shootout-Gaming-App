import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { colors, radius } from '../constants/theme';
import { rupee } from '../utils/format';

export default function PrizeBreakdown({ items = [] }) {
  return (
    <View style={s.box}>
      <Text style={s.title}>Prize Breakdown</Text>
      {items.length === 0 ? <Text style={s.empty}>Breakdown will be announced soon.</Text> : items.map((p) => (
        <View key={p.rank} style={s.row}>
          <Text style={s.rank}>Rank {p.rank}</Text>
          <Text style={s.amt}>{rupee(p.amount)}</Text>
        </View>
      ))}
    </View>
  );
}
const s = StyleSheet.create({
  box: { backgroundColor: colors.surface, borderRadius: radius.sm, padding: 12, marginTop: 10 },
  title: { fontWeight: '700', color: colors.text, marginBottom: 6 },
  row: { flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 3 },
  rank: { color: colors.muted }, amt: { fontWeight: '700', color: colors.text },
  empty: { color: colors.muted, fontSize: 12 },
});
