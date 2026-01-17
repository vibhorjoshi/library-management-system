import React, { useState, useEffect, useContext } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  Text,
  TouchableOpacity,
  RefreshControl,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { AuthContext } from '../contexts/AuthContext';
import { analyticsAPI, fineAPI } from '../api/client';

export const DashboardScreen = ({ navigation }) => {
  const { user, signOut } = useContext(AuthContext);
  const [analytics, setAnalytics] = useState(null);
  const [fines, setFines] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [analyticsData, finesData] = await Promise.all([
        analyticsAPI.getUserAnalytics(),
        fineAPI.getFines(),
      ]);
      setAnalytics(analyticsData);
      setFines(finesData.results || finesData);
    } catch (error) {
      Alert.alert('Error', 'Failed to load dashboard data');
      console.log('Error loading dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadData();
    setRefreshing(false);
  };

  const handleLogout = () => {
    Alert.alert('Sign Out', 'Are you sure you want to sign out?', [
      { text: 'Cancel' },
      {
        text: 'Sign Out',
        onPress: () => signOut(),
      },
    ]);
  };

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#3498db" />
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      {/* Header */}
      <View style={styles.header}>
        <View>
          <Text style={styles.welcomeText}>Welcome back,</Text>
          <Text style={styles.nameText}>{user?.first_name || 'User'}</Text>
        </View>
        <TouchableOpacity style={styles.logoutBtn} onPress={handleLogout}>
          <Text style={styles.logoutText}>Sign Out</Text>
        </TouchableOpacity>
      </View>

      {/* Analytics Cards */}
      {analytics && (
        <>
          <View style={styles.cardsContainer}>
            <View style={[styles.card, styles.cardBlue]}>
              <Text style={styles.cardLabel}>Total Fines</Text>
              <Text style={styles.cardValue}>
                ₹{analytics.fine_statistics?.total_amount || 0}
              </Text>
            </View>
            <View style={[styles.card, styles.cardGreen]}>
              <Text style={styles.cardLabel}>Paid</Text>
              <Text style={styles.cardValue}>
                ₹{analytics.fine_statistics?.paid_amount || 0}
              </Text>
            </View>
          </View>

          <View style={styles.cardsContainer}>
            <View style={[styles.card, styles.cardRed]}>
              <Text style={styles.cardLabel}>Pending</Text>
              <Text style={styles.cardValue}>
                ₹{analytics.fine_statistics?.pending_amount || 0}
              </Text>
            </View>
            <View style={[styles.card, styles.cardOrange]}>
              <Text style={styles.cardLabel}>Overdue Books</Text>
              <Text style={styles.cardValue}>{analytics.overdue_books || 0}</Text>
            </View>
          </View>
        </>
      )}

      {/* Action Buttons */}
      <View style={styles.actionButtons}>
        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => navigation.navigate('Books')}
        >
          <Text style={styles.actionButtonText}>📚 Browse Books</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => navigation.navigate('Fines')}
        >
          <Text style={styles.actionButtonText}>💰 Pay Fines</Text>
        </TouchableOpacity>
      </View>

      {/* Pending Fines Section */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Pending Fines</Text>
          <TouchableOpacity onPress={() => navigation.navigate('Fines')}>
            <Text style={styles.seeAll}>See All</Text>
          </TouchableOpacity>
        </View>

        {fines.length > 0 ? (
          fines.slice(0, 3).map((fine) => (
            <View key={fine.id} style={styles.fineCard}>
              <View style={styles.fineLeft}>
                <Text style={styles.fineAmount}>₹{fine.amount}</Text>
                <Text style={styles.fineBook}>{fine.issued_book?.book?.title}</Text>
              </View>
              <View
                style={[
                  styles.fineStatus,
                  {
                    backgroundColor: fine.paid ? '#2ecc71' : '#e74c3c',
                  },
                ]}
              >
                <Text style={styles.fineStatusText}>
                  {fine.paid ? 'Paid' : 'Pending'}
                </Text>
              </View>
            </View>
          ))
        ) : (
          <View style={styles.emptyState}>
            <Text style={styles.emptyStateText}>No pending fines! 🎉</Text>
          </View>
        )}
      </View>

      {/* My Books Section */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Currently Issued</Text>
          <TouchableOpacity onPress={() => navigation.navigate('MyBooks')}>
            <Text style={styles.seeAll}>See All</Text>
          </TouchableOpacity>
        </View>
        {analytics?.pending_fines && analytics.pending_fines.length > 0 ? (
          <Text style={styles.emptyStateText}>
            You have {analytics.pending_fines.length} issued books
          </Text>
        ) : (
          <View style={styles.emptyState}>
            <Text style={styles.emptyStateText}>No books issued</Text>
          </View>
        )}
      </View>

      <View style={{ height: 30 }} />
    </ScrollView>
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
    backgroundColor: '#f5f5f5',
  },
  header: {
    backgroundColor: '#2c3e50',
    paddingHorizontal: 20,
    paddingVertical: 20,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  welcomeText: {
    color: '#ecf0f1',
    fontSize: 14,
    marginBottom: 4,
  },
  nameText: {
    color: '#fff',
    fontSize: 24,
    fontWeight: 'bold',
  },
  logoutBtn: {
    backgroundColor: '#e74c3c',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 6,
  },
  logoutText: {
    color: '#fff',
    fontWeight: '600',
    fontSize: 12,
  },
  cardsContainer: {
    flexDirection: 'row',
    paddingHorizontal: 10,
    marginTop: 20,
    gap: 10,
  },
  card: {
    flex: 1,
    borderRadius: 12,
    padding: 16,
    marginHorizontal: 10,
  },
  cardBlue: {
    backgroundColor: '#3498db',
  },
  cardGreen: {
    backgroundColor: '#2ecc71',
  },
  cardRed: {
    backgroundColor: '#e74c3c',
  },
  cardOrange: {
    backgroundColor: '#f39c12',
  },
  cardLabel: {
    color: '#fff',
    fontSize: 12,
    marginBottom: 8,
    opacity: 0.8,
  },
  cardValue: {
    color: '#fff',
    fontSize: 24,
    fontWeight: 'bold',
  },
  actionButtons: {
    flexDirection: 'row',
    paddingHorizontal: 10,
    marginTop: 20,
    gap: 10,
  },
  actionButton: {
    flex: 1,
    backgroundColor: '#3498db',
    borderRadius: 8,
    paddingVertical: 14,
    alignItems: 'center',
  },
  actionButtonText: {
    color: '#fff',
    fontWeight: '600',
    fontSize: 14,
  },
  section: {
    marginTop: 24,
    paddingHorizontal: 20,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2c3e50',
  },
  seeAll: {
    color: '#3498db',
    fontSize: 14,
    fontWeight: '600',
  },
  fineCard: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 16,
    marginBottom: 12,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  fineLeft: {
    flex: 1,
  },
  fineAmount: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2c3e50',
    marginBottom: 4,
  },
  fineBook: {
    fontSize: 12,
    color: '#7f8c8d',
  },
  fineStatus: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
  },
  fineStatusText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
  },
  emptyState: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 24,
    alignItems: 'center',
  },
  emptyStateText: {
    color: '#7f8c8d',
    fontSize: 14,
  },
});
