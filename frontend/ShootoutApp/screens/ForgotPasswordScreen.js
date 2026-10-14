import React, { useState } from 'react';
import { Alert, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import * as authService from '../services/authService';
import { colors } from '../constants/theme';
import Button from '../components/Button';
import Field from '../components/Field';

export default function ForgotPasswordScreen({ navigation }) {
  const [identifier, setIdentifier] = useState('');
  const [busy, setBusy] = useState(false);
  const submit = async () => {
    if (!identifier.trim()) return;
    setBusy(true);
    try {
      const msg = await authService.forgotPassword(identifier.trim());
      Alert.alert('Request received', `${msg}\n\nOTP verification is coming soon.`, [{ text: 'OK', onPress: () => navigation.goBack() }]);
    } catch (e) { Alert.alert('Error', e.message); } finally { setBusy(false); }
  };
  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: '#fff' }}>
      <View style={{ padding: 28 }}>
        <Text style={s.h}>Forgot password</Text>
        <Field label="Mobile Number / Username" value={identifier} onChangeText={setIdentifier} />
        <Button title="Continue" onPress={submit} loading={busy} />
        <Text style={s.link} onPress={() => navigation.goBack()}>Back to Login</Text>
      </View>
    </SafeAreaView>
  );
}
const s = StyleSheet.create({
  h: { fontSize: 28, fontWeight: '800', marginBottom: 24, color: colors.text },
  link: { color: colors.primary, fontWeight: '600', textAlign: 'center', marginTop: 20 },
});
