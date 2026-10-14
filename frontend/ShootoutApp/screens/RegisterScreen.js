import React, { useState } from 'react';
import { Alert, KeyboardAvoidingView, Platform, ScrollView, StyleSheet, Text } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useAuth } from '../context/AuthContext';
import { colors } from '../constants/theme';
import Button from '../components/Button';
import Field from '../components/Field';

export default function RegisterScreen({ navigation }) {
  const { register } = useAuth();
  const [f, setF] = useState({ username: '', mobileNumber: '', password: '', confirmPassword: '' });
  const [errors, setErrors] = useState({});
  const [busy, setBusy] = useState(false);
  const set = (k) => (v) => setF({ ...f, [k]: v });

  const validate = () => {
    const e = {};
    if (!/^[A-Za-z0-9_]{3,20}$/.test(f.username)) e.username = '3-20 letters, numbers or underscore';
    if (!/^[6-9]\d{9}$/.test(f.mobileNumber)) e.mobileNumber = 'Enter a valid 10-digit mobile number';
    if (f.password.length < 8) e.password = 'At least 8 characters';
    if (f.password !== f.confirmPassword) e.confirmPassword = 'Passwords do not match';
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const submit = async () => {
    if (!validate()) return;
    setBusy(true);
    try {
      await register(f);
      Alert.alert('Registered', 'Account created. Please log in.', [{ text: 'OK', onPress: () => navigation.navigate('Login') }]);
    } catch (e) {
      if (e.code === 'USERNAME_EXISTS') setErrors({ username: e.message });
      else if (e.code === 'MOBILE_EXISTS') setErrors({ mobileNumber: e.message });
      else if (e.details) setErrors(Object.fromEntries(e.details.map((d) => [d.field, d.message])));
      else Alert.alert('Registration failed', e.message);
    } finally { setBusy(false); }
  };

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: '#fff' }}>
      <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined} style={{ flex: 1 }}>
        <ScrollView contentContainerStyle={{ padding: 28 }} keyboardShouldPersistTaps="handled">
          <Text style={s.h}>Create account</Text>
          <Field label="Username" value={f.username} onChangeText={set('username')} error={errors.username} />
          <Field label="Mobile Number" keyboardType="number-pad" maxLength={10} value={f.mobileNumber} onChangeText={set('mobileNumber')} error={errors.mobileNumber} />
          <Field label="Password" secure value={f.password} onChangeText={set('password')} error={errors.password} />
          <Field label="Confirm Password" secure value={f.confirmPassword} onChangeText={set('confirmPassword')} error={errors.confirmPassword} />
          <Button title="Register" onPress={submit} loading={busy} />
          <Text style={s.link} onPress={() => navigation.navigate('Login')}>Back to Login</Text>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}
const s = StyleSheet.create({
  h: { fontSize: 28, fontWeight: '800', marginBottom: 24, color: colors.text },
  link: { color: colors.primary, fontWeight: '600', textAlign: 'center', marginTop: 20 },
});
