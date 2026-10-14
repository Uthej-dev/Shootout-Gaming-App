import React, { useState } from 'react';
import { Pressable, StyleSheet, Text, TextInput, View } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors, radius } from '../constants/theme';

export default function Field({ label, error, secure, ...props }) {
  const [hidden, setHidden] = useState(!!secure);
  return (
    <View style={{ marginBottom: 14 }}>
      <Text style={s.label}>{label}</Text>
      <View style={[s.box, error && { borderColor: colors.danger }]}>
        <TextInput style={s.input} placeholderTextColor="#9CA3AF" secureTextEntry={hidden} autoCapitalize="none" {...props} />
        {secure && (
          <Pressable onPress={() => setHidden(!hidden)} hitSlop={10}>
            <Ionicons name={hidden ? 'eye-off-outline' : 'eye-outline'} size={20} color={colors.muted} />
          </Pressable>
        )}
      </View>
      {!!error && <Text style={s.err}>{error}</Text>}
    </View>
  );
}
const s = StyleSheet.create({
  label: { fontSize: 13, fontWeight: '600', color: colors.muted, marginBottom: 6 },
  box: { flexDirection: 'row', alignItems: 'center', borderWidth: 1.5, borderColor: colors.border, borderRadius: radius.md, paddingHorizontal: 14, backgroundColor: colors.surface },
  input: { flex: 1, paddingVertical: 13, fontSize: 16, color: colors.text },
  err: { color: colors.danger, fontSize: 12, marginTop: 4 },
});
