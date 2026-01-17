import React, { useState, useEffect } from 'react';
import {
  View,
  StyleSheet,
  FlatList,
  Text,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  RefreshControl,
} from 'react-native';
import { fineAPI } from '../api/client';

export const FinesScreen = ({ navigation }) => {
  const [fines, setFines] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [totalAmount, setTotalAmount] = useState(0);
  const [paidAmount, setPaidAmount] = useState(0);

  useEffect(() => {
    loadFines();
  }, []);

  const loadFines = async () => {
    try {
      setLoading(true);
      const data = await fineAPI.getFines();
      const finesList = data.results || data;
      setFines(finesList);

      // Calculate totals
      const total = finesList.reduce((sum, f) => sum + (parseFloat(f.amount) || 0), 0);
      const paid = finesList
        .filter((f) => f.paid)
        .reduce((sum, f) => sum + (parseFloat(f.amount) || 0), 0);

      setTotalAmount(total);
      setPaidAmount(paid);
    } catch (error) {
      Alert.alert('Error', 'Failed to load fines');
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadFines().finally(() => setRefreshing(false));
  };

  const handlePayFine = (fine) => {
    if (fine.paid) {
      Alert.alert('Already Paid', 'This fine has already been paid');
      return;
    }
    navigation.navigate('PayFine', { fine });
  };

  const renderFine = ({ item }) => (
    <View style={styles.fineCard}>
      <View style={styles.fineCardContent}>
        <View style={styles.fineTop}>
          <Text style={styles.fineAmount}>₹{item.amount}</Text>
          <View
            style={[
              styles.badge,
              { backgroundColor: item.paid ? '#2ecc71' : '#e74c3c' },
            ]}
          >
            <Text style={styles.badgeText}>{item.paid ? 'Paid' : 'Pending'}</Text>
          </View>
        </View>
        <Text style={styles.bookTitle} numberOfLines={2}>
          {item.issued_book?.book?.title}
        </Text>
        <View style={styles.fineDetails}>
          <Text style={styles.detailText}>
            Due: {new Date(item.issued_book?.due_date).toLocaleDateString()}
          </Text>
        </View>
      </View>

      {!item.paid && (
        <TouchableOpacity
          style={styles.payButton}
          onPress={() => handlePayFine(item)}
        >
          <Text style={styles.payButtonText}>Pay Now</Text>
        </TouchableOpacity>
      )}
    </View>
  );

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#3498db" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Summary Cards */}
      <View style={styles.summaryCards}>
        <View style={[styles.summaryCard, styles.totalCard]}>
          <Text style={styles.summaryLabel}>Total Fines</Text>
          <Text style={styles.summaryValue}>₹{totalAmount.toFixed(2)}</Text>
        </View>
        <View style={[styles.summaryCard, styles.paidCard]}>
          <Text style={styles.summaryLabel}>Paid</Text>
          <Text style={styles.summaryValue}>₹{paidAmount.toFixed(2)}</Text>
        </View>
      </View>

      {/* Fines List */}
      {fines.length > 0 ? (
        <FlatList
          data={fines}
          renderItem={renderFine}
          keyExtractor={(item) => item.id.toString()}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
          contentContainerStyle={styles.listContent}
        />
      ) : (
        <View style={styles.emptyState}>
          <Text style={styles.emptyStateText}>No fines! 🎉</Text>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  summaryCards: {
    flexDirection: 'row',
    paddingHorizontal: 10,
    paddingVertical: 16,
    gap: 10,
  },
  summaryCard: {
    flex: 1,
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
  },
  totalCard: {
    backgroundColor: '#3498db',
  },
  paidCard: {
    backgroundColor: '#2ecc71',
  },
  summaryLabel: {
    color: '#fff',
    fontSize: 12,
    marginBottom: 8,
    opacity: 0.8,
  },
  summaryValue: {
    color: '#fff',
    fontSize: 20,
    fontWeight: 'bold',
  },
  listContent: {
    paddingHorizontal: 10,
    paddingBottom: 20,
  },
  fineCard: {
    backgroundColor: '#fff',
    borderRadius: 8,
    marginVertical: 8,
    overflow: 'hidden',
  },
  fineCardContent: {
    padding: 16,
  },
  fineTop: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  fineAmount: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2c3e50',
  },
  badge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
  },
  badgeText: {
    color: '#fff',
    fontSize: 11,
    fontWeight: '600',
  },
  bookTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#2c3e50',
    marginBottom: 8,
  },
  fineDetails: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  detailText: {
    fontSize: 11,
    color: '#7f8c8d',
  },
  payButton: {
    backgroundColor: '#3498db',
    paddingVertical: 12,
    alignItems: 'center',
  },
  payButtonText: {
    color: '#fff',
    fontWeight: '600',
    fontSize: 14,
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  emptyStateText: {
    fontSize: 16,
    color: '#7f8c8d',
  },
});
