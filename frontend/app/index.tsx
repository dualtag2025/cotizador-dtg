import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
  Alert,
  Platform,
} from 'react-native';
import { StatusBar } from 'expo-status-bar';

const API_URL = 'https://cotizador-dtg.onrender.com';

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

export default function Index() {
  const [searchText, setSearchText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SearchResult | null>(null);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [debounceTimer, setDebounceTimer] = useState<NodeJS.Timeout | null>(null);

  const fetchSuggestions = useCallback(async (query: string) => {
    if (query.length < 2) {
      setSuggestions([]);
      setShowSuggestions(false);
      return;
    }
    
    try {
      const response = await fetch(
        `${API_URL}/api/autocomplete?q=${encodeURIComponent(query)}`
      );
      if (response.ok) {
        const data = await response.json();
        setSuggestions(data.suggestions || []);
        setShowSuggestions((data.suggestions || []).length > 0);
      }
    } catch (error) {
      console.log('Autocomplete error:', error);
    }
  }, []);

  const handleTextChange = (text: string) => {
    setSearchText(text);
    setResult(null);
    
    if (debounceTimer) {
      clearTimeout(debounceTimer);
    }
    
    const timer = setTimeout(() => {
      fetchSuggestions(text);
    }, 400);
    
    setDebounceTimer(timer);
  };

  const handleSearch = async (query?: string) => {
    const searchQuery = query || searchText;
    
    if (!searchQuery.trim()) {
      Alert.alert('Error', 'Por favor ingrese un código o nombre');
      return;
    }

    setShowSuggestions(false);
    setLoading(true);
    setResult(null);

    try {
      const response = await fetch(
        `${API_URL}/api/search/${encodeURIComponent(searchQuery.trim())}`
      );
      
      if (response.status === 404) {
        Alert.alert('No encontrado', 'No se encontraron datos para esta búsqueda');
        return;
      }
      
      if (!response.ok) {
        throw new Error('Error de servidor');
      }
      
      const data = await response.json();
      setResult(data);
    } catch (error) {
      Alert.alert('Error', 'Error al buscar. Verifique su conexión a internet.');
      console.log('Search error:', error);
    } finally {
      setLoading(false);
    }
  };

  const selectSuggestion = (suggestion: string) => {
    setSearchText(suggestion);
    setShowSuggestions(false);
    setSuggestions([]);
    handleSearch(suggestion);
  };

  const clearSearch = () => {
    setSearchText('');
    setResult(null);
    setSuggestions([]);
    setShowSuggestions(false);
  };

  return (
    <View style={styles.container}>
      <StatusBar style="light" />
      
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Cotizador DTG</Text>
        <Text style={styles.headerSubtitle}>Consulta de Tasas</Text>
      </View>

      <ScrollView 
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        keyboardShouldPersistTaps="handled"
      >
        {/* Search Box */}
        <View style={styles.searchBox}>
          <Text style={styles.searchTitle}>Buscar Datos</Text>
          <Text style={styles.searchSubtitle}>
            Ingrese código CIIU o nombre del giro de negocio
          </Text>

          <View style={styles.inputRow}>
            <TextInput
              style={styles.input}
              placeholder="Ej: 4711 o Supermercados"
              placeholderTextColor="#999"
              value={searchText}
              onChangeText={handleTextChange}
              autoCapitalize="none"
              autoCorrect={false}
              returnKeyType="search"
              onSubmitEditing={() => handleSearch()}
            />
            {searchText.length > 0 && (
              <TouchableOpacity onPress={clearSearch} style={styles.clearButton}>
                <Text style={styles.clearButtonText}>✕</Text>
              </TouchableOpacity>
            )}
          </View>

          {/* Suggestions */}
          {showSuggestions && suggestions.length > 0 && (
            <View style={styles.suggestionsBox}>
              {suggestions.slice(0, 8).map((item, index) => (
                <TouchableOpacity
                  key={index}
                  style={styles.suggestionItem}
                  onPress={() => selectSuggestion(item)}
                >
                  <Text style={styles.suggestionText} numberOfLines={1}>
                    {item}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          )}

          <TouchableOpacity
            style={[styles.searchButton, loading && styles.searchButtonDisabled]}
            onPress={() => handleSearch()}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color="#fff" size="small" />
            ) : (
              <Text style={styles.searchButtonText}>Buscar</Text>
            )}
          </TouchableOpacity>
        </View>

        {/* Results */}
        {result && (
          <View style={styles.resultsBox}>
            {/* Result Header */}
            <View style={styles.resultHeader}>
              <Text style={styles.resultType}>
                {result.tipo === 'codigo' ? '📋 Código CIIU' : '🏢 Giro de Negocio'}
              </Text>
              <Text style={styles.resultValue}>{result.valor}</Text>
            </View>

            {/* Tasa Campaña - Solo para códigos */}
            {result.tipo === 'codigo' && (result.debito_campana || result.credito_campana) && (
              <View style={styles.rateCard}>
                <Text style={styles.rateTitle}>Tasa Campaña</Text>
                <View style={styles.rateRow}>
                  {result.debito_campana && (
                    <View style={[styles.rateItem, styles.debitoItem]}>
                      <Text style={styles.rateLabel}>Débito</Text>
                      <Text style={styles.rateValue2}>{result.debito_campana}</Text>
                    </View>
                  )}
                  {result.credito_campana && (
                    <View style={[styles.rateItem, styles.creditoItem]}>
                      <Text style={styles.rateLabel}>Crédito</Text>
                      <Text style={styles.rateValue2}>{result.credito_campana}</Text>
                    </View>
                  )}
                </View>
              </View>
            )}

            {/* Tasa Dinámica */}
            {(result.debito_dinamica || result.credito_dinamica) && (
              <View style={styles.rateCard}>
                <Text style={styles.rateTitle}>Tasa Dinámica</Text>
                <View style={styles.rateRow}>
                  {result.debito_dinamica && (
                    <View style={[styles.rateItem, styles.debitoItem]}>
                      <Text style={styles.rateLabel}>Débito</Text>
                      <Text style={styles.rateValue2}>{result.debito_dinamica}</Text>
                    </View>
                  )}
                  {result.credito_dinamica && (
                    <View style={[styles.rateItem, styles.creditoItem]}>
                      <Text style={styles.rateLabel}>Crédito</Text>
                      <Text style={styles.rateValue2}>{result.credito_dinamica}</Text>
                    </View>
                  )}
                </View>
              </View>
            )}

            {/* Tasa Pizarra - Solo para nombres */}
            {result.tipo === 'nombre' && (result.debito_pizarra || result.credito_pizarra) && (
              <View style={styles.rateCard}>
                <Text style={styles.rateTitle}>Tasa Pizarra</Text>
                <View style={styles.rateRow}>
                  {result.debito_pizarra && (
                    <View style={[styles.rateItem, styles.debitoItem]}>
                      <Text style={styles.rateLabel}>Débito</Text>
                      <Text style={styles.rateValue2}>{result.debito_pizarra}</Text>
                    </View>
                  )}
                  {result.credito_pizarra && (
                    <View style={[styles.rateItem, styles.creditoItem]}>
                      <Text style={styles.rateLabel}>Crédito</Text>
                      <Text style={styles.rateValue2}>{result.credito_pizarra}</Text>
                    </View>
                  )}
                </View>
              </View>
            )}

            {/* Info Adicional */}
            {(result.grupo || result.subgrupo) && (
              <View style={styles.infoCard}>
                <Text style={styles.infoTitle}>Información Adicional</Text>
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
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f0f2f5',
  },
  header: {
    backgroundColor: '#0066CC',
    paddingTop: Platform.OS === 'ios' ? 50 : 40,
    paddingBottom: 20,
    paddingHorizontal: 20,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
  },
  headerSubtitle: {
    fontSize: 14,
    color: 'rgba(255,255,255,0.8)',
    marginTop: 4,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    padding: 16,
    paddingBottom: 40,
  },
  searchBox: {
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
  searchTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  searchSubtitle: {
    fontSize: 13,
    color: '#666',
    marginBottom: 16,
  },
  inputRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
    borderRadius: 8,
    paddingHorizontal: 12,
    marginBottom: 12,
  },
  input: {
    flex: 1,
    height: 48,
    fontSize: 16,
    color: '#333',
  },
  clearButton: {
    padding: 8,
  },
  clearButtonText: {
    fontSize: 18,
    color: '#999',
  },
  suggestionsBox: {
    backgroundColor: '#fff',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#e0e0e0',
    marginBottom: 12,
    maxHeight: 200,
  },
  suggestionItem: {
    padding: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  suggestionText: {
    fontSize: 14,
    color: '#333',
  },
  searchButton: {
    backgroundColor: '#0066CC',
    paddingVertical: 14,
    borderRadius: 8,
    alignItems: 'center',
  },
  searchButtonDisabled: {
    opacity: 0.7,
  },
  searchButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  resultsBox: {
    gap: 12,
  },
  resultHeader: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  resultType: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4,
  },
  resultValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  rateCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  rateTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 12,
  },
  rateRow: {
    flexDirection: 'row',
    gap: 12,
  },
  rateItem: {
    flex: 1,
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  debitoItem: {
    backgroundColor: '#E3F2FD',
    borderWidth: 1,
    borderColor: '#0066CC',
  },
  creditoItem: {
    backgroundColor: '#E0F7FA',
    borderWidth: 1,
    borderColor: '#00ACC1',
  },
  rateLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  rateValue2: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  infoCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  infoTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 12,
  },
  infoRow: {
    flexDirection: 'row',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  infoLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
    width: 80,
  },
  infoValue: {
    fontSize: 14,
    color: '#333',
    flex: 1,
  },
});
