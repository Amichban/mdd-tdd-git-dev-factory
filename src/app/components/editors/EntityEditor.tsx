/**
 * Entity Editor Component
 *
 * Visual editor for entity definitions in specs/entities.json
 * Allows business users to view and edit entities without touching code
 */

import React, { useState } from 'react';
import {
  Entity,
  Property,
  Relationship,
  Action,
  PropertyType,
  RelationshipType,
} from '../../types/specs';

interface EntityEditorProps {
  entity: Entity;
  allEntities: Entity[];
  onSave: (entity: Entity) => void;
  onCancel: () => void;
  pendingChanges?: { issueNumber?: number; prNumber?: number };
}

export const EntityEditor: React.FC<EntityEditorProps> = ({
  entity,
  allEntities,
  onSave,
  onCancel,
  pendingChanges,
}) => {
  const [editedEntity, setEditedEntity] = useState<Entity>({ ...entity });
  const [activeTab, setActiveTab] = useState<'properties' | 'relationships' | 'actions'>('properties');

  const handlePropertyChange = (index: number, field: keyof Property, value: any) => {
    const newProperties = [...editedEntity.properties];
    newProperties[index] = { ...newProperties[index], [field]: value };
    setEditedEntity({ ...editedEntity, properties: newProperties });
  };

  const handleAddProperty = () => {
    const newProperty: Property = {
      id: `new_property_${Date.now()}`,
      name: 'New Property',
      type: 'string',
      description: '',
      required: false,
    };
    setEditedEntity({
      ...editedEntity,
      properties: [...editedEntity.properties, newProperty],
    });
  };

  const handleRemoveProperty = (index: number) => {
    const newProperties = editedEntity.properties.filter((_, i) => i !== index);
    setEditedEntity({ ...editedEntity, properties: newProperties });
  };

  const handleAddRelationship = () => {
    const newRelationship: Relationship = {
      id: `new_relationship_${Date.now()}`,
      name: 'New Relationship',
      targetEntity: allEntities[0]?.id || '',
      type: 'many-to-one',
      description: '',
    };
    setEditedEntity({
      ...editedEntity,
      relationships: [...(editedEntity.relationships || []), newRelationship],
    });
  };

  const handleAddAction = () => {
    const newAction: Action = {
      id: `new_action_${Date.now()}`,
      name: 'New Action',
      description: '',
    };
    setEditedEntity({
      ...editedEntity,
      actions: [...(editedEntity.actions || []), newAction],
    });
  };

  return (
    <div className="entity-editor">
      {/* Header */}
      <div className="editor-header">
        <div className="entity-info">
          <input
            type="text"
            value={editedEntity.name}
            onChange={(e) => setEditedEntity({ ...editedEntity, name: e.target.value })}
            className="entity-name-input"
          />
          <span className="entity-id">ID: {editedEntity.id}</span>
        </div>

        {pendingChanges && (
          <div className="pending-status">
            {pendingChanges.prNumber ? (
              <span className="status-badge in-review">
                PR #{pendingChanges.prNumber}
              </span>
            ) : pendingChanges.issueNumber ? (
              <span className="status-badge pending">
                Issue #{pendingChanges.issueNumber}
              </span>
            ) : null}
          </div>
        )}
      </div>

      {/* Description */}
      <div className="description-section">
        <label>Description</label>
        <textarea
          value={editedEntity.description}
          onChange={(e) => setEditedEntity({ ...editedEntity, description: e.target.value })}
          rows={2}
        />
      </div>

      {/* Tabs */}
      <div className="editor-tabs">
        <button
          className={activeTab === 'properties' ? 'active' : ''}
          onClick={() => setActiveTab('properties')}
        >
          Properties ({editedEntity.properties.length})
        </button>
        <button
          className={activeTab === 'relationships' ? 'active' : ''}
          onClick={() => setActiveTab('relationships')}
        >
          Relationships ({editedEntity.relationships?.length || 0})
        </button>
        <button
          className={activeTab === 'actions' ? 'active' : ''}
          onClick={() => setActiveTab('actions')}
        >
          Actions ({editedEntity.actions?.length || 0})
        </button>
      </div>

      {/* Properties Tab */}
      {activeTab === 'properties' && (
        <div className="properties-section">
          <table className="properties-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Type</th>
                <th>Required</th>
                <th>Description</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {editedEntity.properties.map((prop, index) => (
                <tr key={prop.id}>
                  <td>
                    <input
                      type="text"
                      value={prop.name}
                      onChange={(e) => handlePropertyChange(index, 'name', e.target.value)}
                    />
                  </td>
                  <td>
                    <select
                      value={prop.type}
                      onChange={(e) => handlePropertyChange(index, 'type', e.target.value as PropertyType)}
                    >
                      <option value="string">Text</option>
                      <option value="number">Number</option>
                      <option value="integer">Integer</option>
                      <option value="boolean">Boolean</option>
                      <option value="datetime">DateTime</option>
                      <option value="date">Date</option>
                      <option value="enum">Enum</option>
                      <option value="array">Array</option>
                    </select>
                  </td>
                  <td>
                    <input
                      type="checkbox"
                      checked={prop.required || false}
                      onChange={(e) => handlePropertyChange(index, 'required', e.target.checked)}
                    />
                  </td>
                  <td>
                    <input
                      type="text"
                      value={prop.description}
                      onChange={(e) => handlePropertyChange(index, 'description', e.target.value)}
                    />
                  </td>
                  <td>
                    <button
                      className="btn-icon danger"
                      onClick={() => handleRemoveProperty(index)}
                      title="Remove property"
                    >
                      ×
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <button className="btn-add" onClick={handleAddProperty}>
            + Add Property
          </button>
        </div>
      )}

      {/* Relationships Tab */}
      {activeTab === 'relationships' && (
        <div className="relationships-section">
          {editedEntity.relationships?.map((rel, index) => (
            <div key={rel.id} className="relationship-card">
              <div className="relationship-header">
                <input
                  type="text"
                  value={rel.name}
                  onChange={(e) => {
                    const newRels = [...(editedEntity.relationships || [])];
                    newRels[index] = { ...newRels[index], name: e.target.value };
                    setEditedEntity({ ...editedEntity, relationships: newRels });
                  }}
                />
                <select
                  value={rel.type}
                  onChange={(e) => {
                    const newRels = [...(editedEntity.relationships || [])];
                    newRels[index] = { ...newRels[index], type: e.target.value as RelationshipType };
                    setEditedEntity({ ...editedEntity, relationships: newRels });
                  }}
                >
                  <option value="one-to-one">One to One</option>
                  <option value="one-to-many">One to Many</option>
                  <option value="many-to-one">Many to One</option>
                  <option value="many-to-many">Many to Many</option>
                </select>
              </div>
              <div className="relationship-target">
                →
                <select
                  value={rel.targetEntity}
                  onChange={(e) => {
                    const newRels = [...(editedEntity.relationships || [])];
                    newRels[index] = { ...newRels[index], targetEntity: e.target.value };
                    setEditedEntity({ ...editedEntity, relationships: newRels });
                  }}
                >
                  {allEntities.map((e) => (
                    <option key={e.id} value={e.id}>
                      {e.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          ))}
          <button className="btn-add" onClick={handleAddRelationship}>
            + Add Relationship
          </button>
        </div>
      )}

      {/* Actions Tab */}
      {activeTab === 'actions' && (
        <div className="actions-section">
          {editedEntity.actions?.map((action, index) => (
            <div key={action.id} className="action-card">
              <div className="action-header">
                <input
                  type="text"
                  value={action.name}
                  onChange={(e) => {
                    const newActions = [...(editedEntity.actions || [])];
                    newActions[index] = { ...newActions[index], name: e.target.value };
                    setEditedEntity({ ...editedEntity, actions: newActions });
                  }}
                  className="action-name"
                />
              </div>
              <textarea
                value={action.description}
                onChange={(e) => {
                  const newActions = [...(editedEntity.actions || [])];
                  newActions[index] = { ...newActions[index], description: e.target.value };
                  setEditedEntity({ ...editedEntity, actions: newActions });
                }}
                placeholder="Description"
                rows={2}
              />
              {action.preconditions && action.preconditions.length > 0 && (
                <div className="conditions">
                  <strong>Preconditions:</strong>
                  <ul>
                    {action.preconditions.map((pre, i) => (
                      <li key={i}>{pre}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
          <button className="btn-add" onClick={handleAddAction}>
            + Add Action
          </button>
        </div>
      )}

      {/* Footer Actions */}
      <div className="editor-footer">
        <button className="btn-secondary" onClick={onCancel}>
          Cancel
        </button>
        <button className="btn-primary" onClick={() => onSave(editedEntity)}>
          Save Changes
        </button>
      </div>

      <style jsx>{`
        .entity-editor {
          display: flex;
          flex-direction: column;
          height: 100%;
          padding: 16px;
        }

        .editor-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 16px;
        }

        .entity-info {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }

        .entity-name-input {
          font-size: 20px;
          font-weight: 600;
          border: none;
          border-bottom: 2px solid transparent;
          padding: 4px 0;
        }

        .entity-name-input:focus {
          border-bottom-color: #0066cc;
          outline: none;
        }

        .entity-id {
          font-size: 12px;
          color: #666;
          font-family: monospace;
        }

        .status-badge {
          padding: 4px 8px;
          border-radius: 4px;
          font-size: 12px;
        }

        .status-badge.pending {
          background: #fff3cd;
          color: #856404;
        }

        .status-badge.in-review {
          background: #cce5ff;
          color: #004085;
        }

        .description-section {
          margin-bottom: 16px;
        }

        .description-section label {
          display: block;
          font-weight: 500;
          margin-bottom: 4px;
        }

        .description-section textarea {
          width: 100%;
          padding: 8px;
          border: 1px solid #ddd;
          border-radius: 4px;
          resize: vertical;
        }

        .editor-tabs {
          display: flex;
          gap: 4px;
          margin-bottom: 16px;
          border-bottom: 1px solid #ddd;
        }

        .editor-tabs button {
          padding: 8px 16px;
          border: none;
          background: none;
          cursor: pointer;
          border-bottom: 2px solid transparent;
        }

        .editor-tabs button.active {
          border-bottom-color: #0066cc;
          color: #0066cc;
        }

        .properties-table {
          width: 100%;
          border-collapse: collapse;
        }

        .properties-table th,
        .properties-table td {
          padding: 8px;
          text-align: left;
          border-bottom: 1px solid #eee;
        }

        .properties-table th {
          font-weight: 500;
          background: #f8f9fa;
        }

        .properties-table input[type="text"],
        .properties-table select {
          width: 100%;
          padding: 4px 8px;
          border: 1px solid #ddd;
          border-radius: 4px;
        }

        .btn-add {
          margin-top: 12px;
          padding: 8px 16px;
          background: #f8f9fa;
          border: 1px dashed #ddd;
          border-radius: 4px;
          cursor: pointer;
        }

        .btn-add:hover {
          background: #e9ecef;
        }

        .btn-icon {
          padding: 4px 8px;
          border: none;
          background: none;
          cursor: pointer;
          font-size: 16px;
        }

        .btn-icon.danger:hover {
          color: #dc3545;
        }

        .relationship-card,
        .action-card {
          padding: 12px;
          border: 1px solid #ddd;
          border-radius: 4px;
          margin-bottom: 8px;
        }

        .editor-footer {
          display: flex;
          justify-content: flex-end;
          gap: 8px;
          margin-top: auto;
          padding-top: 16px;
          border-top: 1px solid #ddd;
        }

        .btn-primary {
          padding: 8px 16px;
          background: #0066cc;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
        }

        .btn-secondary {
          padding: 8px 16px;
          background: #f8f9fa;
          border: 1px solid #ddd;
          border-radius: 4px;
          cursor: pointer;
        }
      `}</style>
    </div>
  );
};

export default EntityEditor;
