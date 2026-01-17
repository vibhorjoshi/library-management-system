import React, { createContext, useReducer, useEffect, useCallback } from 'react';
import * as SecureStore from 'expo-secure-store';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { authAPI } from '../api/client';

export const AuthContext = createContext();

const initialState = {
  isLoading: true,
  isSignout: false,
  userToken: null,
  user: null,
  error: null,
};

const reducer = (state, action) => {
  switch (action.type) {
    case 'RESTORE_TOKEN':
      return {
        ...state,
        userToken: action.payload.token,
        user: action.payload.user,
        isLoading: false,
      };
    case 'SIGN_IN':
      return {
        ...state,
        isSignout: false,
        userToken: action.payload.token,
        user: action.payload.user,
        error: null,
      };
    case 'SIGN_UP':
      return {
        ...state,
        isSignout: false,
        userToken: action.payload.token,
        user: action.payload.user,
        error: null,
      };
    case 'SIGN_OUT':
      return {
        ...state,
        isSignout: true,
        userToken: null,
        user: null,
        error: null,
      };
    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload,
      };
    case 'CLEAR_ERROR':
      return {
        ...state,
        error: null,
      };
    case 'UPDATE_USER':
      return {
        ...state,
        user: { ...state.user, ...action.payload },
      };
    default:
      return state;
  }
};

export const AuthProvider = ({ children }) => {
  const [state, dispatch] = useReducer(reducer, initialState);

  // Restore token on app launch
  useEffect(() => {
    const bootstrapAsync = async () => {
      try {
        const token = await SecureStore.getItemAsync('userToken');
        const userData = await AsyncStorage.getItem('userData');
        
        if (token && userData) {
          dispatch({
            type: 'RESTORE_TOKEN',
            payload: {
              token,
              user: JSON.parse(userData),
            },
          });
        } else {
          dispatch({ type: 'RESTORE_TOKEN', payload: { token: null, user: null } });
        }
      } catch (e) {
        console.log('Failed to restore token:', e);
        dispatch({ type: 'RESTORE_TOKEN', payload: { token: null, user: null } });
      }
    };

    bootstrapAsync();
  }, []);

  const authContext = {
    signIn: useCallback(async (email, password) => {
      try {
        const { token, user } = await authAPI.login(email, password);
        dispatch({
          type: 'SIGN_IN',
          payload: { token, user },
        });
        return { success: true };
      } catch (error) {
        const errorMessage = error.response?.data?.detail || 'Login failed';
        dispatch({
          type: 'SET_ERROR',
          payload: errorMessage,
        });
        return { success: false, error: errorMessage };
      }
    }, []),

    signUp: useCallback(async (email, password, firstName, lastName, userType) => {
      try {
        const { token, user } = await authAPI.register(
          email,
          password,
          firstName,
          lastName,
          userType
        );
        dispatch({
          type: 'SIGN_UP',
          payload: { token, user },
        });
        return { success: true };
      } catch (error) {
        const errorMessage = error.response?.data?.detail || 'Registration failed';
        dispatch({
          type: 'SET_ERROR',
          payload: errorMessage,
        });
        return { success: false, error: errorMessage };
      }
    }, []),

    signOut: useCallback(async () => {
      try {
        await authAPI.logout();
        dispatch({ type: 'SIGN_OUT' });
      } catch (error) {
        console.log('Logout error:', error);
      }
    }, []),

    clearError: useCallback(() => {
      dispatch({ type: 'CLEAR_ERROR' });
    }, []),

    updateUser: useCallback(async (userData) => {
      dispatch({
        type: 'UPDATE_USER',
        payload: userData,
      });
      await AsyncStorage.setItem('userData', JSON.stringify(userData));
    }, []),
  };

  return (
    <AuthContext.Provider value={{ ...state, ...authContext }}>
      {children}
    </AuthContext.Provider>
  );
};
