import React, { useState } from 'react';
import { View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import useFocusFetch from '../hooks/useFocusFetch';
import * as userService from '../services/userService';
import { colors } from '../constants/theme';
import MatchList from '../components/MatchList';
import Segmented from '../components/Segmented';

const TABS = [
  { key: 'upcoming', label: 'Upcoming' }, { key: 'current', label: 'Current' },
  { key: 'previous', label: 'Previous' }, { key: 'joined', label: 'Joined' },
];

// Your matches. Browse and join new ones from each game screen.
export default function MatchesScreen({ navigation, initial = 'joined' }) {
  const [tab, setTab] = useState(initial);
  const list = useFocusFetch(() => userService.joinedMatches(), []);
  const data = tab === 'joined' ? list.data : list.data.filter((m) => m.status === tab);
  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.surface }} edges={['top']}>
      <View style={{ flex: 1 }}>
        <Segmented options={TABS} value={tab} onChange={setTab} />
        <MatchList {...list} data={data} onRefresh={list.refresh}
          onViewRoom={(m) => navigation.navigate('Room', { matchId: m.id, title: `${m.title} #${m.matchNumber}` })}
          emptyText={tab === 'joined' ? "You haven't joined any matches yet." : `No ${tab} matches among your joined matches.`} />
      </View>
    </SafeAreaView>
  );
}
