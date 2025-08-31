'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { 
  Upload, 
  Shield, 
  CheckCircle, 
  FileText, 
  Users, 
  BarChart3,
  Eye,
  QrCode,
  Lock,
  Brain
} from 'lucide-react'
import toast from 'react-hot-toast'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'

export default function Home() {
  const [activeTab, setActiveTab] = useState('issuer')
  const router = useRouter()
  const { user, isAuthenticated, loading } = useAuth()

  useEffect(() => {
    if (!loading && isAuthenticated) {
      router.push('/dashboard')
    }
  }, [isAuthenticated, loading, router])

  const handleGetStarted = () => {
    router.push('/register')
  }

  const handleUploadDocument = () => {
    router.push('/login')
  }

  const handleVerifyDocument = () => {
    router.push('/login')
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  if (isAuthenticated) {
    return null // Will redirect to dashboard
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Hero Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-4xl font-bold text-gray-900 mb-6">
              Secure Document Lifecycle Management
            </h2>
            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
              AI-powered verification, blockchain-backed security, and seamless document management 
              for academic credentials, healthcare records, and financial documents.
            </p>
            <div className="flex justify-center space-x-4">
              <Button size="lg" className="bg-blue-600 hover:bg-blue-700" onClick={handleUploadDocument}>
                <Upload className="w-5 h-5 mr-2" />
                Upload Document
              </Button>
              <Button size="lg" variant="outline" onClick={handleVerifyDocument}>
                <Eye className="w-5 h-5 mr-2" />
                Verify Document
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h3 className="text-3xl font-bold text-gray-900 mb-4">
              Why Choose IntelliTrust?
            </h3>
            <p className="text-lg text-gray-600">
              Advanced AI analysis combined with blockchain security
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <Card>
              <CardHeader>
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                  <Brain className="w-6 h-6 text-blue-600" />
                </div>
                <CardTitle>AI Gatekeeper</CardTitle>
                <CardDescription>
                  Advanced document analysis with forensic checks, template validation, and content verification
                </CardDescription>
              </CardHeader>
            </Card>

            <Card>
              <CardHeader>
                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
                  <Lock className="w-6 h-6 text-green-600" />
                </div>
                <CardTitle>Blockchain Security</CardTitle>
                <CardDescription>
                  Immutable record of verified document hashes with Hyperledger Fabric integration
                </CardDescription>
              </CardHeader>
            </Card>

            <Card>
              <CardHeader>
                <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                  <CheckCircle className="w-6 h-6 text-purple-600" />
                </div>
                <CardTitle>Instant Verification</CardTitle>
                <CardDescription>
                  QR code scanning and real-time verification with comprehensive audit trails
                </CardDescription>
              </CardHeader>
            </Card>
          </div>
        </div>
      </section>

      {/* Platform Access Section */}
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h3 className="text-3xl font-bold text-gray-900 mb-4">
              Platform Access
            </h3>
            <p className="text-lg text-gray-600">
              Choose your role and start using IntelliTrust
            </p>
          </div>

          <Tabs value={activeTab} onValueChange={setActiveTab} className="max-w-4xl mx-auto">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="issuer">Issuer Portal</TabsTrigger>
              <TabsTrigger value="holder">Holder Wallet</TabsTrigger>
              <TabsTrigger value="verifier">Verifier App</TabsTrigger>
            </TabsList>

            <TabsContent value="issuer" className="mt-8">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <FileText className="w-5 h-5 mr-2" />
                    Issuer Portal
                  </CardTitle>
                  <CardDescription>
                    Upload and verify documents, set validation rules, and manage credentials
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="document-upload">Upload Document</Label>
                      <Input id="document-upload" type="file" accept=".pdf,.jpg,.jpeg,.png" />
                    </div>
                    <div>
                      <Label htmlFor="document-type">Document Type</Label>
                      <select className="w-full p-2 border rounded-md">
                        <option>Academic Degree</option>
                        <option>Transcript</option>
                        <option>Certificate</option>
                        <option>ID Document</option>
                      </select>
                    </div>
                  </div>
                  <Button className="w-full" onClick={() => router.push('/issuer')}>
                    <Upload className="w-4 h-4 mr-2" />
                    Go to Issuer Portal
                  </Button>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="holder" className="mt-8">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Users className="w-5 h-5 mr-2" />
                    Holder Wallet
                  </CardTitle>
                  <CardDescription>
                    Manage your verifiable credentials and control sharing permissions
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label>My Credentials</Label>
                      <div className="p-4 border rounded-md bg-gray-50">
                        <p className="text-sm text-gray-600">No credentials yet</p>
                      </div>
                    </div>
                    <div>
                      <Label>Recent Activity</Label>
                      <div className="p-4 border rounded-md bg-gray-50">
                        <p className="text-sm text-gray-600">No recent activity</p>
                      </div>
                    </div>
                  </div>
                  <Button variant="outline" className="w-full" onClick={() => router.push('/holder')}>
                    <QrCode className="w-4 h-4 mr-2" />
                    Go to Holder Wallet
                  </Button>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="verifier" className="mt-8">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Eye className="w-5 h-5 mr-2" />
                    Verifier App
                  </CardTitle>
                  <CardDescription>
                    Scan QR codes and verify document authenticity instantly
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="text-center">
                    <div className="w-64 h-64 mx-auto border-2 border-dashed border-gray-300 rounded-lg flex items-center justify-center">
                      <div className="text-center">
                        <QrCode className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                        <p className="text-gray-600">Scan QR Code</p>
                        <p className="text-sm text-gray-500">or</p>
                        <Button variant="outline" size="sm" className="mt-2">
                          Upload Image
                        </Button>
                      </div>
                    </div>
                  </div>
                  <div className="text-center">
                    <Button variant="outline" onClick={() => router.push('/verifier')}>
                      <BarChart3 className="w-4 h-4 mr-2" />
                      Go to Verifier App
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <h4 className="text-lg font-semibold mb-4">IntelliTrust</h4>
              <p className="text-gray-400 text-sm">
                AI-driven, blockchain-backed platform for secure document lifecycle management.
              </p>
            </div>
            <div>
              <h5 className="font-semibold mb-4">Platform</h5>
              <ul className="space-y-2 text-sm text-gray-400">
                <li>Issuer Portal</li>
                <li>Holder Wallet</li>
                <li>Verifier App</li>
                <li>API Documentation</li>
              </ul>
            </div>
            <div>
              <h5 className="font-semibold mb-4">Support</h5>
              <ul className="space-y-2 text-sm text-gray-400">
                <li>Documentation</li>
                <li>API Reference</li>
                <li>Contact Support</li>
                <li>Status Page</li>
              </ul>
            </div>
            <div>
              <h5 className="font-semibold mb-4">Legal</h5>
              <ul className="space-y-2 text-sm text-gray-400">
                <li>Privacy Policy</li>
                <li>Terms of Service</li>
                <li>Security</li>
                <li>Compliance</li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-sm text-gray-400">
            <p>&copy; 2024 IntelliTrust. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
