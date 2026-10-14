import React from 'react';
import { ActivityIndicator, Pressable, StyleSheet, Text } from 'react-native';
import { colors, radius } from '../constants/theme';

export default function Button({ title, onPress, loading, disabled, variant = 'primary', style }) {
  const off = disabled || loading;
  return (
    <Pressable
      onPress={onPress}
      disabled={off}
      style={({ pressed }) => [s.btn, variant === 'outline' && s.outline, off && s.off, pressed && { opacity: 0.85 }, style]}
    >
      {loading ? <ActivityIndicator color={variant === 'outline' ? colors.primary : '#fff'} /> : (
        <Text style={[s.text, variant === 'outline' && { color: colors.primary }]}>{title}</Text>
      )}
    </Pressable>
  );
}
const s = StyleSheet.create({
  btn: { backgroundColor: colors.primary, borderRadius: radius.md, paddingVertical: 14, paddingHorizontal: 22, alignItems: 'center' },
  outline: { backgroundColor: 'transparent', borderWidth: 1.5, borderColor: colors.primary },
  off: { opacity: 0.5 },
  text: { color: '#fff', fontWeight: '700', fontSize: 16, letterSpacing: 0.5 },
});
