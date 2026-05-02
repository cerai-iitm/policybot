export interface RegisterPayload {
  email: string;
  password: string;
  full_name: string;
  username: string;
}

export interface LoginPayload {
  username: string;
  password: string;
}

export interface User {
  id: number;
  email: string;
  username: string;
  full_name: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}