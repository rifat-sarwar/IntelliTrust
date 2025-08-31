'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { 
  Users, 
  QrCode, 
  CheckCircle, 
  Clock,
  Download,
  Share2,
  Eye,
  Lock,
  Unlock
} from 'lucide-react'
import toast from 'react-hot-toast'

export default function HolderWallet() {
  const [credentials, setCredentials] = useState([
    {
      id: 1,
      name: 'Bachelor Degree - Computer Science',
      issuer: 'University of Technology',
      issuedDate: '2024-01-15',
      expiryDate: '2029-01-15',
      status: 'active',
      type: 'Academic Degree',
      shared: false
    },
    {
      id: 2,
      name: 'AWS Solutions Architect',
      issuer: 'Amazon Web Services',
      issuedDate: '2024-01-10',
      expiryDate: '2027-01-10',
      status: 'active',
      type: 'Professional Certificate',
      shared: true
    }
  ])

  const [showQR, setShowQR] = useState<number | null>(null)

  const handleShareCredential = (credentialId: number) => {
    setCredentials(prev => 
      prev.map(cred => 
        cred.id === credentialId 
          ? { ...cred, shared: !cred.shared }
          : cred
      )
    )
    toast.success('Sharing settings updated!')
  }

  const handleGenerateQR = (credentialId: number) => {
    setShowQR(showQR === credentialId ? null : credentialId)
    toast.success('QR Code generated!')
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return <Badge className="bg-green-100 text-green-800"><CheckCircle className="w-3 h-3 mr-1" />Active</Badge>
      case 'expired':
        return <Badge className="bg-red-100 text-red-800"><Clock className="w-3 h-3 mr-1" />Expired</Badge>
      case 'pending':
        return <Badge className="bg-yellow-100 text-yellow-800"><Clock className="w-3 h-3 mr-1" />Pending</Badge>
      default:
        return <Badge variant="secondary">{status}</Badge>
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Holder Wallet</h1>
          <p className="text-gray-600">Manage your verifiable credentials and control sharing permissions</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Wallet Overview */}
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Users className="w-5 h-5 mr-2" />
                  Wallet Overview
                </CardTitle>
                <CardDescription>
                  Your credential statistics and wallet information
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-4">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Total Credentials</span>
                    <span className="font-semibold">{credentials.length}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Active</span>
                    <span className="font-semibold text-green-600">
                      {credentials.filter(c => c.status === 'active').length}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Shared</span>
                    <span className="font-semibold text-blue-600">
                      {credentials.filter(c => c.shared).length}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card className="mt-6">
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button variant="outline" className="w-full">
                  <QrCode className="w-4 h-4 mr-2" />
                  Generate QR Code
                </Button>
                <Button variant="outline" className="w-full">
                  <Download className="w-4 h-4 mr-2" />
                  Export All Credentials
                </Button>
                <Button variant="outline" className="w-full">
                  <Share2 className="w-4 h-4 mr-2" />
                  Share Multiple
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Credentials List */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Users className="w-5 h-5 mr-2" />
                  My Credentials
                </CardTitle>
                <CardDescription>
                  View and manage your verifiable credentials
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {credentials.map((credential) => (
                    <div key={credential.id} className="border rounded-lg p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-2">
                            <h3 className="font-medium text-gray-900">{credential.name}</h3>
                            {getStatusBadge(credential.status)}
                            {credential.shared ? (
                              <Badge className="bg-blue-100 text-blue-800">
                                <Share2 className="w-3 h-3 mr-1" />Shared
                              </Badge>
                            ) : (
                              <Badge className="bg-gray-100 text-gray-800">
                                <Lock className="w-3 h-3 mr-1" />Private
                              </Badge>
                            )}
                          </div>
                          <p className="text-sm text-gray-600 mb-2">
                            Issued by: {credential.issuer}
                          </p>
                          <p className="text-sm text-gray-500">
                            Issued: {credential.issuedDate} • Expires: {credential.expiryDate}
                          </p>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Button 
                            variant="ghost" 
                            size="sm"
                            onClick={() => handleGenerateQR(credential.id)}
                          >
                            <QrCode className="w-4 h-4" />
                          </Button>
                          <Button variant="ghost" size="sm">
                            <Eye className="w-4 h-4" />
                          </Button>
                          <Button variant="ghost" size="sm">
                            <Download className="w-4 h-4" />
                          </Button>
                          <Button 
                            variant="ghost" 
                            size="sm"
                            onClick={() => handleShareCredential(credential.id)}
                          >
                            {credential.shared ? <Lock className="w-4 h-4" /> : <Unlock className="w-4 h-4" />}
                          </Button>
                        </div>
                      </div>
                      
                      {/* QR Code Display */}
                      {showQR === credential.id && (
                        <div className="mt-4 p-4 bg-gray-50 rounded-lg text-center">
                          <div className="w-32 h-32 mx-auto bg-white border rounded-lg flex items-center justify-center">
                            <QrCode className="w-16 h-16 text-gray-400" />
                          </div>
                          <p className="text-sm text-gray-600 mt-2">
                            QR Code for {credential.name}
                          </p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
