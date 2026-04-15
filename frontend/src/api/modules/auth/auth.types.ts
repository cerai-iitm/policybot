export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
}

export interface RegisterRequest {
  email: string
  password: string
  full_name: string
}

export interface UserRead {
  id: number | string
  email: string
  is_active: boolean
  is_verified: boolean
  full_name?: string
}