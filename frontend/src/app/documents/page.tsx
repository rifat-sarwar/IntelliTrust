'use client'

import { useState, useEffect } from 'react';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useAuth } from '@/contexts/AuthContext';
import { apiClient, Document, AIAnalysisResponse } from '@/lib/api';
import { 
  FileText, 
  Upload, 
  Search, 
  Eye,
  Shield,
  CheckCircle,
  Clock,
  AlertCircle,
  RefreshCw,
  BarChart3,
  QrCode
} from 'lucide-react';
import toast from 'react-hot-toast';

interface DocumentWithAnalysis extends Document {
  ai_analysis?: AIAnalysisResponse;
}

export default function DocumentsPage() {
  const { user: currentUser } = useAuth();
  const [documents, setDocuments] = useState<DocumentWithAnalysis[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [documentTypeFilter, setDocumentTypeFilter] = useState<string>('all');
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadForm, setUploadForm] = useState({
    title: '',
    description: '',
    document_type: 'other'
  });

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      const response = await apiClient.getDocuments({ limit: 100 });
      
      const docsWithAnalysis = await Promise.all(
        (response.items || []).map(async (doc) => {
          try {
            const analysis = await apiClient.getAnalysisResults(doc.id);
            return { ...doc, ai_analysis: analysis };
          } catch (error) {
            return doc;
          }
        })
      );
      setDocuments(docsWithAnalysis);
    } catch (error) {
      console.error('Error loading documents:', error);
      toast.error('Failed to load documents');
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      if (!uploadForm.title) {
        setUploadForm(prev => ({ ...prev, title: file.name }));
      }
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      toast.error('Please select a file');
      return;
    }

    try {
      setUploading(true);
      await apiClient.uploadDocument({
        file: selectedFile,
        title: uploadForm.title || selectedFile.name,
        description: uploadForm.description,
        document_type: uploadForm.document_type
      });

      toast.success('Document uploaded successfully!');
      setShowUploadModal(false);
      setSelectedFile(null);
      setUploadForm({ title: '', description: '', document_type: 'other' });
      loadDocuments();
    } catch (error) {
      console.error('Upload error:', error);
      toast.error('Failed to upload document');
    } finally {
      setUploading(false);
    }
  };

  const handleAnalyzeDocument = async (documentId: number) => {
    try {
      const document = documents.find(d => d.id === documentId);
      if (!document) return;

      toast.loading('Analyzing document...');
      const analysis = await apiClient.analyzeDocument(
        new File([document.file_url], document.title, { type: document.file_type }),
        document.document_type
      );
      
      setDocuments(prev => prev.map(d => 
        d.id === documentId ? { ...d, ai_analysis: analysis } : d
      ));
      toast.dismiss();
      toast.success('Document analysis completed!');
    } catch (error) {
      console.error('Analysis error:', error);
      toast.dismiss();
      toast.error('Failed to analyze document');
    }
  };

  const handleAnchorToBlockchain = async (documentId: number) => {
    try {
      toast.loading('Anchoring to blockchain...');
      await apiClient.anchorDocument(documentId);
      toast.dismiss();
      toast.success('Document anchored to blockchain!');
      loadDocuments();
    } catch (error) {
      console.error('Blockchain anchoring error:', error);
      toast.dismiss();
      toast.error('Failed to anchor document to blockchain');
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'verified':
        return <Badge className="bg-green-100 text-green-800"><CheckCircle className="w-3 h-3 mr-1" />Verified</Badge>;
      case 'pending_verification':
        return <Badge className="bg-yellow-100 text-yellow-800"><Clock className="w-3 h-3 mr-1" />Pending</Badge>;
      case 'rejected':
        return <Badge className="bg-red-100 text-red-800"><AlertCircle className="w-3 h-3 mr-1" />Rejected</Badge>;
      default:
        return <Badge variant="secondary">{status}</Badge>;
    }
  };

  const getAIConfidenceBadge = (confidence?: number) => {
    if (!confidence) return null;
    
    if (confidence >= 0.8) {
      return <Badge className="bg-green-100 text-green-800">High ({Math.round(confidence * 100)}%)</Badge>;
    } else if (confidence >= 0.6) {
      return <Badge className="bg-yellow-100 text-yellow-800">Medium ({Math.round(confidence * 100)}%)</Badge>;
    } else {
      return <Badge className="bg-red-100 text-red-800">Low ({Math.round(confidence * 100)}%)</Badge>;
    }
  };

  const filteredDocuments = documents.filter(doc => {
    const matchesSearch = doc.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         doc.description?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || doc.status === statusFilter;
    const matchesType = documentTypeFilter === 'all' || doc.document_type === documentTypeFilter;
    
    return matchesSearch && matchesStatus && matchesType;
  });

  if (loading) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading documents...</p>
          </div>
        </div>
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="mb-8">
            <div className="flex justify-between items-center">
              <div>
                <h1 className="text-3xl font-bold text-gray-900 mb-2">Documents</h1>
                <p className="text-gray-600">Manage and verify your documents</p>
              </div>
              <Button onClick={() => setShowUploadModal(true)} className="flex items-center space-x-2">
                <Upload className="w-4 h-4" />
                <span>Upload Document</span>
              </Button>
            </div>
          </div>

          {/* Filters */}
          <Card className="mb-6">
            <CardContent className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div>
                  <Label htmlFor="search">Search</Label>
                  <div className="relative">
                    <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                    <Input
                      id="search"
                      placeholder="Search documents..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                </div>
                <div>
                  <Label htmlFor="status">Status</Label>
                  <Select value={statusFilter} onValueChange={setStatusFilter}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Status</SelectItem>
                      <SelectItem value="pending_verification">Pending</SelectItem>
                      <SelectItem value="verified">Verified</SelectItem>
                      <SelectItem value="rejected">Rejected</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="type">Document Type</Label>
                  <Select value={documentTypeFilter} onValueChange={setDocumentTypeFilter}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Types</SelectItem>
                      <SelectItem value="academic">Academic</SelectItem>
                      <SelectItem value="legal">Legal</SelectItem>
                      <SelectItem value="financial">Financial</SelectItem>
                      <SelectItem value="medical">Medical</SelectItem>
                      <SelectItem value="other">Other</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="flex items-end">
                  <Button variant="outline" onClick={loadDocuments} className="w-full">
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Refresh
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Documents Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredDocuments.map((doc) => (
              <Card key={doc.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-2">
                      <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                        <FileText className="w-4 h-4 text-blue-600" />
                      </div>
                      <div>
                        <CardTitle className="text-lg">{doc.title}</CardTitle>
                        <CardDescription className="text-sm">
                          {doc.document_type} • {new Date(doc.created_at).toLocaleDateString()}
                        </CardDescription>
                      </div>
                    </div>
                    {getStatusBadge(doc.status)}
                  </div>
                </CardHeader>
                <CardContent>
                  {doc.description && (
                    <p className="text-sm text-gray-600 mb-4">{doc.description}</p>
                  )}
                  
                  <div className="space-y-3">
                    {/* AI Analysis Status */}
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">AI Analysis:</span>
                      {doc.ai_analysis ? (
                        <div className="flex items-center space-x-2">
                          {getAIConfidenceBadge(doc.ai_analysis.confidence_score)}
                          {doc.ai_analysis.is_authentic ? (
                            <Badge className="bg-green-100 text-green-800">
                              <CheckCircle className="w-3 h-3 mr-1" />Authentic
                            </Badge>
                          ) : (
                            <Badge className="bg-red-100 text-red-800">
                              <AlertCircle className="w-3 h-3 mr-1" />Suspicious
                            </Badge>
                          )}
                        </div>
                      ) : (
                        <Badge variant="secondary">Not Analyzed</Badge>
                      )}
                    </div>

                    {/* Blockchain Status */}
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Blockchain:</span>
                      {doc.blockchain_hash ? (
                        <Badge className="bg-green-100 text-green-800">
                          <Shield className="w-3 h-3 mr-1" />Anchored
                        </Badge>
                      ) : (
                        <Badge variant="secondary">Not Anchored</Badge>
                      )}
                    </div>

                    {/* File Info */}
                    <div className="text-xs text-gray-500">
                      Size: {(doc.file_size / 1024 / 1024).toFixed(2)} MB
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex flex-wrap gap-2 mt-4">
                    <Button size="sm" variant="outline" onClick={() => window.open(doc.file_url, '_blank')}>
                      <Eye className="w-3 h-3 mr-1" />
                      View
                    </Button>
                    
                    {!doc.ai_analysis && (
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={() => handleAnalyzeDocument(doc.id)}
                      >
                        <BarChart3 className="w-3 h-3 mr-1" />
                        Analyze
                      </Button>
                    )}
                    
                    {doc.status === 'verified' && !doc.blockchain_hash && (
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={() => handleAnchorToBlockchain(doc.id)}
                      >
                        <Shield className="w-3 h-3 mr-1" />
                        Anchor
                      </Button>
                    )}
                    
                    <Button size="sm" variant="outline">
                      <QrCode className="w-3 h-3 mr-1" />
                      QR
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {filteredDocuments.length === 0 && (
            <Card>
              <CardContent className="p-12 text-center">
                <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No documents found</h3>
                <p className="text-gray-600 mb-4">
                  {searchTerm || statusFilter !== 'all' || documentTypeFilter !== 'all'
                    ? 'Try adjusting your filters'
                    : 'Get started by uploading your first document'
                  }
                </p>
                <Button onClick={() => setShowUploadModal(true)}>
                  <Upload className="w-4 h-4 mr-2" />
                  Upload Document
                </Button>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Upload Modal */}
        {showUploadModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <Card className="w-full max-w-md mx-4">
              <CardHeader>
                <CardTitle>Upload Document</CardTitle>
                <CardDescription>
                  Upload a document for AI analysis and blockchain anchoring
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="file">File</Label>
                  <Input
                    id="file"
                    type="file"
                    onChange={handleFileSelect}
                    accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
                  />
                </div>
                
                <div>
                  <Label htmlFor="title">Title</Label>
                  <Input
                    id="title"
                    value={uploadForm.title}
                    onChange={(e) => setUploadForm(prev => ({ ...prev, title: e.target.value }))}
                    placeholder="Document title"
                  />
                </div>
                
                <div>
                  <Label htmlFor="description">Description</Label>
                  <Input
                    id="description"
                    value={uploadForm.description}
                    onChange={(e) => setUploadForm(prev => ({ ...prev, description: e.target.value }))}
                    placeholder="Document description"
                  />
                </div>
                
                <div>
                  <Label htmlFor="document_type">Document Type</Label>
                  <Select 
                    value={uploadForm.document_type} 
                    onValueChange={(value) => setUploadForm(prev => ({ ...prev, document_type: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="academic_degree">Academic Degree</SelectItem>
                      <SelectItem value="transcript">Transcript</SelectItem>
                      <SelectItem value="certificate">Certificate</SelectItem>
                      <SelectItem value="id_document">ID Document</SelectItem>
                      <SelectItem value="contract">Contract</SelectItem>
                      <SelectItem value="medical_record">Medical Record</SelectItem>
                      <SelectItem value="financial_document">Financial Document</SelectItem>
                      <SelectItem value="property_document">Property Document</SelectItem>
                      <SelectItem value="other">Other</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="flex space-x-2 pt-4">
                  <Button 
                    variant="outline" 
                    onClick={() => setShowUploadModal(false)}
                    className="flex-1"
                  >
                    Cancel
                  </Button>
                  <Button 
                    onClick={handleUpload}
                    disabled={!selectedFile || uploading}
                    className="flex-1"
                  >
                    {uploading ? 'Uploading...' : 'Upload'}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </ProtectedRoute>
  );
}
