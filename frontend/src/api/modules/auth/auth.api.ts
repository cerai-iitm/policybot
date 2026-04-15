import { apiClient, buildUrl } from "../../core/client"
import { LoginRequest, LoginResponse, RegisterRequest, UserRead } from "./auth.types"

export const authApi = {
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    const res = await apiClient.post<LoginResponse>(
      buildUrl("/auth/login"),
      data
    )

    if (res.data?.access_token) {
      localStorage.setItem("jwt", res.data.access_token)
    }

    return res.data
  },

  register: async (data: RegisterRequest): Promise<UserRead> => {
    const res = await apiClient.post<UserRead>(
      buildUrl("/auth/register"),
      data
    )
    return res.data
  },

  logout: async () => {
    await apiClient.post(buildUrl("/auth/logout"))
    localStorage.removeItem("jwt")
  },
}