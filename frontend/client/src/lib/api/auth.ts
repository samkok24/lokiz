import apiClient from './client';
import type {
  AuthResponse,
  RegisterRequest,
  LoginRequest,
  UserProfile,
} from '../types/api';

export const authAPI = {
  // Register
  register: async (data: RegisterRequest): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>('/auth/register', data);
    return response.data;
  },

  // Login
  login: async (data: LoginRequest): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>('/auth/login', data);
    return response.data;
  },

  // Get current user
  getMe: async (): Promise<UserProfile> => {
    const response = await apiClient.get<UserProfile>('/auth/me');
    return response.data;
  },

  // Update profile
  updateProfile: async (data: Partial<UserProfile>): Promise<UserProfile> => {
    const response = await apiClient.patch<UserProfile>('/auth/me', data);
    return response.data;
  },
};

