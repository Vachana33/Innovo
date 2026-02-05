import axios from "axios";

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "http://localhost:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("innovo_auth_token");

  if (token) {
    (config.headers as any)["Authorization"] = `Bearer ${token}`;
  }

  return config;
});

apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error?.response?.status === 401) {
      localStorage.removeItem("innovo_auth_token");
      window.location.replace("/login");
    }
    return Promise.reject(error);
  }
);

export const apiGet = <T>(url: string) => apiClient.get<T, T>(url);
export const apiPost = <T>(url: string, data: unknown) =>
  apiClient.post<T, T>(url, data);
export const apiPut = <T>(url: string, data: unknown) =>
  apiClient.put<T, T>(url, data);
export const apiDelete = <T>(url: string) => apiClient.delete<T, T>(url);
