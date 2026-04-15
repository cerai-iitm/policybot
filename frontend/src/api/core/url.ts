export const BASE_PATH = process.env.NEXT_PUBLIC_BASE_PATH ?? "/policybot";

export function withBase(p: string): string {
  if (!p.startsWith("/")) {
    p = "/" + p;
  }
  if (!BASE_PATH) {
    return p;
  }
  if (BASE_PATH.endsWith("/")) {
    return `${BASE_PATH.slice(0, -1)}${p}`;
  }
  return `${BASE_PATH}${p}`;
}
