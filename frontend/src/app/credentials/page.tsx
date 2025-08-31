'use client'

import { useState, useEffect, useCallback } from 'react';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useAuth } from '@/contexts/AuthContext';
import { apiClient, Credential, Document, CredentialCreateRequest } from '@/lib/api';
import { 
  Shield, 
  Plus, 
  Search, 
  Eye,
  QrCode,
  CheckCircle,
  AlertCircle,
  RefreshCw
} from 'lucide-react';
import toast from 'react-hot-toast';

export default function CredentialsPage() {
  const { user } = useAuth();
  const [credentials, setCredentials] = useState<Credential[]>([]);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [showIssueModal, setShowIssueModal] = useState(false);
  const [showQRModal, setShowQRModal] = useState(false);
  const [selectedCredential, setSelectedCredential] = useState<Credential | null>(null);
  const [qrData, setQrData] = useState<string>('');
  const [issueForm, setIssueForm] = useState<CredentialCreateRequest>({
    document_id: 0,
    holder_id: 0,
    credential_type: 'academic',
    title: '',
    description: '',
    metadata: {},
    validity_days: 365
  });

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      
      // Load credentials based on user role
      let credsResponse;
      if (user?.role === 'issuer' || user?.role === 'admin') {
        credsResponse = await apiClient.getIssuedCredentials();
      } else {
        credsResponse = await apiClient.getMyCredentials();
      }
      setCredentials(credsResponse || []);

      // Load documents for issuers
      if (user?.role === 'issuer' || user?.role === 'admin') {
        const docsResponse = await apiClient.getDocuments({ status: 'verified' });
        setDocuments(docsResponse.items || []);
      }
    } catch (error) {
      console.error('Error loading data:', error);
      toast.error('Failed to load credentials');
    } finally {
      setLoading(false);
    }
  }, [user?.role]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleIssueCredential = async () => {
    try {
      await apiClient.issueCredential(issueForm);
      toast.success('Credential issued successfully!');
      setShowIssueModal(false);
      setIssueForm({
        document_id: 0,
        holder_id: 0,
        credential_type: 'academic',
        title: '',
        description: '',
        metadata: {},
        validity_days: 365
      });
      loadData();
    } catch (error) {
      console.error('Error issuing credential:', error);
      toast.error('Failed to issue credential');
    }
  };

  const handleRevokeCredential = async (credentialId: number, reason: string) => {
    try {
      await apiClient.revokeCredential(credentialId, reason);
      toast.success('Credential revoked successfully!');
      loadData();
    } catch (error) {
      console.error('Error revoking credential:', error);
      toast.error('Failed to revoke credential');
    }
  };

  const handleGenerateQR = async (credentialId: number) => {
    try {
      const qrResponse = await apiClient.getCredentialQR(credentialId);
      setQrData(qrResponse.qr_code);
      setSelectedCredential(credentials.find(c => c.id === credentialId) || null);
      setShowQRModal(true);
    } catch (error) {
      console.error('Error generating QR code:', error);
      toast.error('Failed to generate QR code');
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return <Badge className="bg-green-100 text-green-800"><CheckCircle className="w-3 h-3 mr-1" />Active</Badge>;
      case 'expired':
        return <Badge className="bg-red-100 text-red-800"><AlertCircle className="w-3 h-3 mr-1" />Expired</Badge>;
      case 'revoked':
        return <Badge className="bg-red-100 text-red-800"><AlertCircle className="w-3 h-3 mr-1" />Revoked</Badge>;
      default:
        return <Badge variant="secondary">{status}</Badge>;
    }
  };

  const getCredentialTypeBadge = (type: string) => {
    const colors = {
      academic: 'bg-blue-100 text-blue-800',
      professional: 'bg-purple-100 text-purple-800',
      identity: 'bg-green-100 text-green-800',
      financial: 'bg-yellow-100 text-yellow-800',
      medical: 'bg-red-100 text-red-800'
    };
    
    return (
      <Badge className={colors[type as keyof typeof colors] || 'bg-gray-100 text-gray-800'}>
        {type.charAt(0).toUpperCase() + type.slice(1)}
      </Badge>
    );
  };

  const filteredCredentials = credentials.filter(cred => {
    const matchesSearch = cred.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         cred.description?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || cred.status === statusFilter;
    
    return matchesSearch && matchesStatus;
  });

  const isExpired = (expiresAt?: string) => {
    if (!expiresAt) return false;
    return new Date(expiresAt) < new Date();
  };

  if (loading) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading credentials...</p>
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
                <h1 className="text-3xl font-bold text-gray-900 mb-2">Credentials</h1>
                <p className="text-gray-600">
                  {user?.role === 'issuer' || user?.role === 'admin' 
                    ? 'Manage issued credentials' 
                    : 'View your credentials'
                  }
                </p>
              </div>
              {(user?.role === 'issuer' || user?.role === 'admin') && (
                <Button onClick={() => setShowIssueModal(true)} className="flex items-center space-x-2">
                  <Plus className="w-4 h-4" />
                  <span>Issue Credential</span>
                </Button>
              )}
            </div>
          </div>

          {/* Filters */}
          <Card className="mb-6">
            <CardContent className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <Label htmlFor="search">Search</Label>
                  <div className="relative">
                    <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                    <Input
                      id="search"
                      placeholder="Search credentials..."
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
                      <SelectItem value="active">Active</SelectItem>
                      <SelectItem value="expired">Expired</SelectItem>
                      <SelectItem value="revoked">Revoked</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="flex items-end">
                  <Button variant="outline" onClick={loadData} className="w-full">
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Refresh
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Credentials Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredCredentials.map((cred) => (
              <Card key={cred.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-2">
                      <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                        <Shield className="w-4 h-4 text-green-600" />
                      </div>
                      <div>
                        <CardTitle className="text-lg">{cred.title}</CardTitle>
                        <CardDescription className="text-sm">
                          {getCredentialTypeBadge(cred.credential_type)}
                        </CardDescription>
                      </div>
                    </div>
                    {getStatusBadge(cred.status)}
                  </div>
                </CardHeader>
                <CardContent>
                  {cred.description && (
                    <p className="text-sm text-gray-600 mb-4">{cred.description}</p>
                  )}
                  
                  <div className="space-y-3">
                    {/* Issue/Expiry Dates */}
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-500">Issued:</span>
                      <span>{new Date(cred.issued_at).toLocaleDateString()}</span>
                    </div>
                    
                    {cred.expires_at && (
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-500">Expires:</span>
                        <span className={isExpired(cred.expires_at) ? 'text-red-600' : ''}>
                          {new Date(cred.expires_at).toLocaleDateString()}
                        </span>
                      </div>
                    )}

                    {/* Revocation Info */}
                    {cred.revoked_at && (
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-500">Revoked:</span>
                        <span className="text-red-600">
                          {new Date(cred.revoked_at).toLocaleDateString()}
                        </span>
                      </div>
                    )}

                    {cred.revocation_reason && (
                      <div className="text-sm text-red-600 bg-red-50 p-2 rounded">
                        Reason: {cred.revocation_reason}
                      </div>
                    )}
                  </div>

                  {/* Actions */}
                  <div className="flex flex-wrap gap-2 mt-4">
                    <Button size="sm" variant="outline">
                      <Eye className="w-3 h-3 mr-1" />
                      View
                    </Button>
                    
                    <Button 
                      size="sm" 
                      variant="outline"
                      onClick={() => handleGenerateQR(cred.id)}
                    >
                      <QrCode className="w-3 h-3 mr-1" />
                      QR
                    </Button>
                    
                    {cred.status === 'active' && (user?.role === 'issuer' || user?.role === 'admin') && (
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={() => handleRevokeCredential(cred.id, 'Manual revocation')}
                      >
                        <AlertCircle className="w-3 h-3 mr-1" />
                        Revoke
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {filteredCredentials.length === 0 && (
            <Card>
              <CardContent className="p-12 text-center">
                <Shield className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No credentials found</h3>
                <p className="text-gray-600 mb-4">
                  {searchTerm || statusFilter !== 'all'
                    ? 'Try adjusting your filters'
                    : user?.role === 'issuer' || user?.role === 'admin'
                    ? 'Get started by issuing your first credential'
                    : 'No credentials have been issued to you yet'
                  }
                </p>
                {(user?.role === 'issuer' || user?.role === 'admin') && (
                  <Button onClick={() => setShowIssueModal(true)}>
                    <Plus className="w-4 h-4 mr-2" />
                    Issue Credential
                  </Button>
                )}
              </CardContent>
            </Card>
          )}
        </div>

        {/* Issue Credential Modal */}
        {showIssueModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <Card className="w-full max-w-md mx-4">
              <CardHeader>
                <CardTitle>Issue Credential</CardTitle>
                <CardDescription>
                  Issue a new credential based on a verified document
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="document">Document</Label>
                  <Select 
                    value={issueForm.document_id.toString()} 
                    onValueChange={(value) => setIssueForm(prev => ({ ...prev, document_id: parseInt(value) }))}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select a document" />
                    </SelectTrigger>
                    <SelectContent>
                      {documents.map((doc) => (
                        <SelectItem key={doc.id} value={doc.id.toString()}>
                          {doc.title}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                
                <div>
                  <Label htmlFor="title">Credential Title</Label>
                  <Input
                    id="title"
                    value={issueForm.title}
                    onChange={(e) => setIssueForm(prev => ({ ...prev, title: e.target.value }))}
                    placeholder="Credential title"
                  />
                </div>
                
                <div>
                  <Label htmlFor="description">Description</Label>
                  <Input
                    id="description"
                    value={issueForm.description || ''}
                    onChange={(e) => setIssueForm(prev => ({ ...prev, description: e.target.value }))}
                    placeholder="Credential description"
                  />
                </div>
                
                <div>
                  <Label htmlFor="credential_type">Credential Type</Label>
                  <Select 
                    value={issueForm.credential_type} 
                    onValueChange={(value) => setIssueForm(prev => ({ ...prev, credential_type: value as any }))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="academic">Academic</SelectItem>
                      <SelectItem value="professional">Professional</SelectItem>
                      <SelectItem value="identity">Identity</SelectItem>
                      <SelectItem value="financial">Financial</SelectItem>
                      <SelectItem value="medical">Medical</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div>
                  <Label htmlFor="validity_days">Validity (days)</Label>
                  <Input
                    id="validity_days"
                    type="number"
                    value={issueForm.validity_days}
                    onChange={(e) => setIssueForm(prev => ({ ...prev, validity_days: parseInt(e.target.value) }))}
                    placeholder="365"
                  />
                </div>
                
                <div className="flex space-x-2 pt-4">
                  <Button 
                    variant="outline" 
                    onClick={() => setShowIssueModal(false)}
                    className="flex-1"
                  >
                    Cancel
                  </Button>
                  <Button 
                    onClick={handleIssueCredential}
                    disabled={!issueForm.document_id || !issueForm.title}
                    className="flex-1"
                  >
                    Issue Credential
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* QR Code Modal */}
        {showQRModal && selectedCredential && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <Card className="w-full max-w-md mx-4">
              <CardHeader>
                <CardTitle>QR Code</CardTitle>
                <CardDescription>
                  Scan this QR code to verify the credential
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="text-center">
                  <img 
                    src={`data:image/png;base64,${qrData}`} 
                    alt="QR Code" 
                    className="mx-auto border rounded-lg"
                  />
                </div>
                <div className="text-sm text-gray-600">
                  <p><strong>Credential:</strong> {selectedCredential.title}</p>
                  <p><strong>Type:</strong> {selectedCredential.credential_type}</p>
                  <p><strong>Status:</strong> {selectedCredential.status}</p>
                </div>
                <Button 
                  variant="outline" 
                  onClick={() => setShowQRModal(false)}
                  className="w-full"
                >
                  Close
                </Button>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </ProtectedRoute>
  );
}
