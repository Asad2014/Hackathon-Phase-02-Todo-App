'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useRouter } from 'next/navigation';
import { LayoutDashboard, PlusCircle, LogOut, User } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { ThemeToggle } from '@/components/navigation/theme-toggle';
import { ProfileDropdown } from '@/components/dashboard/profile-dropdown';
import { signOut } from '@/lib/auth';
import { useSession } from '@/lib/auth';

const navItems = [
  { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/dashboard/tasks', label: 'Tasks', icon: PlusCircle },
];

export default function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { data: session } = useSession();

  return (
    <aside className="hidden w-64 border-r bg-muted/40 md:block">
      <div className="flex h-full max-h-screen flex-col gap-2">
        <div className="flex h-14 items-center border-b px-4 lg:h-[60px] lg:px-6">
          <Link href="/" className="flex items-center gap-2 font-semibold">
            <span className="text-lg">Todo App</span>
          </Link>
        </div>
        <div className="flex-1">
          <nav className="grid items-start px-2 text-sm font-medium lg:px-4">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;

              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center gap-3 rounded-lg px-3 py-2 transition-all ${
                    isActive
                      ? 'bg-primary text-primary-foreground'
                      : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </div>
        <div className="mt-auto p-4 border-t">
          <div className="flex flex-col gap-2">
            {session?.user ? (
              <div className="flex items-center justify-between">
                <ProfileDropdown
                  user={{
                    name: session.user.name || session.user.email || 'User',
                    email: session.user.email || ''
                  }}
                />
                <ThemeToggle />
              </div>
            ) : (
              <div className="flex justify-between">
                <ThemeToggle />
              </div>
            )}
            {/* Standalone signout button for logged in users */}
            {session?.user && (
              <div className="pt-2">
                <button
                  onClick={async () => {
                    await signOut();
                    router.push('/sign-in');
                    router.refresh(); // Refresh to ensure the auth state is updated
                  }}
                  className="w-full flex items-center gap-3 rounded-lg px-3 py-2 text-muted-foreground hover:bg-accent hover:text-accent-foreground transition-all"
                >
                  <LogOut className="h-4 w-4" />
                  Sign out
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </aside>
  );
}