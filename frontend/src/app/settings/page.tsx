'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Switch } from '@/components/ui/switch'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  User, 
  Shield, 
  Bell, 
  Key,
  Globe,
  Download,
  Trash2,
  Save,
  Eye,
  EyeOff
} from 'lucide-react'
import toast from 'react-hot-toast'

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState('profile')
  const [showPassword, setShowPassword] = useState(false)
  const [settings, setSettings] = useState({
    profile: {
      fullName: 'John Doe',
      email: 'john.doe@example.com',
      phone: '+1 (555) 123-4567',
      organization: 'University of Technology'
    },
    security: {
      twoFactorEnabled: true,
      emailNotifications: true,
      sessionTimeout: 30,
      passwordLastChanged: '2024-01-15'
    },
    notifications: {
      documentUploads: true,
      verifications: true,
      blockchainUpdates: true,
      securityAlerts: true,
      emailDigest: false
    },
    preferences: {
      language: 'en',
      timezone: 'UTC',
      dateFormat: 'MM/DD/YYYY',
      theme: 'light'
    }
  })

  const handleSaveProfile = () => {
    toast.success('Profile updated successfully!')
  }

  const handleChangePassword = () => {
    toast.success('Password change request sent!')
  }

  const handleToggleTwoFactor = () => {
    setSettings(prev => ({
      ...prev,
      security: {
        ...prev.security,
        twoFactorEnabled: !prev.security.twoFactorEnabled
      }
    }))
    toast.success(`Two-factor authentication ${settings.security.twoFactorEnabled ? 'disabled' : 'enabled'}!`)
  }

  const handleExportData = () => {
    toast.success('Data export started! Check your email.')
  }

  const handleDeleteAccount = () => {
    if (confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
      toast.success('Account deletion request submitted!')
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Settings</h1>
          <p className="text-gray-600">Manage your account settings and preferences</p>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="profile">Profile</TabsTrigger>
            <TabsTrigger value="security">Security</TabsTrigger>
            <TabsTrigger value="notifications">Notifications</TabsTrigger>
            <TabsTrigger value="preferences">Preferences</TabsTrigger>
          </TabsList>

          {/* Profile Settings */}
          <TabsContent value="profile" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <User className="w-5 h-5 mr-2" />
                  Profile Information
                </CardTitle>
                <CardDescription>
                  Update your personal information and contact details
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="fullName">Full Name</Label>
                    <Input 
                      id="fullName" 
                      value={settings.profile.fullName}
                      onChange={(e) => setSettings(prev => ({
                        ...prev,
                        profile: { ...prev.profile, fullName: e.target.value }
                      }))}
                    />
                  </div>
                  <div>
                    <Label htmlFor="email">Email Address</Label>
                    <Input 
                      id="email" 
                      type="email" 
                      value={settings.profile.email}
                      onChange={(e) => setSettings(prev => ({
                        ...prev,
                        profile: { ...prev.profile, email: e.target.value }
                      }))}
                    />
                  </div>
                  <div>
                    <Label htmlFor="phone">Phone Number</Label>
                    <Input 
                      id="phone" 
                      value={settings.profile.phone}
                      onChange={(e) => setSettings(prev => ({
                        ...prev,
                        profile: { ...prev.profile, phone: e.target.value }
                      }))}
                    />
                  </div>
                  <div>
                    <Label htmlFor="organization">Organization</Label>
                    <Input 
                      id="organization" 
                      value={settings.profile.organization}
                      onChange={(e) => setSettings(prev => ({
                        ...prev,
                        profile: { ...prev.profile, organization: e.target.value }
                      }))}
                    />
                  </div>
                </div>
                <Button onClick={handleSaveProfile}>
                  <Save className="w-4 h-4 mr-2" />
                  Save Changes
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Security Settings */}
          <TabsContent value="security" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Shield className="w-5 h-5 mr-2" />
                  Security Settings
                </CardTitle>
                <CardDescription>
                  Manage your account security and authentication
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Two-Factor Authentication */}
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-medium">Two-Factor Authentication</h3>
                    <p className="text-sm text-gray-600">
                      Add an extra layer of security to your account
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Switch 
                      checked={settings.security.twoFactorEnabled}
                      onCheckedChange={handleToggleTwoFactor}
                    />
                    <Badge variant={settings.security.twoFactorEnabled ? "default" : "secondary"}>
                      {settings.security.twoFactorEnabled ? "Enabled" : "Disabled"}
                    </Badge>
                  </div>
                </div>

                {/* Password Change */}
                <div className="space-y-4">
                  <h3 className="font-medium">Change Password</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <Label htmlFor="currentPassword">Current Password</Label>
                      <div className="relative">
                        <Input 
                          id="currentPassword" 
                          type={showPassword ? "text" : "password"}
                        />
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                          onClick={() => setShowPassword(!showPassword)}
                        >
                          {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                        </Button>
                      </div>
                    </div>
                    <div>
                      <Label htmlFor="newPassword">New Password</Label>
                      <Input 
                        id="newPassword" 
                        type="password"
                      />
                    </div>
                    <div>
                      <Label htmlFor="confirmPassword">Confirm Password</Label>
                      <Input 
                        id="confirmPassword" 
                        type="password"
                      />
                    </div>
                  </div>
                  <Button onClick={handleChangePassword}>
                    <Key className="w-4 h-4 mr-2" />
                    Change Password
                  </Button>
                </div>

                {/* Session Management */}
                <div className="space-y-4">
                  <h3 className="font-medium">Session Management</h3>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600">Session timeout</p>
                      <p className="text-xs text-gray-500">Automatically log out after inactivity</p>
                    </div>
                    <select 
                      className="p-2 border rounded-md"
                      value={settings.security.sessionTimeout}
                      onChange={(e) => setSettings(prev => ({
                        ...prev,
                        security: { ...prev.security, sessionTimeout: parseInt(e.target.value) }
                      }))}
                    >
                      <option value={15}>15 minutes</option>
                      <option value={30}>30 minutes</option>
                      <option value={60}>1 hour</option>
                      <option value={120}>2 hours</option>
                    </select>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Notification Settings */}
          <TabsContent value="notifications" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Bell className="w-5 h-5 mr-2" />
                  Notification Preferences
                </CardTitle>
                <CardDescription>
                  Choose what notifications you want to receive
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-medium">Document Uploads</h3>
                      <p className="text-sm text-gray-600">Get notified when documents are uploaded</p>
                    </div>
                                         <Switch 
                       checked={settings.notifications.documentUploads}
                       onCheckedChange={(checked: boolean) => setSettings(prev => ({
                         ...prev,
                         notifications: { ...prev.notifications, documentUploads: checked }
                       }))}
                     />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-medium">Verifications</h3>
                      <p className="text-sm text-gray-600">Get notified about verification requests</p>
                    </div>
                                         <Switch 
                       checked={settings.notifications.verifications}
                       onCheckedChange={(checked: boolean) => setSettings(prev => ({
                         ...prev,
                         notifications: { ...prev.notifications, verifications: checked }
                       }))}
                     />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-medium">Blockchain Updates</h3>
                      <p className="text-sm text-gray-600">Get notified about blockchain transactions</p>
                    </div>
                                         <Switch 
                       checked={settings.notifications.blockchainUpdates}
                       onCheckedChange={(checked: boolean) => setSettings(prev => ({
                         ...prev,
                         notifications: { ...prev.notifications, blockchainUpdates: checked }
                       }))}
                     />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-medium">Security Alerts</h3>
                      <p className="text-sm text-gray-600">Get notified about security events</p>
                    </div>
                                         <Switch 
                       checked={settings.notifications.securityAlerts}
                       onCheckedChange={(checked: boolean) => setSettings(prev => ({
                         ...prev,
                         notifications: { ...prev.notifications, securityAlerts: checked }
                       }))}
                     />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-medium">Email Digest</h3>
                      <p className="text-sm text-gray-600">Receive daily email summaries</p>
                    </div>
                                         <Switch 
                       checked={settings.notifications.emailDigest}
                       onCheckedChange={(checked: boolean) => setSettings(prev => ({
                         ...prev,
                         notifications: { ...prev.notifications, emailDigest: checked }
                       }))}
                     />
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Preferences */}
          <TabsContent value="preferences" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Globe className="w-5 h-5 mr-2" />
                  Application Preferences
                </CardTitle>
                <CardDescription>
                  Customize your application experience
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="language">Language</Label>
                    <select 
                      id="language"
                      className="w-full p-2 border rounded-md"
                      value={settings.preferences.language}
                      onChange={(e) => setSettings(prev => ({
                        ...prev,
                        preferences: { ...prev.preferences, language: e.target.value }
                      }))}
                    >
                      <option value="en">English</option>
                      <option value="es">Spanish</option>
                      <option value="fr">French</option>
                      <option value="de">German</option>
                    </select>
                  </div>
                  <div>
                    <Label htmlFor="timezone">Timezone</Label>
                    <select 
                      id="timezone"
                      className="w-full p-2 border rounded-md"
                      value={settings.preferences.timezone}
                      onChange={(e) => setSettings(prev => ({
                        ...prev,
                        preferences: { ...prev.preferences, timezone: e.target.value }
                      }))}
                    >
                      <option value="UTC">UTC</option>
                      <option value="EST">Eastern Time</option>
                      <option value="PST">Pacific Time</option>
                      <option value="GMT">GMT</option>
                    </select>
                  </div>
                  <div>
                    <Label htmlFor="dateFormat">Date Format</Label>
                    <select 
                      id="dateFormat"
                      className="w-full p-2 border rounded-md"
                      value={settings.preferences.dateFormat}
                      onChange={(e) => setSettings(prev => ({
                        ...prev,
                        preferences: { ...prev.preferences, dateFormat: e.target.value }
                      }))}
                    >
                      <option value="MM/DD/YYYY">MM/DD/YYYY</option>
                      <option value="DD/MM/YYYY">DD/MM/YYYY</option>
                      <option value="YYYY-MM-DD">YYYY-MM-DD</option>
                    </select>
                  </div>
                  <div>
                    <Label htmlFor="theme">Theme</Label>
                    <select 
                      id="theme"
                      className="w-full p-2 border rounded-md"
                      value={settings.preferences.theme}
                      onChange={(e) => setSettings(prev => ({
                        ...prev,
                        preferences: { ...prev.preferences, theme: e.target.value }
                      }))}
                    >
                      <option value="light">Light</option>
                      <option value="dark">Dark</option>
                      <option value="auto">Auto</option>
                    </select>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Data Management */}
            <Card>
              <CardHeader>
                <CardTitle>Data Management</CardTitle>
                <CardDescription>
                  Export your data or delete your account
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-medium">Export Data</h3>
                    <p className="text-sm text-gray-600">Download all your data in JSON format</p>
                  </div>
                  <Button variant="outline" onClick={handleExportData}>
                    <Download className="w-4 h-4 mr-2" />
                    Export Data
                  </Button>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-medium text-red-600">Delete Account</h3>
                    <p className="text-sm text-gray-600">Permanently delete your account and all data</p>
                  </div>
                  <Button variant="destructive" onClick={handleDeleteAccount}>
                    <Trash2 className="w-4 h-4 mr-2" />
                    Delete Account
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
