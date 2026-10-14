import React from 'react';
import { Alert, ScrollView, StyleSheet, Text } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { colors } from '../constants/theme';
import WalletOfferCard from '../components/WalletOfferCard';

// Placeholder data until the offers API + payment gateway are built.
const OFFERS = [{ add: 50, extra: 2 }, { add: 100, extra: 6 }, { add: 200, extra: 15 }, { add: 500, extra: 50 }];

export default function EarnScreen() {
  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.surface }} edges={['top']}>
      <ScrollView contentContainerStyle={{ padding: 20 }}>
        <Text style={s.h}>Offers</Text>
        {OFFERS.map((o) => <WalletOfferCard key={o.add} offer={o} onPress={() => Alert.alert('Coming soon', 'Wallet recharge is not available yet.')} />)}
      </ScrollView>
    </SafeAreaView>
  );
}
const s = StyleSheet.create({ h: { fontSize: 26, fontWeight: '800', marginBottom: 16, color: colors.text } });
