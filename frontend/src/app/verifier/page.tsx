'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { 
  Eye, 
  QrCode, 
  CheckCircle, 
  XCircle,
  Upload,
  Camera,
  BarChart3,
  Download,
  Share2
} from 'lucide-react'
import toast from 'react-hot-toast'

export default function VerifierApp() {
  const [scanMode, setScanMode] = useState<'qr' | 'upload'>('qr')
  const [verificationHistory, setVerificationHistory] = useState([
    {
      id: 1,
      documentName: 'Bachelor Degree - Computer Science',
      issuer: 'University of Technology',
      verifiedAt: '2024-01-15 14:30',
      status: 'verified',
      holder: 'John Doe',
      type: 'Academic Degree'
    },
    {
      id: 2,
      documentName: 'AWS Solutions Architect',
      issuer: 'Amazon Web Services',
      verifiedAt: '2024-01-14 09:15',
      status: 'verified',
      holder: 'Jane Smith',
      type: 'Professional Certificate'
    }
  ])

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      toast.success(`File "${file.name}" uploaded for verification!`)
      // Here you would typically send to backend for verification
    }
  }

  const handleScanQR = () => {
    toast.success('QR Code scanning initiated!')
    // Here you would typically open camera for QR scanning
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'verified':
        return <Badge className="bg-green-100 text-green-800"><CheckCircle className="w-3 h-3 mr-1" />Verified</Badge>
      case 'invalid':
        return <Badge className="bg-red-100 text-red-800"><XCircle className="w-3 h-3 mr-1" />Invalid</Badge>
      case 'pending':
        return <Badge className="bg-yellow-100 text-yellow-800">Pending</Badge>
      default:
        return <Badge variant="secondary">{status}</Badge>
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Verifier App</h1>
          <p className="text-gray-600">Scan QR codes and verify document authenticity instantly</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Verification Interface */}
          <div>
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Eye className="w-5 h-5 mr-2" />
                  Document Verification
                </CardTitle>
                <CardDescription>
                  Choose your verification method
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Method Selection */}
                <div className="flex space-x-2">
                  <Button
                    variant={scanMode === 'qr' ? 'default' : 'outline'}
                    onClick={() => setScanMode('qr')}
                    className="flex-1"
                  >
                    <QrCode className="w-4 h-4 mr-2" />
                    Scan QR Code
                  </Button>
                  <Button
                    variant={scanMode === 'upload' ? 'default' : 'outline'}
                    onClick={() => setScanMode('upload')}
                    className="flex-1"
                  >
                    <Upload className="w-4 h-4 mr-2" />
                    Upload Image
                  </Button>
                </div>

                {/* QR Code Scanner */}
                {scanMode === 'qr' && (
                  <div className="text-center">
                    <div className="w-64 h-64 mx-auto border-2 border-dashed border-gray-300 rounded-lg flex items-center justify-center bg-gray-50">
                      <div className="text-center">
                        <Camera className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                        <p className="text-gray-600 mb-2">Camera Scanner</p>
                        <p className="text-sm text-gray-500 mb-4">Point camera at QR code</p>
                        <Button onClick={handleScanQR}>
                          <Camera className="w-4 h-4 mr-2" />
                          Start Scanning
                        </Button>
                      </div>
                    </div>
                  </div>
                )}

                {/* File Upload */}
                {scanMode === 'upload' && (
                  <div className="text-center">
                    <div className="w-64 h-64 mx-auto border-2 border-dashed border-gray-300 rounded-lg flex items-center justify-center bg-gray-50">
                      <div className="text-center">
                        <Upload className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                        <p className="text-gray-600 mb-2">Upload Document</p>
                        <p className="text-sm text-gray-500 mb-4">Drag & drop or click to browse</p>
                        <Input
                          type="file"
                          accept=".pdf,.jpg,.jpeg,.png"
                          onChange={handleFileUpload}
                          className="max-w-xs mx-auto"
                        />
                      </div>
                    </div>
                  </div>
                )}

                {/* Manual Entry */}
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium">Or enter document ID manually</label>
                    <Input placeholder="Enter document ID or URL" />
                  </div>
                  <Button className="w-full">
                    <Eye className="w-4 h-4 mr-2" />
                    Verify Document
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Quick Stats */}
            <Card className="mt-6">
              <CardHeader>
                <CardTitle>Verification Stats</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">
                      {verificationHistory.filter(v => v.status === 'verified').length}
                    </div>
                    <div className="text-sm text-gray-600">Verified</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-red-600">
                      {verificationHistory.filter(v => v.status === 'invalid').length}
                    </div>
                    <div className="text-sm text-gray-600">Invalid</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Verification History */}
          <div>
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <BarChart3 className="w-5 h-5 mr-2" />
                  Verification History
                </CardTitle>
                <CardDescription>
                  Recent document verifications
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {verificationHistory.map((verification) => (
                    <div key={verification.id} className="border rounded-lg p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-2">
                            <h3 className="font-medium text-gray-900">{verification.documentName}</h3>
                            {getStatusBadge(verification.status)}
                          </div>
                          <p className="text-sm text-gray-600 mb-1">
                            Issuer: {verification.issuer}
                          </p>
                          <p className="text-sm text-gray-500 mb-2">
                            Holder: {verification.holder} • Type: {verification.type}
                          </p>
                          <p className="text-xs text-gray-400">
                            Verified: {verification.verifiedAt}
                          </p>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Button variant="ghost" size="sm">
                            <Eye className="w-4 h-4" />
                          </Button>
                          <Button variant="ghost" size="sm">
                            <Download className="w-4 h-4" />
                          </Button>
                          <Button variant="ghost" size="sm">
                            <Share2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                
                <div className="mt-4 text-center">
                  <Button variant="outline">
                    <BarChart3 className="w-4 h-4 mr-2" />
                    View Full History
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
