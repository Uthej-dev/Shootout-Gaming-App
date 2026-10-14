import React, { useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors, radius, shadow } from '../constants/theme';
import { formatDate, formatTime, rupee } from '../utils/format';
import Button from './Button';
import PrizeBreakdown from './PrizeBreakdown';
import ProgressBar from './ProgressBar';

const STATUS = { upcoming: ['Upcoming', colors.info], current: ['Live', colors.success], previous: ['Ended', colors.muted] };

const Stat = ({ label, value, onPress, open }) => (
  <Pressable onPress={onPress} disabled={!onPress} style={{ flex: 1 }}>
    <Text style={s.statLabel}>{label}{onPress ? <Ionicons name={open ? 'chevron-up' : 'chevron-down'} size={12} color={colors.primary} /> : null}</Text>
    <Text style={s.statValue}>{value}</Text>
  </Pressable>
);

export default function MatchCard({ match: m, onJoin, onViewRoom, joining }) {
  const [open, setOpen] = useState(false);
  const [label, color] = STATUS[m.status] || STATUS.upcoming;

  let action;
  if (m.joined) action = <Button title="View Room" variant="outline" onPress={() => onViewRoom(m)} />;
  else if (m.status !== 'upcoming') action = <Button title={m.status === 'current' ? 'Match Started' : 'Match Ended'} disabled />;
  else if (m.isFull) action = <Button title="Match Full" disabled />;
  else action = <Button title="JOIN NOW" onPress={() => onJoin(m)} loading={joining} />;

  return (
    <View style={s.card}>
      <View style={s.header}>
        <View style={s.logo}><Text style={s.logoTxt}>ShootOut</Text></View>
        <View style={{ alignItems: 'flex-end' }}>
          <Text style={s.title}>{m.title} #{m.matchNumber}</Text>
          <Text style={s.sub}>{formatDate(m.startTime)}</Text>
          <Text style={s.sub}>{formatTime(m.startTime)}</Text>
          <View style={[s.badge, { backgroundColor: color + '22' }]}><Text style={[s.badgeTxt, { color }]}>{label}</Text></View>
        </View>
      </View>

      <View style={s.row}>
        <Stat label="Prize Pool " value={rupee(m.prizePool)} onPress={() => setOpen(!open)} open={open} />
        <Stat label="Per Kill" value={rupee(m.perKill)} />
        <Stat label="Entry Fee" value={rupee(m.entryFee)} />
      </View>
      {open && <PrizeBreakdown items={m.prizeBreakdown} />}

      <View style={[s.row, { marginTop: 14 }]}>
        <Stat label="Team" value={m.teamType} />
        <Stat label="Mode" value={m.mode} />
        <Stat label="Map" value={m.map} />
      </View>

      <View style={{ marginTop: 16 }}>
        <ProgressBar registered={m.registeredPlayers} max={m.maxPlayers} spotsLeft={m.spotsLeft} isFull={m.isFull} />
      </View>
      <View style={{ marginTop: 14, alignItems: 'flex-end' }}>{action}</View>
    </View>
  );
}
const s = StyleSheet.create({
  card: { backgroundColor: colors.card, borderRadius: radius.lg, padding: 16, marginBottom: 16, borderWidth: 1, borderColor: colors.border, ...shadow },
  header: { flexDirection: 'row', justifyContent: 'space-between', borderBottomWidth: 1, borderBottomColor: colors.border, paddingBottom: 12, marginBottom: 14 },
  logo: { backgroundColor: colors.text, borderRadius: radius.sm, paddingHorizontal: 10, justifyContent: 'center', alignSelf: 'flex-start', height: 36 },
  logoTxt: { color: '#fff', fontWeight: '800', letterSpacing: 0.5 },
  title: { fontSize: 17, fontWeight: '800', color: colors.text },
  sub: { fontSize: 12, color: colors.muted, marginTop: 1 },
  badge: { borderRadius: 10, paddingHorizontal: 8, paddingVertical: 2, marginTop: 6 },
  badgeTxt: { fontSize: 11, fontWeight: '700' },
  row: { flexDirection: 'row' },
  statLabel: { fontSize: 12, color: colors.muted, marginBottom: 2 },
  statValue: { fontSize: 16, fontWeight: '700', color: colors.text },
});
