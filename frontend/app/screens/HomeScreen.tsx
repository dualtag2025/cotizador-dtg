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
  FlatList,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import axios from 'axios';

const EXPO_PUBLIC_BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

interface SearchResult {
  tipo: string;
  valor: string;
  grupo?: string;
  subgrupo?: string;
  debito_campana?: string;
  credito_campana?: string;
  debito_dinamica?: string;
  credito_dinamica?: string;
  debito_pizarra?: string;
  credito_pizarra?: string;
}

const HomeScreen = () => {
  const [searchText, setSearchText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SearchResult | null>(null);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [loadingSuggestions, setLoadingSuggestions] = useState(false);

  // Debounce para autocompletado
  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchText.length >= 2) {
        fetchSuggestions(searchText);
      } else {
        setSuggestions([]);
        setShowSuggestions(false);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [searchText]);

  const fetchSuggestions = async (query: string) => {
    setLoadingSuggestions(true);
    try {
      const response = await axios.get(
        `${EXPO_PUBLIC_BACKEND_URL}/api/autocomplete?q=${encodeURIComponent(query)}`
      );
      setSuggestions(response.data.suggestions || []);
      setShowSuggestions(response.data.suggestions.length > 0);
    } catch (error) {
      console.error('Autocomplete error:', error);
      setSuggestions([]);
      setShowSuggestions(false);
    } finally {
      setLoadingSuggestions(false);
    }
  };

  const handleSearch = async (query?: string) => {
    const searchQuery = query || searchText;
    
    if (!searchQuery.trim()) {
      Alert.alert('Error', 'Por favor ingrese datos');
      return;
    }

    setShowSuggestions(false);
    setLoading(true);
    setResult(null);

    try {
      const response = await axios.get(
        `${EXPO_PUBLIC_BACKEND_URL}/api/search/${encodeURIComponent(searchQuery.trim())}`
      );
      setResult(response.data);
    } catch (error: any) {
      if (error.response?.status === 404) {
        Alert.alert('No encontrado', 'Datos no encontrados');
      } else {
        Alert.alert('Error', 'Error al buscar datos. Por favor intente nuevamente.');
      }
      console.error('Search error:', error);
    } finally {
      setLoading(false);
    }
  };

  const selectSuggestion = (suggestion: string) => {
    setSearchText(suggestion);
    setShowSuggestions(false);
    handleSearch(suggestion);
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
            <Text style={styles.title}>Buscar Datos</Text>
            <Text style={styles.subtitle}>Ingrese código CIIU o nombre del giro de negocio</Text>

            <View style={styles.inputWrapper}>
              <View style={styles.inputContainer}>
                <Ionicons name="search" size={24} color="#666" style={styles.searchIcon} />
                <TextInput
                  style={styles.input}
                  placeholder="Ingrese Datos"
                  value={searchText}
                  onChangeText={(text) => {
                    setSearchText(text);
                    setResult(null);
                  }}
                  autoCapitalize="none"
                  returnKeyType="search"
                  onSubmitEditing={() => handleSearch()}
                />
                {searchText.length > 0 && (
                  <TouchableOpacity onPress={() => {
                    setSearchText('');
                    setResult(null);
                    setSuggestions([]);
                    setShowSuggestions(false);
                  }}>
                    <Ionicons name="close-circle" size={20} color="#666" />
                  </TouchableOpacity>
                )}
              </View>

              {/* Sugerencias de autocompletado */}
              {showSuggestions && suggestions.length > 0 && (
                <View style={styles.suggestionsContainer}>
                  <FlatList
                    data={suggestions}
                    keyExtractor={(item, index) => `${item}-${index}`}
                    renderItem={({ item }) => (
                      <TouchableOpacity
                        style={styles.suggestionItem}
                        onPress={() => selectSuggestion(item)}
                      >
                        <Ionicons name="business-outline" size={18} color="#666" style={{ marginRight: 8 }} />
                        <Text style={styles.suggestionText} numberOfLines={2}>{item}</Text>
                      </TouchableOpacity>
                    )}
                    scrollEnabled={false}
                  />
                </View>
              )}
            </View>

            <TouchableOpacity
              style={styles.searchButton}
              onPress={() => handleSearch()}
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
                <View style={{ flex: 1 }}>
                  <Text style={styles.resultHeaderText}>
                    {result.tipo === 'codigo' ? 'Código CIIU' : 'Giro de Negocio'}
                  </Text>
                  <Text style={styles.resultValueText}>{result.valor}</Text>
                  {result.tipo === 'codigo' && (
                    <Text style={styles.resultNote}>
                      * Tasas promocionales trimestrales
                    </Text>
                  )}
                </View>
              </View>

              {/* Tasa Campaña - Solo para códigos */}
              {result.tipo === 'codigo' && renderRateCard(
                'Tasa Campaña',
                'Débito',
                result.debito_campana,
                'Crédito',
                result.credito_campana
              )}

              {/* Tasa Dinámica - Para códigos y nombres */}
              {renderRateCard(
                'Tasa Dinámica',
                'Débito',
                result.debito_dinamica,
                'Crédito',
                result.credito_dinamica
              )}

              {/* Tasa Pizarra - Solo para nombres */}
              {result.tipo === 'nombre' && renderRateCard(
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
  inputWrapper: {
    marginBottom: 16,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
    borderRadius: 8,
    paddingHorizontal: 12,
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
  suggestionsContainer: {
    backgroundColor: '#fff',
    borderRadius: 8,
    marginTop: 8,
    borderWidth: 1,
    borderColor: '#e0e0e0',
    maxHeight: 300,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  suggestionItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  suggestionText: {
    fontSize: 14,
    color: '#333',
    flex: 1,
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
    alignItems: 'flex-start',
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
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
  },
  resultValueText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 4,
  },
  resultNote: {
    fontSize: 12,
    color: '#FF9800',
    fontStyle: 'italic',
    marginTop: 4,
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
