import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  const token = request.cookies.get("token")?.value;
  const isDemoUser = request.cookies.get("isDemoUser")?.value === "true";

  const { pathname } = request.nextUrl;

  const isHome = pathname === "/";
  const isAuthPage = pathname === "/login";
  const isProtected = pathname.startsWith("/notebook");

  if (isHome) {
    return NextResponse.next();
  }

  const isRealUser = token && !isDemoUser;
  const isDemo = token && isDemoUser;

  // 🔒 Allow BOTH demo + real users into notebook
  if (!token && isProtected) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  // 🚫 Only block login for REAL users (not demo)
  if (isRealUser && isAuthPage) {
    return NextResponse.redirect(new URL("/notebook", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/", "/login", "/notebook/:path*"],
};