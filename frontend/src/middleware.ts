import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  const token = request.cookies.get("token")?.value;
  const { pathname } = request.nextUrl;

  const isHome = pathname === "/";
  const isAuthPage = pathname === "/login";
  const isProtected = pathname.startsWith("/notebook");

if (isHome) {
  return NextResponse.next();
}

  // 🔒 Not logged in → block protected routes
  if (!token && isProtected) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  // 🚫 Already logged in → block login page
  if (token && isAuthPage) {
    return NextResponse.redirect(new URL("/notebook", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/", "/login", "/notebook/:path*"],
};