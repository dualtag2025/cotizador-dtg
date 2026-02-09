import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
  Alert,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import axios from 'axios';
import { useAuth } from '../../src/context/AuthContext';

const EXPO_PUBLIC_BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

interface SheetConfig {
  comision_especial_url: string;
  comisiones_por_giro_url: string;
  last_sync?: string;
}

const AdminScreen = () => {
  const { token, isAuthenticated, login, logout } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [config, setConfig] = useState<SheetConfig | null>(null);
  const [sheet1Url, setSheet1Url] = useState('');
  const [sheet2Url, setSheet2Url] = useState('');

  useEffect(() => {
    if (isAuthenticated) {
      loadConfig();
    }
  }, [isAuthenticated]);

  const loadConfig = async () => {
    try {
      const response = await axios.get(`${EXPO_PUBLIC_BACKEND_URL}/api/config/sheets`);
      setConfig(response.data);
      setSheet1Url(response.data.comision_especial_url);
      setSheet2Url(response.data.comisiones_por_giro_url);
    } catch (error) {
      console.error('Error loading config:', error);
      Alert.alert('Error', 'Error al cargar configuración');
    }
  };

  const handleLogin = async () => {
    if (!username.trim() || !password.trim()) {
      Alert.alert('Error', 'Por favor ingrese usuario y contraseña');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${EXPO_PUBLIC_BACKEND_URL}/api/auth/login`, {
        username: username.trim(),
        password: password.trim(),
      });

      await login(response.data.access_token);
      Alert.alert('Éxito', 'Inicio de sesión exitoso');
      setUsername('');
      setPassword('');
    } catch (error: any) {
      if (error.response?.status === 401) {
        Alert.alert('Error', 'Usuario o contraseña incorrectos');
      } else {
        Alert.alert('Error', 'Error al iniciar sesión');
      }
      console.error('Login error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    Alert.alert(
      'Cerrar Sesión',
      '¿Está seguro que desea cerrar sesión?',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Cerrar Sesión',
          style: 'destructive',
          onPress: async () => {
            await logout();
            setConfig(null);
            setSheet1Url('');
            setSheet2Url('');
          },
        },
      ]
    );
  };

  const handleUpdateUrls = async () => {
    if (!sheet1Url.trim() || !sheet2Url.trim()) {
      Alert.alert('Error', 'Por favor ingrese ambas URLs');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.put(
        `${EXPO_PUBLIC_BACKEND_URL}/api/config/sheets`,
        {
          comision_especial_url: sheet1Url.trim(),
          comisiones_por_giro_url: sheet2Url.trim(),
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setConfig(response.data);
      Alert.alert('Éxito', 'URLs actualizadas exitosamente');
    } catch (error: any) {
      if (error.response?.status === 401) {
        Alert.alert('Error', 'Sesión expirada. Por favor inicie sesión nuevamente.');
        await logout();
      } else {
        Alert.alert('Error', 'Error al actualizar URLs');
      }
      console.error('Update error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSync = async () => {
    Alert.alert(
      'Sincronizar Datos',
      '¿Desea sincronizar los datos desde Google Sheets?',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Sincronizar',
          onPress: async () => {
            setSyncing(true);
            try {
              const response = await axios.post(
                `${EXPO_PUBLIC_BACKEND_URL}/api/sync`,
                {},
                {
                  headers: {
                    Authorization: `Bearer ${token}`,
                  },
                }
              );

              Alert.alert(
                'Sincronización Exitosa',
                `${response.data.records_synced} registros sincronizados`
              );
              await loadConfig();
            } catch (error: any) {
              if (error.response?.status === 401) {
                Alert.alert('Error', 'Sesión expirada. Por favor inicie sesión nuevamente.');
                await logout();
              } else {
                const errorMsg = error.response?.data?.detail || 'Error al sincronizar datos';
                Alert.alert('Error', errorMsg);
              }
              console.error('Sync error:', error);
            } finally {
              setSyncing(false);
            }
          },
        },
      ]
    );
  };

  if (!isAuthenticated) {
    return (
      <SafeAreaView style={styles.container} edges={['bottom']}>
        <KeyboardAvoidingView
          behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
          style={styles.keyboardView}
        >
          <ScrollView
            style={styles.scrollView}
            contentContainerStyle={styles.scrollContent}
            keyboardShouldPersistTaps="handled"
          >
            <View style={styles.loginContainer}>
              <Ionicons name="lock-closed" size={64} color="#0066CC" style={styles.lockIcon} />
              <Text style={styles.title}>Acceso Administrador</Text>
              <Text style={styles.subtitle}>Ingrese sus credenciales</Text>

              <View style={styles.inputGroup}>
                <Text style={styles.label}>Usuario</Text>
                <View style={styles.inputContainer}>
                  <Ionicons name="person" size={20} color="#666" style={styles.icon} />
                  <TextInput
                    style={styles.input}
                    placeholder="Usuario"
                    value={username}
                    onChangeText={setUsername}
                    autoCapitalize="none"
                    returnKeyType="next"
                  />
                </View>
              </View>

              <View style={styles.inputGroup}>
                <Text style={styles.label}>Contraseña</Text>
                <View style={styles.inputContainer}>
                  <Ionicons name="lock-closed" size={20} color="#666" style={styles.icon} />
                  <TextInput
                    style={styles.input}
                    placeholder="Contraseña"
                    value={password}
                    onChangeText={setPassword}
                    secureTextEntry
                    returnKeyType="done"
                    onSubmitEditing={handleLogin}
                  />
                </View>
              </View>

              <TouchableOpacity
                style={styles.loginButton}
                onPress={handleLogin}
                disabled={loading}
              >
                {loading ? (
                  <ActivityIndicator color="#fff" />
                ) : (
                  <>
                    <Ionicons name="log-in" size={20} color="#fff" />
                    <Text style={styles.loginButtonText}>Iniciar Sesión</Text>
                  </>
                )}
              </TouchableOpacity>
            </View>
          </ScrollView>
        </KeyboardAvoidingView>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container} edges={['bottom']}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardView}
      >
        <ScrollView
          style={styles.scrollView}
          contentContainerStyle={styles.scrollContent}
          keyboardShouldPersistTaps="handled"
        >
          <View style={styles.adminContainer}>
            <View style={styles.header}>
              <View>
                <Text style={styles.title}>Panel de Administración</Text>
                {config?.last_sync && (
                  <Text style={styles.lastSync}>
                    Última sincronización: {new Date(config.last_sync).toLocaleString('es')}
                  </Text>
                )}
              </View>
              <TouchableOpacity onPress={handleLogout} style={styles.logoutButton}>
                <Ionicons name="log-out" size={24} color="#FF5252" />
              </TouchableOpacity>
            </View>

            <View style={styles.card}>
              <Text style={styles.cardTitle}>Configuración de Google Sheets</Text>

              <View style={styles.inputGroup}>
                <Text style={styles.label}>Sheet 1: Comisión especial 3m</Text>
                <TextInput
                  style={styles.urlInput}
                  placeholder="URL del Google Sheet"
                  value={sheet1Url}
                  onChangeText={setSheet1Url}
                  multiline
                  autoCapitalize="none"
                />
              </View>

              <View style={styles.inputGroup}>
                <Text style={styles.label}>Sheet 2: Comisiones por Giro</Text>
                <TextInput
                  style={styles.urlInput}
                  placeholder="URL del Google Sheet"
                  value={sheet2Url}
                  onChangeText={setSheet2Url}
                  multiline
                  autoCapitalize="none"
                />
              </View>

              <TouchableOpacity
                style={styles.updateButton}
                onPress={handleUpdateUrls}
                disabled={loading}
              >
                {loading ? (
                  <ActivityIndicator color="#fff" />
                ) : (
                  <>
                    <Ionicons name="save" size={20} color="#fff" />
                    <Text style={styles.buttonText}>Guardar URLs</Text>
                  </>
                )}
              </TouchableOpacity>
            </View>

            <View style={styles.card}>
              <Text style={styles.cardTitle}>Sincronización de Datos</Text>
              <Text style={styles.description}>
                Sincronice los datos desde los Google Sheets configurados.
                Esto actualizará todos los datos de CIU disponibles para consulta.
              </Text>

              <TouchableOpacity
                style={styles.syncButton}
                onPress={handleSync}
                disabled={syncing}
              >
                {syncing ? (
                  <ActivityIndicator color="#fff" />
                ) : (
                  <>
                    <Ionicons name="sync" size={20} color="#fff" />
                    <Text style={styles.buttonText}>Sincronizar Ahora</Text>
                  </>
                )}
              </TouchableOpacity>
            </View>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  keyboardView: {
    flex: 1,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    padding: 16,
  },
  loginContainer: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 24,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  lockIcon: {
    marginBottom: 16,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 14,
    color: '#666',
    marginBottom: 24,
  },
  inputGroup: {
    width: '100%',
    marginBottom: 16,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
    borderRadius: 8,
    paddingHorizontal: 12,
  },
  icon: {
    marginRight: 8,
  },
  input: {
    flex: 1,
    height: 48,
    fontSize: 16,
    color: '#333',
  },
  loginButton: {
    backgroundColor: '#0066CC',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 14,
    borderRadius: 8,
    width: '100%',
    gap: 8,
    marginTop: 8,
  },
  loginButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  adminContainer: {
    gap: 16,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  lastSync: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
  },
  logoutButton: {
    padding: 8,
  },
  card: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 16,
  },
  urlInput: {
    backgroundColor: '#f5f5f5',
    borderRadius: 8,
    padding: 12,
    fontSize: 14,
    color: '#333',
    minHeight: 80,
    textAlignVertical: 'top',
  },
  updateButton: {
    backgroundColor: '#4CAF50',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 14,
    borderRadius: 8,
    gap: 8,
    marginTop: 8,
  },
  description: {
    fontSize: 14,
    color: '#666',
    marginBottom: 16,
  },
  syncButton: {
    backgroundColor: '#FF9800',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 14,
    borderRadius: 8,
    gap: 8,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default AdminScreen;
