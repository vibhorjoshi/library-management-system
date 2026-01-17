import React, { useContext } from 'react';
import { View, ActivityIndicator } from 'react-native';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { AuthProvider, AuthContext } from './src/contexts/AuthContext';
import { RootNavigator } from './src/navigation/RootNavigator';

const RootApp = () => {
  const { isLoading, userToken } = useContext(AuthContext);

  if (isLoading) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ActivityIndicator size="large" color="#3498db" />
      </View>
    );
  }

  return <RootNavigator userToken={userToken} isLoading={isLoading} />;
};

export default function App() {
  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <AuthProvider>
        <RootApp />
      </AuthProvider>
    </GestureHandlerRootView>
  );
}
