// frontend/src/utils/api.ts
import axios, { AxiosHeaders } from "axios";


const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "http://localhost:8000",
});

/* ================================
   Request interceptor
================================ */
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("innovo_auth_token");

  if (token) {
    // Axios v1 compliant headers
    const headers = AxiosHeaders.from(config.headers);
    headers.set("Authorization", `Bearer ${token}`);
    config.headers = headers;
  }

  return config;
});




/* ================================
   Response interceptor
================================ */
apiClient.interceptors.response.use(
  (response) => response.data, // 🔴 IMPORTANT
  (error) => {
    if (error?.response?.status === 401) {
      localStorage.removeItem("innovo_auth_token");
      window.location.replace("/login");
    }
    return Promise.reject(error);
  }
);

/* ================================
   Typed helpers (RETURN T, NOT AxiosResponse)
================================ */
export const apiGet = <T>(url: string): Promise<T> =>
  apiClient.get(url);

export const apiPost = <T>(
  url: string,
  data?: unknown
): Promise<T> => apiClient.post(url, data);

export const apiPut = <T>(
  url: string,
  data?: unknown
): Promise<T> => apiClient.put(url, data);

export const apiDelete = <T>(url: string): Promise<T> =>
  apiClient.delete(url);

/* ================================
   Multipart upload helper
================================ */
export const apiUploadFiles = async <T>(
  url: string,
  files: File[]
): Promise<T> => {
  const formData = new FormData();

  files.forEach((file) => {
    formData.append("files", file); // MUST be "files"
  });

  return apiClient.post(url, formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
};

