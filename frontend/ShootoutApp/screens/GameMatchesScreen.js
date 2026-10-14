import React, { useState } from 'react';
import { Alert, StyleSheet, Text, View } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import useFocusFetch from '../hooks/useFocusFetch';
import * as matchService from '../services/matchService';
import * as walletService from '../services/walletService';
import { colors } from '../constants/theme';
import MatchList from '../components/MatchList';
import Segmented from '../components/Segmented';

const TABS = [{ key: 'upcoming', label: 'Upcoming' }, { key: 'current', label: 'Current' }, { key: 'previous', label: 'Previous' }];

// Shared by BGMI, BGMI TDM and Free Fire.
export default function GameMatchesScreen({ navigation, game }) {
  const [status, setStatus] = useState('upcoming');
  const [joiningId, setJoiningId] = useState(null);
  const [balance, setBalance] = useState(null);
  const list = useFocusFetch(async () => {
    const [matches, w] = await Promise.all([matchService.listByGame(game, status), walletService.getWallet()]);
    setBalance(w.balance);
    return matches;
  }, [game, status]);

  const doJoin = async (m) => {
    setJoiningId(m.id);
    try {
      const res = await matchService.join(m.id);
      setBalance(res.balance);
      await list.reload();
      Alert.alert('Joined!', `${m.title} #${m.matchNumber} joined. New balance: ₹${res.balance}`);
    } catch (e) {
      if (e.code === 'INSUFFICIENT_BALANCE') Alert.alert('Insufficient wallet balance.', 'Please add money to your wallet to join this match.');
      else Alert.alert('Could not join', e.message);
      list.reload();
    } finally { setJoiningId(null); }
  };
  const onJoin = (m) => Alert.alert('Join match', `Entry fee ₹${m.entryFee} will be deducted from your wallet.`, [
    { text: 'Cancel', style: 'cancel' }, { text: 'Join', onPress: () => doJoin(m) },
  ]);

  return (
    <View style={{ flex: 1, backgroundColor: colors.surface }}>
      <View style={s.wallet}>
        <Ionicons name="wallet-outline" size={18} color={colors.primary} />
        <Text style={s.walletTxt}>Wallet: {balance === null ? '—' : `₹${balance}`}</Text>
      </View>
      <Segmented options={TABS} value={status} onChange={setStatus} />
      <MatchList {...list} onRefresh={list.refresh} onJoin={onJoin} joiningId={joiningId}
        onViewRoom={(m) => navigation.navigate('Room', { matchId: m.id, title: `${m.title} #${m.matchNumber}` })}
        emptyText={`No ${status} matches right now.`} />
    </View>
  );
}
const s = StyleSheet.create({
  wallet: { flexDirection: 'row', alignItems: 'center', justifyContent: 'flex-end', paddingHorizontal: 16, paddingTop: 10 },
  walletTxt: { marginLeft: 6, fontWeight: '700', color: colors.text },
});
