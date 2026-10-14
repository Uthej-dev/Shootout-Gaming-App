import React from 'react';
import { ActivityIndicator, FlatList, RefreshControl, StyleSheet, Text, View } from 'react-native';
import { colors } from '../constants/theme';
import MatchCard from './MatchCard';

export default function MatchList({ data, loading, refreshing, error, onRefresh, onJoin, onViewRoom, joiningId, emptyText }) {
  if (loading && !refreshing) return <ActivityIndicator style={{ marginTop: 40 }} color={colors.primary} size="large" />;
  return (
    <FlatList
      data={data}
      keyExtractor={(m) => m.id}
      contentContainerStyle={{ padding: 16 }}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.primary} />}
      ListEmptyComponent={<Text style={s.empty}>{error || emptyText || 'No matches found.'}</Text>}
      renderItem={({ item }) => <MatchCard match={item} onJoin={onJoin} onViewRoom={onViewRoom} joining={joiningId === item.id} />}
    />
  );
}
const s = StyleSheet.create({ empty: { textAlign: 'center', color: colors.muted, marginTop: 60 } });
