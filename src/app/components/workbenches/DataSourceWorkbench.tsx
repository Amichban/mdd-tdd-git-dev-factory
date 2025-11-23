/**
 * DataSourceWorkbench Component
 *
 * AUTO-GENERATED from specs/workbenches.json
 * DO NOT EDIT MANUALLY - changes will be overwritten
 *
 * Generated: 2024-01-01T00:00:00Z
 * Source: specs/workbenches.json#DataSourceWorkbench
 */

import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

// Types
interface RawDataSource {
  id: string;
  name: string;
  source_type: 'database' | 'api' | 'file' | 'stream' | 'webhook';
  connection_string: string;
  schema_definition?: Record<string, unknown>;
  refresh_interval: number;
  is_active: boolean;
  last_sync_at?: string;
  sync_status: 'pending' | 'syncing' | 'success' | 'failed';
  error_message?: string;
  metadata?: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

interface DataSourceListResponse {
  items: RawDataSource[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

// API functions
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const fetchDataSources = async (params: {
  page?: number;
  source_type?: string;
  is_active?: boolean;
  sync_status?: string;
  search?: string;
}): Promise<DataSourceListResponse> => {
  const searchParams = new URLSearchParams();
  if (params.page) searchParams.set('page', String(params.page));
  if (params.source_type) searchParams.set('source_type', params.source_type);
  if (params.is_active !== undefined) searchParams.set('is_active', String(params.is_active));
  if (params.sync_status) searchParams.set('sync_status', params.sync_status);
  if (params.search) searchParams.set('search', params.search);

  const response = await fetch(`${API_BASE}/raw-data-sources?${searchParams}`);
  if (!response.ok) throw new Error('Failed to fetch data sources');
  return response.json();
};

const syncDataSource = async (id: string): Promise<void> => {
  const response = await fetch(`${API_BASE}/raw-data-sources/${id}/sync`, {
    method: 'POST',
  });
  if (!response.ok) throw new Error('Failed to sync data source');
};

const testConnection = async (id: string): Promise<{ success: boolean; message: string }> => {
  const response = await fetch(`${API_BASE}/raw-data-sources/${id}/test`, {
    method: 'POST',
  });
  if (!response.ok) throw new Error('Failed to test connection');
  return response.json();
};

// Component
export const DataSourceWorkbench: React.FC = () => {
  const queryClient = useQueryClient();
  const [selectedSource, setSelectedSource] = useState<RawDataSource | null>(null);
  const [filters, setFilters] = useState({
    source_type: '',
    is_active: undefined as boolean | undefined,
    sync_status: '',
    search: '',
  });
  const [page, setPage] = useState(1);

  // Queries
  const { data, isLoading, error } = useQuery({
    queryKey: ['dataSources', page, filters],
    queryFn: () => fetchDataSources({ page, ...filters }),
  });

  // Mutations
  const syncMutation = useMutation({
    mutationFn: syncDataSource,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dataSources'] });
    },
  });

  const testMutation = useMutation({
    mutationFn: testConnection,
  });

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'n' && !e.metaKey && !e.ctrlKey) {
        // Open create modal
      }
      if (e.key === 'r' && !e.metaKey && !e.ctrlKey) {
        queryClient.invalidateQueries({ queryKey: ['dataSources'] });
      }
      if (e.key === '/') {
        e.preventDefault();
        // Focus search
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [queryClient]);

  // Stats calculations
  const activeCount = data?.items.filter(s => s.is_active).length ?? 0;
  const failedCount = data?.items.filter(s => s.sync_status === 'failed').length ?? 0;

  return (
    <div className="workbench-container" style={{ display: 'flex', height: '100vh' }}>
      {/* Zone A: Pulse (20%) */}
      <aside className="zone-pulse" style={{ width: '20%', padding: '1rem', borderRight: '1px solid #e5e7eb' }}>
        {/* Stats Cards */}
        <div className="stats-card" style={{ marginBottom: '1rem', padding: '1rem', background: '#f9fafb', borderRadius: '0.5rem' }}>
          <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>Active Sources</div>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#3B82F6' }}>{activeCount}</div>
        </div>

        <div className="stats-card" style={{ marginBottom: '1rem', padding: '1rem', background: failedCount > 0 ? '#fef2f2' : '#f9fafb', borderRadius: '0.5rem' }}>
          <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>Failed Syncs</div>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: failedCount > 0 ? '#ef4444' : '#10b981' }}>{failedCount}</div>
        </div>

        {/* Activity Feed */}
        <div className="activity-feed">
          <h3 style={{ fontSize: '0.875rem', fontWeight: '600', marginBottom: '0.5rem' }}>Recent Activity</h3>
          {/* Activity items would be populated from event bus */}
          <div style={{ fontSize: '0.75rem', color: '#9ca3af' }}>No recent activity</div>
        </div>
      </aside>

