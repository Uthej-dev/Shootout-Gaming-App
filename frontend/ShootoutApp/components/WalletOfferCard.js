import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { colors, radius, shadow } from '../constants/theme';
import Button from './Button';

export default function WalletOfferCard({ offer, onPress }) {
  return (
    <View style={s.card}>
      <Text style={s.add}>Add ₹{offer.add}</Text>
      <Text style={s.extra}>Get ₹{offer.extra} Extra</Text>
      <Text style={s.total}>You receive ₹{offer.add + offer.extra}</Text>
      <Button title="Add Money" onPress={onPress} style={{ marginTop: 12 }} />
    </View>
  );
}
const s = StyleSheet.create({
  card: { backgroundColor: colors.card, borderRadius: radius.lg, padding: 18, marginBottom: 14, borderWidth: 1, borderColor: colors.border, ...shadow },
  add: { fontSize: 20, fontWeight: '800', color: colors.text },
  extra: { fontSize: 15, color: colors.success, fontWeight: '700', marginTop: 2 },
  total: { fontSize: 13, color: colors.muted, marginTop: 4 },
});
