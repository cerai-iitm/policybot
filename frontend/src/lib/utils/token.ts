export const getToken = () => {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("token");
};