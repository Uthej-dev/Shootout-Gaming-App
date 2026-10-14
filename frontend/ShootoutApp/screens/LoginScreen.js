import React, { useState } from 'react';
import { KeyboardAvoidingView, Platform, ScrollView, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useAuth } from '../context/AuthContext';
import { colors } from '../constants/theme';
import Button from '../components/Button';
import Field from '../components/Field';

export default function LoginScreen({ navigation }) {
  const { login } = useAuth();
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  const submit = async () => {
    if (!identifier.trim() || !password) return setError('Enter your username/mobile and password');
    setBusy(true); setError('');
    try { await login(identifier.trim(), password); } catch (e) { setError(e.message); } finally { setBusy(false); }
  };

  return (
    <SafeAreaView style={s.safe}>
      <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined} style={{ flex: 1 }}>
        <ScrollView contentContainerStyle={s.body} keyboardShouldPersistTaps="handled">
          <Text style={s.brand}>Shoot<Text style={{ color: colors.primary }}>Out</Text></Text>
          <Field label="Username or Mobile Number" value={identifier} onChangeText={setIdentifier} />
          <Field label="Password" secure value={password} onChangeText={setPassword} />
          {!!error && <Text style={s.error}>{error}</Text>}
          <Button title="Login" onPress={submit} loading={busy} style={{ marginTop: 6 }} />
          <View style={s.links}>
            <Text style={s.link} onPress={() => navigation.navigate('ForgotPassword')}>Forgot Password?</Text>
            <Text style={s.link} onPress={() => navigation.navigate('Register')}>Register Yourself</Text>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}
const s = StyleSheet.create({
  safe: { flex: 1, backgroundColor: '#fff' },
  body: { padding: 28, flexGrow: 1, justifyContent: 'center' },
  brand: { fontSize: 40, fontWeight: '900', textAlign: 'center', marginBottom: 40, color: colors.text },
  error: { color: colors.danger, marginBottom: 10, textAlign: 'center' },
  links: { flexDirection: 'row', justifyContent: 'space-between', marginTop: 22 },
  link: { color: colors.primary, fontWeight: '600' },
});