      {/* Zone B: Canvas (50%) */}
      <main className="zone-canvas" style={{ width: '50%', padding: '1rem', overflow: 'auto' }}>
        {/* Search & Filters */}
        <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
          <input
            type="text"
            placeholder="Search sources... (/)"
            value={filters.search}
            onChange={e => setFilters(f => ({ ...f, search: e.target.value }))}
            style={{ flex: 1, padding: '0.5rem', border: '1px solid #d1d5db', borderRadius: '0.375rem' }}
          />
          <select
            value={filters.source_type}
            onChange={e => setFilters(f => ({ ...f, source_type: e.target.value }))}
            style={{ padding: '0.5rem', border: '1px solid #d1d5db', borderRadius: '0.375rem' }}
          >
            <option value="">All Types</option>
            <option value="database">Database</option>
            <option value="api">API</option>
            <option value="file">File</option>
            <option value="stream">Stream</option>
            <option value="webhook">Webhook</option>
          </select>
          <select
            value={filters.sync_status}
            onChange={e => setFilters(f => ({ ...f, sync_status: e.target.value }))}
            style={{ padding: '0.5rem', border: '1px solid #d1d5db', borderRadius: '0.375rem' }}
          >
            <option value="">All Status</option>
            <option value="pending">Pending</option>
            <option value="syncing">Syncing</option>
            <option value="success">Success</option>
            <option value="failed">Failed</option>
          </select>
        </div>

