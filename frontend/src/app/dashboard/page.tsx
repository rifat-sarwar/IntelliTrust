'use client'

import { useEffect, useState } from 'react';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useAuth } from '@/contexts/AuthContext';
import { apiClient, Document, Credential } from '@/lib/api';
import { 
  FileText, 
  Shield, 
  CheckCircle, 
  Clock, 
  AlertCircle,
  Upload,
  Eye,
  Users,
  BarChart3,
  Activity,
  Award,
  Building,
  QrCode
} from 'lucide-react';
import Link from 'next/link';
import toast from 'react-hot-toast';

interface DashboardStats {
  totalDocuments: number;
  verifiedDocuments: number;
  pendingDocuments: number;
  totalCredentials: number;
  activeCredentials: number;
  totalVerifications: number;
  successfulVerifications: number;
}

export default function DashboardPage() {
  const { user } = useAuth();
  const [stats, setStats] = useState<DashboardStats>({
    totalDocuments: 0,
    verifiedDocuments: 0,
    pendingDocuments: 0,
    totalCredentials: 0,
    activeCredentials: 0,
    totalVerifications: 0,
    successfulVerifications: 0,
  });
  const [recentDocuments, setRecentDocuments] = useState<Document[]>([]);
  const [recentCredentials, setRecentCredentials] = useState<Credential[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load documents
      const documentsResponse = await apiClient.getDocuments({ limit: 5 });
      setRecentDocuments(documentsResponse.items || []);
      
      // Load credentials
      const credentialsResponse = await apiClient.getMyCredentials({ limit: 5 });
      setRecentCredentials(credentialsResponse || []);
      
      // Calculate stats
      const allDocuments = await apiClient.getDocuments({ limit: 100 });
      const allCredentials = await apiClient.getMyCredentials({ limit: 100 });
      const allVerifications = await apiClient.getMyVerifications({ limit: 100 });
      
      setStats({
        totalDocuments: allDocuments.total || 0,
        verifiedDocuments: allDocuments.items?.filter(d => d.status === 'verified').length || 0,
        pendingDocuments: allDocuments.items?.filter(d => d.status === 'pending_verification').length || 0,
        totalCredentials: allCredentials.length || 0,
        activeCredentials: allCredentials.filter(c => c.status === 'active').length || 0,
        totalVerifications: allVerifications.length || 0,
        successfulVerifications: allVerifications.filter(v => v.status === 'completed' && v.result?.overall_verified).length || 0,
      });
      
    } catch (error) {
      console.error('Error loading dashboard data:', error);
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const getRoleBasedActions = () => {
    switch (user?.role) {
      case 'admin':
        return [
          { title: 'Manage Users', href: '/admin/users', icon: Users },
          { title: 'Organizations', href: '/admin/organizations', icon: Building },
          { title: 'System Analytics', href: '/admin/analytics', icon: BarChart3 },
        ];
      case 'issuer':
        return [
          { title: 'Upload Document', href: '/issuer', icon: Upload },
          { title: 'Issue Credentials', href: '/credentials/issue', icon: Award },
          { title: 'Manage Documents', href: '/documents', icon: FileText },
        ];
      case 'holder':
        return [
          { title: 'My Credentials', href: '/holder', icon: Shield },
          { title: 'View Documents', href: '/documents', icon: FileText },
          { title: 'Generate QR Code', href: '/qr-generator', icon: QrCode },
        ];
      case 'verifier':
        return [
          { title: 'Verify Documents', href: '/verifier', icon: Eye },
          { title: 'Scan QR Code', href: '/verifier', icon: QrCode },
          { title: 'Verification History', href: '/verifications', icon: Activity },
        ];
      default:
        return [];
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
      case 'active':
        return <Badge className="bg-green-100 text-green-800"><CheckCircle className="w-3 h-3 mr-1" />Active</Badge>;
      case 'expired':
        return <Badge className="bg-red-100 text-red-800"><AlertCircle className="w-3 h-3 mr-1" />Expired</Badge>;
      default:
        return <Badge variant="secondary">{status}</Badge>;
    }
  };

  if (loading) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading dashboard...</p>
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
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Welcome back, {user?.full_name}!
            </h1>
            <p className="text-gray-600">
              Here&apos;s what&apos;s happening with your {user?.role} account
            </p>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Documents</CardTitle>
                <FileText className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.totalDocuments}</div>
                <p className="text-xs text-muted-foreground">
                  {stats.verifiedDocuments} verified
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Active Credentials</CardTitle>
                <Shield className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.activeCredentials}</div>
                <p className="text-xs text-muted-foreground">
                  of {stats.totalCredentials} total
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Verifications</CardTitle>
                <CheckCircle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.successfulVerifications}</div>
                <p className="text-xs text-muted-foreground">
                  of {stats.totalVerifications} total
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Pending Items</CardTitle>
                <Clock className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.pendingDocuments}</div>
                <p className="text-xs text-muted-foreground">
                  documents pending verification
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Quick Actions */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {getRoleBasedActions().map((action) => (
                <Link key={action.title} href={action.href}>
                  <Card className="hover:shadow-md transition-shadow cursor-pointer">
                    <CardContent className="p-6">
                      <div className="flex items-center space-x-3">
                        <action.icon className="h-6 w-6 text-blue-600" />
                        <div>
                          <h3 className="font-medium text-gray-900">{action.title}</h3>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </Link>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Recent Documents */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <FileText className="w-5 h-5 mr-2" />
                  Recent Documents
                </CardTitle>
                <CardDescription>
                  Your recently uploaded documents
                </CardDescription>
              </CardHeader>
              <CardContent>
                {recentDocuments.length > 0 ? (
                  <div className="space-y-4">
                    {recentDocuments.map((doc) => (
                      <div key={doc.id} className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex items-center space-x-3">
                          <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                            <FileText className="w-4 h-4 text-blue-600" />
                          </div>
                          <div>
                            <h4 className="font-medium text-sm">{doc.title}</h4>
                            <p className="text-xs text-gray-500">
                              {new Date(doc.created_at).toLocaleDateString()}
                            </p>
                          </div>
                        </div>
                        {getStatusBadge(doc.status)}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-500">No documents yet</p>
                    <Button className="mt-2" asChild>
                      <Link href="/documents">Upload Document</Link>
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Recent Credentials */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Shield className="w-5 h-5 mr-2" />
                  Recent Credentials
                </CardTitle>
                <CardDescription>
                  Your recently issued credentials
                </CardDescription>
              </CardHeader>
              <CardContent>
                {recentCredentials.length > 0 ? (
                  <div className="space-y-4">
                    {recentCredentials.map((cred) => (
                      <div key={cred.id} className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex items-center space-x-3">
                          <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                            <Shield className="w-4 h-4 text-green-600" />
                          </div>
                          <div>
                            <h4 className="font-medium text-sm">{cred.title}</h4>
                            <p className="text-xs text-gray-500">
                              Issued {new Date(cred.issued_at).toLocaleDateString()}
                            </p>
                          </div>
                        </div>
                        {getStatusBadge(cred.status)}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <Shield className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-500">No credentials yet</p>
                    <Button className="mt-2" asChild>
                      <Link href="/credentials">View Credentials</Link>
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
