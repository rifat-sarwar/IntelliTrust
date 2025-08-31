'use client'

import { useRouter, usePathname } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { 
  Shield, 
  ArrowLeft, 
  Home, 
  FileText, 
  Users, 
  Eye, 
  Settings,
  User,
  LogOut,
  LayoutDashboard,
  Menu,
  X
} from 'lucide-react'
import { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import Link from 'next/link'
// Simplified navigation without dropdown for now

export default function Navigation() {
  const router = useRouter()
  const pathname = usePathname()
  const [canGoBack, setCanGoBack] = useState(false)
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const { user, isAuthenticated, logout } = useAuth()

  // Check if we can go back (not on home page)
  useEffect(() => {
    setCanGoBack(pathname !== '/')
  }, [pathname])

  const handleBack = () => {
    if (canGoBack) {
      router.back()
    } else {
      router.push('/')
    }
  }

  const handleLogout = async () => {
    try {
      await logout()
      router.push('/login')
    } catch (error) {
      console.error('Logout failed:', error)
    }
  }

  const getRoleBasedLinks = () => {
    if (!user) return []

    switch (user.role) {
      case 'admin':
        return [
          { href: '/admin/users', label: 'Users', icon: User },
          { href: '/admin/organizations', label: 'Organizations', icon: Shield },
        ]
      case 'issuer':
        return [
          { href: '/issuer', label: 'Issuer Portal', icon: FileText },
          { href: '/documents', label: 'Documents', icon: FileText },
          { href: '/credentials/issue', label: 'Issue Credentials', icon: Shield },
        ]
      case 'holder':
        return [
          { href: '/holder', label: 'My Credentials', icon: Shield },
          { href: '/documents', label: 'Documents', icon: FileText },
        ]
      case 'verifier':
        return [
          { href: '/verifier', label: 'Verify Documents', icon: Eye },
          { href: '/verifications', label: 'Verification History', icon: Eye },
        ]
      default:
        return []
    }
  }

  const navigationItems = isAuthenticated ? [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    ...getRoleBasedLinks().map(link => ({
      name: link.label,
      href: link.href,
      icon: link.icon
    })),
    { name: 'Settings', href: '/settings', icon: Settings },
  ] : [
    { name: 'Home', href: '/', icon: Home },
    { name: 'Issuer Portal', href: '/issuer', icon: FileText },
    { name: 'Holder Wallet', href: '/holder', icon: Users },
    { name: 'Verifier App', href: '/verifier', icon: Eye },
  ]

  return (
    <header className="bg-white shadow-sm border-b sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          {/* Left side - Logo and Back button */}
          <div className="flex items-center space-x-4">
            {canGoBack && (
              <Button
                variant="ghost"
                size="sm"
                onClick={handleBack}
                className="flex items-center space-x-2"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>Back</span>
              </Button>
            )}
            
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
                <Shield className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">IntelliTrust</h1>
                <p className="text-xs text-gray-500">AI-Driven Document Verification</p>
              </div>
            </div>
          </div>

          {/* Center - Navigation Links */}
          <nav className="hidden md:flex items-center space-x-1">
            {navigationItems.map((item) => {
              const Icon = item.icon
              const isActive = pathname === item.href
              
              return (
                <Button
                  key={item.name}
                  variant={isActive ? "default" : "ghost"}
                  size="sm"
                  onClick={() => router.push(item.href)}
                  className="flex items-center space-x-2"
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.name}</span>
                </Button>
              )
            })}
          </nav>

          {/* Right side - Auth buttons or User menu */}
          <div className="flex items-center space-x-2">
            {isAuthenticated ? (
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-700">
                  {user?.full_name || user?.username}
                </span>
                <Button variant="outline" size="sm" onClick={handleLogout}>
                  <LogOut className="w-4 h-4 mr-1" />
                  Logout
                </Button>
              </div>
            ) : (
              <>
                <Button variant="outline" size="sm" onClick={() => router.push('/login')}>
                  Login
                </Button>
                <Button size="sm" onClick={() => router.push('/register')}>
                  Get Started
                </Button>
              </>
            )}

            {/* Mobile menu button */}
            <div className="md:hidden">
              <button
                onClick={() => setIsMenuOpen(!isMenuOpen)}
                className="text-gray-600 hover:text-gray-900"
              >
                {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="md:hidden">
            <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
              {isAuthenticated ? (
                <>
                  {navigationItems.map((item) => {
                    const Icon = item.icon
                    return (
                      <Button
                        key={item.name}
                        variant="ghost"
                        className="w-full justify-start"
                        onClick={() => {
                          router.push(item.href)
                          setIsMenuOpen(false)
                        }}
                      >
                        <Icon className="w-4 h-4 mr-2" />
                        <span>{item.name}</span>
                      </Button>
                    )
                  })}
                  <Button
                    variant="ghost"
                    className="w-full justify-start text-red-600 hover:text-red-700"
                    onClick={() => {
                      handleLogout()
                      setIsMenuOpen(false)
                    }}
                  >
                    <LogOut className="w-4 h-4 mr-2" />
                    <span>Log out</span>
                  </Button>
                </>
              ) : (
                <>
                  <Button
                    variant="ghost"
                    className="w-full justify-start"
                    onClick={() => {
                      router.push('/login')
                      setIsMenuOpen(false)
                    }}
                  >
                    Login
                  </Button>
                  <Button
                    variant="ghost"
                    className="w-full justify-start"
                    onClick={() => {
                      router.push('/register')
                      setIsMenuOpen(false)
                    }}
                  >
                    Get Started
                  </Button>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </header>
  )
}