        {/* Data Table */}
        {isLoading ? (
          <div>Loading...</div>
        ) : error ? (
          <div style={{ color: '#ef4444' }}>Error loading data sources</div>
        ) : (
          <>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid #e5e7eb' }}>
                  <th style={{ textAlign: 'left', padding: '0.75rem', fontSize: '0.875rem' }}>Name</th>
                  <th style={{ textAlign: 'left', padding: '0.75rem', fontSize: '0.875rem' }}>Type</th>
                  <th style={{ textAlign: 'left', padding: '0.75rem', fontSize: '0.875rem' }}>Status</th>
                  <th style={{ textAlign: 'left', padding: '0.75rem', fontSize: '0.875rem' }}>Last Sync</th>
                  <th style={{ textAlign: 'right', padding: '0.75rem', fontSize: '0.875rem' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {data?.items.map(source => (
                  <tr
                    key={source.id}
                    onClick={() => setSelectedSource(source)}
                    style={{
                      borderBottom: '1px solid #e5e7eb',
                      cursor: 'pointer',
                      background: selectedSource?.id === source.id ? '#eff6ff' : 'transparent',
                    }}
                  >
                    <td style={{ padding: '0.75rem' }}>{source.name}</td>
                    <td style={{ padding: '0.75rem' }}>
                      <span style={{
                        padding: '0.25rem 0.5rem',
                        borderRadius: '0.25rem',
                        fontSize: '0.75rem',
                        background: '#e5e7eb',
                      }}>
                        {source.source_type}
                      </span>
                    </td>
                    <td style={{ padding: '0.75rem' }}>
                      <span style={{
                        padding: '0.25rem 0.5rem',
                        borderRadius: '0.25rem',
                        fontSize: '0.75rem',
                        background: {
                          pending: '#fef3c7',
                          syncing: '#dbeafe',
                          success: '#d1fae5',
                          failed: '#fee2e2',
                        }[source.sync_status],
                        color: {
                          pending: '#92400e',
                          syncing: '#1e40af',
                          success: '#065f46',
                          failed: '#991b1b',
                        }[source.sync_status],
                      }}>
                        {source.sync_status}
                      </span>
                    </td>
                    <td style={{ padding: '0.75rem', fontSize: '0.875rem', color: '#6b7280' }}>
                      {source.last_sync_at
                        ? new Date(source.last_sync_at).toLocaleString()
                        : 'Never'}
                    </td>
                    <td style={{ padding: '0.75rem', textAlign: 'right' }}>
                      <button
                        onClick={e => {
                          e.stopPropagation();
                          syncMutation.mutate(source.id);
                        }}
                        style={{
                          padding: '0.25rem 0.5rem',
                          marginRight: '0.25rem',
                          border: '1px solid #d1d5db',
                          borderRadius: '0.25rem',
                          background: 'white',
                          cursor: 'pointer',
                        }}
                      >
                        Sync
                      </button>
                      <button
                        onClick={e => {
                          e.stopPropagation();
                          testMutation.mutate(source.id);
                        }}
                        style={{
                          padding: '0.25rem 0.5rem',
                          border: '1px solid #d1d5db',
                          borderRadius: '0.25rem',
                          background: 'white',
                          cursor: 'pointer',
                        }}
                      >
                        Test
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {/* Pagination */}
            {data && data.pages > 1 && (
              <div style={{ display: 'flex', justifyContent: 'center', gap: '0.5rem', marginTop: '1rem' }}>
                <button
                  disabled={page === 1}
                  onClick={() => setPage(p => p - 1)}
                  style={{ padding: '0.5rem 1rem', border: '1px solid #d1d5db', borderRadius: '0.25rem' }}
                >
                  Previous
                </button>
                <span style={{ padding: '0.5rem', color: '#6b7280' }}>
                  Page {page} of {data.pages}
                </span>
                <button
                  disabled={page === data.pages}
                  onClick={() => setPage(p => p + 1)}
                  style={{ padding: '0.5rem 1rem', border: '1px solid #d1d5db', borderRadius: '0.25rem' }}
                >
                  Next
                </button>
              </div>
            )}
          </>
        )}
      </main>

      {/* Zone C: Co-Pilot (30%) */}
      <aside className="zone-copilot" style={{ width: '30%', padding: '1rem', borderLeft: '1px solid #e5e7eb', overflow: 'auto' }}>
        {selectedSource ? (
          <>
            {/* Detail Panel */}
            <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>
              {selectedSource.name}
            </h2>

            {/* Configuration Section */}
            <section style={{ marginBottom: '1.5rem' }}>
              <h3 style={{ fontSize: '0.875rem', fontWeight: '600', color: '#6b7280', marginBottom: '0.5rem' }}>
                Configuration
              </h3>
              <dl style={{ fontSize: '0.875rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem 0', borderBottom: '1px solid #f3f4f6' }}>
                  <dt style={{ color: '#6b7280' }}>Type</dt>
                  <dd>{selectedSource.source_type}</dd>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem 0', borderBottom: '1px solid #f3f4f6' }}>
                  <dt style={{ color: '#6b7280' }}>Refresh</dt>
                  <dd>{selectedSource.refresh_interval}s</dd>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem 0', borderBottom: '1px solid #f3f4f6' }}>
                  <dt style={{ color: '#6b7280' }}>Active</dt>
                  <dd>{selectedSource.is_active ? 'Yes' : 'No'}</dd>
                </div>
              </dl>
            </section>

            {/* Schema Section */}
            {selectedSource.schema_definition && (
              <section style={{ marginBottom: '1.5rem' }}>
                <h3 style={{ fontSize: '0.875rem', fontWeight: '600', color: '#6b7280', marginBottom: '0.5rem' }}>
                  Schema
                </h3>
                <pre style={{
                  padding: '0.75rem',
                  background: '#f9fafb',
                  borderRadius: '0.375rem',
                  fontSize: '0.75rem',
                  overflow: 'auto',
                }}>
                  {JSON.stringify(selectedSource.schema_definition, null, 2)}
                </pre>
              </section>
            )}

            {/* Status Section */}
            <section style={{ marginBottom: '1.5rem' }}>
              <h3 style={{ fontSize: '0.875rem', fontWeight: '600', color: '#6b7280', marginBottom: '0.5rem' }}>
                Status
              </h3>
              <dl style={{ fontSize: '0.875rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem 0', borderBottom: '1px solid #f3f4f6' }}>
                  <dt style={{ color: '#6b7280' }}>Status</dt>
                  <dd>{selectedSource.sync_status}</dd>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem 0', borderBottom: '1px solid #f3f4f6' }}>
                  <dt style={{ color: '#6b7280' }}>Last Sync</dt>
                  <dd>{selectedSource.last_sync_at ? new Date(selectedSource.last_sync_at).toLocaleString() : 'Never'}</dd>
                </div>
                {selectedSource.error_message && (
                  <div style={{ padding: '0.5rem 0' }}>
                    <dt style={{ color: '#ef4444', marginBottom: '0.25rem' }}>Error</dt>
                    <dd style={{ color: '#991b1b', fontSize: '0.75rem' }}>{selectedSource.error_message}</dd>
                  </div>
                )}
              </dl>
            </section>

            {/* Sync History / Explainability */}
            <section>
              <h3 style={{ fontSize: '0.875rem', fontWeight: '600', color: '#6b7280', marginBottom: '0.5rem' }}>
                Sync History
              </h3>
              <div style={{ fontSize: '0.75rem', color: '#9ca3af' }}>
                {/* Events would be loaded from event bus by correlation_id */}
                View sync events and decisions in the timeline
              </div>
            </section>
          </>
        ) : (
          <div style={{ color: '#9ca3af', textAlign: 'center', marginTop: '2rem' }}>
            Select a data source to view details
          </div>
        )}
      </aside>
    </div>
  );
};

export default DataSourceWorkbench;
