import client from './client'

export interface RegisterData {
  username: string
  email: string
  password: string
}

export interface LoginData {
  username: string
  password: string
  remember_me?: boolean
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface UserResponse {
  id: string
  username: string
  email: string
  is_active: boolean
  last_login: string | null
  created_at: string
  updated_at: string
}

export const authAPI = {
  register: (data: RegisterData) =>
    client.post<UserResponse>('/api/v1/auth/register', data),

  login: (data: LoginData) =>
    client.post<TokenResponse>('/api/v1/auth/login', data),

  logout: () =>
    client.post('/api/v1/auth/logout'),

  getCurrentUser: () =>
    client.get<UserResponse>('/api/v1/auth/me'),

  refreshToken: (refreshToken: string) =>
    client.post<TokenResponse>('/api/v1/auth/refresh', { refresh_token: refreshToken }),

  changePassword: (oldPassword: string, newPassword: string) =>
    client.post('/api/v1/auth/change-password', {
      old_password: oldPassword,
      new_password: newPassword,
    }),
}
