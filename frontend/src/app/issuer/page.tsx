'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { 
  Upload, 
  FileText, 
  CheckCircle, 
  Clock,
  AlertCircle,
  Download,
  Eye,
  Trash2
} from 'lucide-react'
import toast from 'react-hot-toast'

export default function IssuerPortal() {
  const [documents, setDocuments] = useState([
    {
      id: 1,
      name: 'Bachelor Degree - Computer Science',
      type: 'Academic Degree',
      status: 'verified',
      uploadedAt: '2024-01-15',
      size: '2.4 MB'
    },
    {
      id: 2,
      name: 'Professional Certificate - AWS',
      type: 'Certificate',
      status: 'pending',
      uploadedAt: '2024-01-14',
      size: '1.8 MB'
    }
  ])

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      toast.success(`File "${file.name}" uploaded successfully!`)
      // Here you would typically upload to the backend
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'verified':
        return <Badge className="bg-green-100 text-green-800"><CheckCircle className="w-3 h-3 mr-1" />Verified</Badge>
      case 'pending':
        return <Badge className="bg-yellow-100 text-yellow-800"><Clock className="w-3 h-3 mr-1" />Pending</Badge>
      case 'failed':
        return <Badge className="bg-red-100 text-red-800"><AlertCircle className="w-3 h-3 mr-1" />Failed</Badge>
      default:
        return <Badge variant="secondary">{status}</Badge>
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Issuer Portal</h1>
          <p className="text-gray-600">Upload and manage documents, set validation rules, and issue credentials</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Upload Section */}
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Upload className="w-5 h-5 mr-2" />
                  Upload Document
                </CardTitle>
                <CardDescription>
                  Upload a new document for verification and credential issuance
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="document-upload">Select Document</Label>
                  <Input 
                    id="document-upload" 
                    type="file" 
                    accept=".pdf,.jpg,.jpeg,.png" 
                    onChange={handleFileUpload}
                  />
                </div>
                <div>
                  <Label htmlFor="document-type">Document Type</Label>
                  <select className="w-full p-2 border rounded-md">
                    <option>Academic Degree</option>
                    <option>Transcript</option>
                    <option>Certificate</option>
                    <option>ID Document</option>
                    <option>Professional License</option>
                  </select>
                </div>
                <div>
                  <Label htmlFor="recipient-email">Recipient Email</Label>
                  <Input 
                    id="recipient-email" 
                    type="email" 
                    placeholder="recipient@example.com"
                  />
                </div>
                <Button className="w-full">
                  <Upload className="w-4 h-4 mr-2" />
                  Upload and Verify
                </Button>
              </CardContent>
            </Card>

            {/* Quick Stats */}
            <Card className="mt-6">
              <CardHeader>
                <CardTitle>Quick Stats</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Total Documents</span>
                    <span className="font-semibold">{documents.length}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Verified</span>
                    <span className="font-semibold text-green-600">
                      {documents.filter(d => d.status === 'verified').length}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Pending</span>
                    <span className="font-semibold text-yellow-600">
                      {documents.filter(d => d.status === 'pending').length}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Documents List */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <FileText className="w-5 h-5 mr-2" />
                  Document Management
                </CardTitle>
                <CardDescription>
                  View and manage all uploaded documents
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {documents.map((doc) => (
                    <div key={doc.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center space-x-4">
                        <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                          <FileText className="w-5 h-5 text-blue-600" />
                        </div>
                        <div>
                          <h3 className="font-medium text-gray-900">{doc.name}</h3>
                          <p className="text-sm text-gray-500">
                            {doc.type} • {doc.size} • {doc.uploadedAt}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        {getStatusBadge(doc.status)}
                        <Button variant="ghost" size="sm">
                          <Eye className="w-4 h-4" />
                        </Button>
                        <Button variant="ghost" size="sm">
                          <Download className="w-4 h-4" />
                        </Button>
                        <Button variant="ghost" size="sm">
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
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
