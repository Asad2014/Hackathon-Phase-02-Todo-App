import { NextRequest, NextResponse } from 'next/server';

export async function middleware(request: NextRequest) {
  // Define public routes that don't require authentication
  const publicRoutes = ['/sign-in', '/sign-up', '/'];
  const isPublicRoute = publicRoutes.some(route =>
    request.nextUrl.pathname.startsWith(route)
  );

  // Get the session token from cookies
  const token = request.cookies.get('better-auth.session_token')?.value;

  // If user is on a private route but not authenticated, redirect to sign-in
  if (!isPublicRoute && !token) {
    return NextResponse.redirect(new URL('/sign-in', request.url));
  }

  // If user is authenticated and trying to access auth pages, redirect to dashboard
  if (isPublicRoute && token &&
      (request.nextUrl.pathname === '/sign-in' ||
       request.nextUrl.pathname === '/sign-up')) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  return NextResponse.next();
}

// Apply middleware to all routes except static assets
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    {
      source: '/((?!api|_next/static|_next/image|favicon.ico).*)',
      missing: [
        { type: 'header', key: 'next-router-prefetch' },
        { type: 'header', key: 'purpose', value: 'prefetch' },
      ],
    },
  ],
};