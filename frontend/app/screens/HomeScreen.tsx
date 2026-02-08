import React, { useState } from 'react';
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

const EXPO_PUBLIC_BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

interface CIUData {
  ciu: string;
  grupo?: string;
  subgrupo?: string;
  debito_campal?: string;
  credito_campal?: string;
  debito_dinamica?: string;
  credito_dinamica?: string;
  debito_pizarra?: string;
  credito_pizarra?: string;
}

const HomeScreen = () => {
  const [ciu, setCiu] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<CIUData | null>(null);

  const handleSearch = async () => {
    if (!ciu.trim()) {
      Alert.alert('Error', 'Por favor ingrese un CIU');
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const response = await axios.get(
        `${EXPO_PUBLIC_BACKEND_URL}/api/search/${ciu.trim()}`
      );
      setResult(response.data);
    } catch (error: any) {
      if (error.response?.status === 404) {
        Alert.alert('No encontrado', 'CIU no encontrado');
      } else {
        Alert.alert('Error', 'Error al buscar CIU. Por favor intente nuevamente.');
      }
      console.error('Search error:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderRateCard = (title: string, debitoLabel: string, debitoValue?: string, creditoLabel: string, creditoValue?: string) => {
    if (!debitoValue && !creditoValue) return null;

    return (
      <View style={styles.card}>
        <Text style={styles.cardTitle}>{title}</Text>
        <View style={styles.rateContainer}>
          {debitoValue && (
            <View style={[styles.rateBox, styles.debitoBox]}>
              <Text style={styles.rateLabel}>{debitoLabel}</Text>
              <Text style={styles.rateValue}>{debitoValue}</Text>
            </View>
          )}
          {creditoValue && (
            <View style={[styles.rateBox, styles.creditoBox]}>
              <Text style={styles.rateLabel}>{creditoLabel}</Text>
              <Text style={styles.rateValue}>{creditoValue}</Text>
            </View>
          )}
        </View>
      </View>
    );
  };

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
          <View style={styles.searchContainer}>
            <Text style={styles.title}>Buscar CIU</Text>
            <Text style={styles.subtitle}>Ingrese el Código MCC para consultar las tasas</Text>

            <View style={styles.inputContainer}>
              <Ionicons name="search" size={24} color="#666" style={styles.searchIcon} />
              <TextInput
                style={styles.input}
                placeholder="Ingrese CIU (Código MCC)"
                value={ciu}
                onChangeText={setCiu}
                keyboardType="default"
                autoCapitalize="none"
                returnKeyType="search"
                onSubmitEditing={handleSearch}
              />
            </View>

            <TouchableOpacity
              style={styles.searchButton}
              onPress={handleSearch}
              disabled={loading}
            >
              {loading ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <>
                  <Ionicons name="search" size={20} color="#fff" />
                  <Text style={styles.searchButtonText}>Buscar</Text>
                </>
              )}
            </TouchableOpacity>
          </View>

          {result && (
            <View style={styles.resultsContainer}>
              <View style={styles.resultHeader}>
                <Ionicons name="checkmark-circle" size={32} color="#4CAF50" />
                <Text style={styles.resultHeaderText}>CIU: {result.ciu}</Text>
              </View>

              {/* Tasa Campal */}
              {renderRateCard(
                'Tasa Campal (Primeros 3 meses)',
                'Débito',
                result.debito_campal,
                'Crédito',
                result.credito_campal
              )}

              {/* Tasa Dinámica */}
              {renderRateCard(
                'Tasa Dinámica (Desde mes 4)',
                'Débito',
                result.debito_dinamica,
                'Crédito',
                result.credito_dinamica
              )}

              {/* Tasa Pizarra */}
              {renderRateCard(
                'Tasa Pizarra',
                'Débito',
                result.debito_pizarra,
                'Crédito',
                result.credito_pizarra
              )}

              {/* Grupo y Subgrupo */}
              {(result.grupo || result.subgrupo) && (
                <View style={styles.card}>
                  <Text style={styles.cardTitle}>Información Adicional</Text>
                  {result.grupo && (
                    <View style={styles.infoRow}>
                      <Text style={styles.infoLabel}>Grupo:</Text>
                      <Text style={styles.infoValue}>{result.grupo}</Text>
                    </View>
                  )}
                  {result.subgrupo && (
                    <View style={styles.infoRow}>
                      <Text style={styles.infoLabel}>Subgrupo:</Text>
                      <Text style={styles.infoValue}>{result.subgrupo}</Text>
                    </View>
                  )}
                </View>
              )}
            </View>
          )}
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
  searchContainer: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
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
    marginBottom: 20,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
    borderRadius: 8,
    paddingHorizontal: 12,
    marginBottom: 16,
  },
  searchIcon: {
    marginRight: 8,
  },
  input: {
    flex: 1,
    height: 48,
    fontSize: 16,
    color: '#333',
  },
  searchButton: {
    backgroundColor: '#0066CC',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 14,
    borderRadius: 8,
    gap: 8,
  },
  searchButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  resultsContainer: {
    gap: 16,
  },
  resultHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 12,
    gap: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  resultHeaderText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
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
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 12,
  },
  rateContainer: {
    flexDirection: 'row',
    gap: 12,
  },
  rateBox: {
    flex: 1,
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  debitoBox: {
    backgroundColor: '#E3F2FD',
    borderWidth: 2,
    borderColor: '#0066CC',
  },
  creditoBox: {
    backgroundColor: '#E0F7FA',
    borderWidth: 2,
    borderColor: '#00BFFF',
  },
  rateLabel: {
    fontSize: 12,
    fontWeight: '600',
    color: '#666',
    marginBottom: 4,
  },
  rateValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  infoLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
  },
  infoValue: {
    fontSize: 14,
    color: '#333',
    flex: 1,
    textAlign: 'right',
  },
});

export default HomeScreen;
