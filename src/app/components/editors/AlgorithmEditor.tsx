/**
 * Algorithm Editor Component
 *
 * Visual editor for algorithm definitions in specs/algorithms.json
 * Shows calculation steps, formulas, and allows natural language editing
 */

import React, { useState } from 'react';
import { Algorithm, AlgorithmStep, AlgorithmInput } from '../../types/specs';

interface AlgorithmEditorProps {
  algorithm: Algorithm;
  onSave: (algorithm: Algorithm) => void;
  onCancel: () => void;
  onExplain?: (step: AlgorithmStep) => void;
  onWhatIf?: (inputs: Record<string, number>) => void;
}

export const AlgorithmEditor: React.FC<AlgorithmEditorProps> = ({
  algorithm,
  onSave,
  onCancel,
  onExplain,
  onWhatIf,
}) => {
  const [editedAlgorithm, setEditedAlgorithm] = useState<Algorithm>({ ...algorithm });
  const [testInputs, setTestInputs] = useState<Record<string, number>>({});
  const [showWhatIf, setShowWhatIf] = useState(false);

  const handleStepChange = (index: number, field: keyof AlgorithmStep, value: any) => {
    const newSteps = [...editedAlgorithm.steps];
    newSteps[index] = { ...newSteps[index], [field]: value };
    setEditedAlgorithm({ ...editedAlgorithm, steps: newSteps });
  };

  const handleInputChange = (index: number, field: keyof AlgorithmInput, value: any) => {
    const newInputs = [...editedAlgorithm.inputs];
    newInputs[index] = { ...newInputs[index], [field]: value };
    setEditedAlgorithm({ ...editedAlgorithm, inputs: newInputs });
  };

  const calculateTotalWeight = () => {
    return editedAlgorithm.steps.reduce((sum, step) => sum + (step.weight || 0), 0);
  };

  return (
    <div className="algorithm-editor">
      {/* Header */}
      <div className="editor-header">
        <input
          type="text"
          value={editedAlgorithm.name}
          onChange={(e) => setEditedAlgorithm({ ...editedAlgorithm, name: e.target.value })}
          className="algorithm-name-input"
        />
        <span className="algorithm-id">ID: {editedAlgorithm.id}</span>
      </div>

      {/* Description */}
      <div className="description-section">
        <label>Purpose</label>
        <textarea
          value={editedAlgorithm.description}
          onChange={(e) => setEditedAlgorithm({ ...editedAlgorithm, description: e.target.value })}
          rows={2}
        />
      </div>

      {/* Inputs Section */}
      <div className="inputs-section">
        <h3>Inputs</h3>
        <table className="inputs-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Type</th>
              <th>Description</th>
            </tr>
          </thead>
          <tbody>
            {editedAlgorithm.inputs.map((input, index) => (
              <tr key={input.id}>
                <td>
                  <input
                    type="text"
                    value={input.name}
                    onChange={(e) => handleInputChange(index, 'name', e.target.value)}
                  />
                </td>
                <td>
                  <select
                    value={input.type}
                    onChange={(e) => handleInputChange(index, 'type', e.target.value)}
                  >
                    <option value="number">Number</option>
                    <option value="integer">Integer</option>
                    <option value="string">Text</option>
                    <option value="boolean">Boolean</option>
                  </select>
                </td>
                <td>
                  <input
                    type="text"
                    value={input.description}
                    onChange={(e) => handleInputChange(index, 'description', e.target.value)}
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Calculation Steps */}
      <div className="steps-section">
        <div className="steps-header">
          <h3>Calculation Steps</h3>
          <span className="weight-total">
            Total Weight: {(calculateTotalWeight() * 100).toFixed(0)}%
          </span>
        </div>

        {editedAlgorithm.steps.map((step, index) => (
          <div key={step.id} className="step-card">
            <div className="step-header">
              <span className="step-number">{index + 1}</span>
              <input
                type="text"
                value={step.name}
                onChange={(e) => handleStepChange(index, 'name', e.target.value)}
                className="step-name"
              />
              <div className="step-weight">
                <input
                  type="number"
                  value={(step.weight || 0) * 100}
                  onChange={(e) => handleStepChange(index, 'weight', Number(e.target.value) / 100)}
                  min={0}
                  max={100}
                  step={5}
                />
                <span>%</span>
              </div>
            </div>

            <div className="step-description">
              <textarea
                value={step.description}
                onChange={(e) => handleStepChange(index, 'description', e.target.value)}
                placeholder="Explain what this step does in plain English..."
                rows={2}
              />
            </div>

            <div className="step-formula">
              <label>Formula</label>
              <input
                type="text"
                value={step.formula}
                onChange={(e) => handleStepChange(index, 'formula', e.target.value)}
                className="formula-input"
              />
              {onExplain && (
                <button
                  className="btn-explain"
                  onClick={() => onExplain(step)}
                  title="Explain this formula"
                >
                  ?
                </button>
              )}
            </div>
          </div>
        ))}

        <button
          className="btn-add"
          onClick={() => {
            const newStep: AlgorithmStep = {
              id: `step_${Date.now()}`,
              name: 'New Step',
              description: '',
              formula: '',
              weight: 0,
            };
            setEditedAlgorithm({
              ...editedAlgorithm,
              steps: [...editedAlgorithm.steps, newStep],
            });
          }}
        >
          + Add Step
        </button>
      </div>

      {/* Final Formula */}
      <div className="final-formula-section">
        <label>Final Formula</label>
        <input
          type="text"
          value={editedAlgorithm.finalFormula || ''}
          onChange={(e) => setEditedAlgorithm({ ...editedAlgorithm, finalFormula: e.target.value })}
          className="formula-input"
          placeholder="e.g., step1 * 0.4 + step2 * 0.3 + step3 * 0.3"
        />
      </div>

      {/* Output */}
      <div className="output-section">
        <h3>Output</h3>
        <div className="output-config">
          <div className="output-field">
            <label>Type</label>
            <select
              value={editedAlgorithm.output.type}
              onChange={(e) =>
                setEditedAlgorithm({
                  ...editedAlgorithm,
                  output: { ...editedAlgorithm.output, type: e.target.value },
                })
              }
            >
              <option value="number">Number</option>
              <option value="integer">Integer</option>
              <option value="boolean">Boolean</option>
            </select>
          </div>
          {editedAlgorithm.output.type === 'number' && (
            <>
              <div className="output-field">
                <label>Min</label>
                <input
                  type="number"
                  value={editedAlgorithm.output.min || ''}
                  onChange={(e) =>
                    setEditedAlgorithm({
                      ...editedAlgorithm,
                      output: { ...editedAlgorithm.output, min: Number(e.target.value) },
                    })
                  }
                />
              </div>
              <div className="output-field">
                <label>Max</label>
                <input
                  type="number"
                  value={editedAlgorithm.output.max || ''}
                  onChange={(e) =>
                    setEditedAlgorithm({
                      ...editedAlgorithm,
                      output: { ...editedAlgorithm.output, max: Number(e.target.value) },
                    })
                  }
                />
              </div>
            </>
          )}
        </div>
      </div>

      {/* What-If Testing */}
      <div className="whatif-section">
        <button
          className="btn-whatif"
          onClick={() => setShowWhatIf(!showWhatIf)}
        >
          {showWhatIf ? 'Hide' : 'Show'} What-If Analysis
        </button>

        {showWhatIf && (
          <div className="whatif-panel">
            <h4>Test with Sample Data</h4>
            <div className="whatif-inputs">
              {editedAlgorithm.inputs.map((input) => (
                <div key={input.id} className="whatif-input">
                  <label>{input.name}</label>
                  <input
                    type="number"
                    value={testInputs[input.id] || ''}
                    onChange={(e) =>
                      setTestInputs({
                        ...testInputs,
                        [input.id]: Number(e.target.value),
                      })
                    }
                  />
                </div>
              ))}
            </div>
            <button
              className="btn-primary"
              onClick={() => onWhatIf && onWhatIf(testInputs)}
            >
              Calculate
            </button>
          </div>
        )}
      </div>

      {/* Footer Actions */}
      <div className="editor-footer">
        <button className="btn-secondary" onClick={onCancel}>
          Cancel
        </button>
        <button className="btn-primary" onClick={() => onSave(editedAlgorithm)}>
          Save Changes
        </button>
      </div>

      <style jsx>{`
        .algorithm-editor {
          display: flex;
          flex-direction: column;
          height: 100%;
          padding: 16px;
          overflow-y: auto;
        }

        .editor-header {
          margin-bottom: 16px;
        }

        .algorithm-name-input {
          font-size: 20px;
          font-weight: 600;
          border: none;
          border-bottom: 2px solid transparent;
          padding: 4px 0;
          display: block;
          width: 100%;
        }

        .algorithm-name-input:focus {
          border-bottom-color: #0066cc;
          outline: none;
        }

        .algorithm-id {
          font-size: 12px;
          color: #666;
          font-family: monospace;
        }

        h3 {
          font-size: 14px;
          font-weight: 600;
          margin: 16px 0 8px;
        }

        .steps-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .weight-total {
          font-size: 12px;
          color: #666;
        }

        .step-card {
          border: 1px solid #ddd;
          border-radius: 8px;
          padding: 12px;
          margin-bottom: 8px;
          background: #fafafa;
        }

        .step-header {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 8px;
        }

        .step-number {
          width: 24px;
          height: 24px;
          border-radius: 50%;
          background: #0066cc;
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 12px;
          font-weight: 600;
        }

        .step-name {
          flex: 1;
          font-weight: 500;
          border: none;
          background: transparent;
          padding: 4px;
        }

        .step-weight {
          display: flex;
          align-items: center;
          gap: 4px;
        }

        .step-weight input {
          width: 60px;
          text-align: right;
        }

        .step-description textarea {
          width: 100%;
          border: 1px solid #ddd;
          border-radius: 4px;
          padding: 8px;
          font-size: 13px;
          margin-bottom: 8px;
        }

        .step-formula {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .step-formula label {
          font-size: 12px;
          color: #666;
        }

        .formula-input {
          flex: 1;
          font-family: monospace;
          padding: 8px;
          border: 1px solid #ddd;
          border-radius: 4px;
          background: #f8f9fa;
        }

        .btn-explain {
          width: 24px;
          height: 24px;
          border-radius: 50%;
          border: 1px solid #ddd;
          background: white;
          cursor: pointer;
        }

        .output-config {
          display: flex;
          gap: 16px;
        }

        .output-field {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }

        .output-field label {
          font-size: 12px;
          color: #666;
        }

        .whatif-section {
          margin-top: 16px;
          padding-top: 16px;
          border-top: 1px solid #ddd;
        }

        .btn-whatif {
          padding: 8px 16px;
          background: #f8f9fa;
          border: 1px solid #ddd;
          border-radius: 4px;
          cursor: pointer;
        }

        .whatif-panel {
          margin-top: 12px;
          padding: 12px;
          background: #f8f9fa;
          border-radius: 4px;
        }

        .whatif-inputs {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
          gap: 12px;
          margin-bottom: 12px;
        }

        .whatif-input label {
          display: block;
          font-size: 12px;
          margin-bottom: 4px;
        }

        .whatif-input input {
          width: 100%;
          padding: 8px;
          border: 1px solid #ddd;
          border-radius: 4px;
        }

        .btn-add {
          margin-top: 8px;
          padding: 8px 16px;
          background: white;
          border: 1px dashed #ddd;
          border-radius: 4px;
          cursor: pointer;
        }

        .editor-footer {
          display: flex;
          justify-content: flex-end;
          gap: 8px;
          margin-top: 16px;
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
          background: white;
          border: 1px solid #ddd;
          border-radius: 4px;
          cursor: pointer;
        }

        .inputs-table,
        .description-section textarea,
        .description-section label {
          width: 100%;
        }

        .inputs-table {
          border-collapse: collapse;
        }

        .inputs-table th,
        .inputs-table td {
          padding: 8px;
          text-align: left;
          border-bottom: 1px solid #eee;
        }

        .inputs-table th {
          font-weight: 500;
          background: #f8f9fa;
          font-size: 12px;
        }

        .inputs-table input,
        .inputs-table select {
          width: 100%;
          padding: 4px 8px;
          border: 1px solid #ddd;
          border-radius: 4px;
        }
      `}</style>
    </div>
  );
};

export default AlgorithmEditor;
