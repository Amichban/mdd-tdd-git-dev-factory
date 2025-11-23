'use client'

import React, { useState } from 'react'

interface FormField {
  name: string
  label: string
  type: 'text' | 'number' | 'select' | 'checkbox' | 'date' | 'textarea'
  required?: boolean
  placeholder?: string
  options?: { label: string; value: string }[]
  defaultValue?: string | number | boolean
}

interface FormWidgetProps {
  title: string
  description?: string
  fields: FormField[]
  submitLabel?: string
  onSubmit: (data: Record<string, unknown>) => void
}

export function FormWidget({
  title,
  description,
  fields,
  submitLabel = 'Submit',
  onSubmit
}: FormWidgetProps) {
  const [formData, setFormData] = useState<Record<string, unknown>>(() => {
    const initial: Record<string, unknown> = {}
    fields.forEach(field => {
      if (field.defaultValue !== undefined) {
        initial[field.name] = field.defaultValue
      } else if (field.type === 'checkbox') {
        initial[field.name] = false
      } else {
        initial[field.name] = ''
      }
    })
    return initial
  })

  const [errors, setErrors] = useState<Record<string, string>>({})

  const handleChange = (name: string, value: unknown) => {
    setFormData(prev => ({ ...prev, [name]: value }))
    // Clear error when field is edited
    if (errors[name]) {
      setErrors(prev => {
        const newErrors = { ...prev }
        delete newErrors[name]
        return newErrors
      })
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    // Validate required fields
    const newErrors: Record<string, string> = {}
    fields.forEach(field => {
      if (field.required && !formData[field.name]) {
        newErrors[field.name] = `${field.label} is required`
      }
    })

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors)
      return
    }

    onSubmit(formData)
  }

  const renderField = (field: FormField) => {
    const commonClasses = "w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600"
    const errorClasses = errors[field.name] ? "border-red-500" : "border-gray-300"

    switch (field.type) {
      case 'textarea':
        return (
          <textarea
            id={field.name}
            value={formData[field.name] as string}
            onChange={(e) => handleChange(field.name, e.target.value)}
            placeholder={field.placeholder}
            className={`${commonClasses} ${errorClasses} min-h-[100px]`}
            required={field.required}
          />
        )

      case 'select':
        return (
          <select
            id={field.name}
            value={formData[field.name] as string}
            onChange={(e) => handleChange(field.name, e.target.value)}
            className={`${commonClasses} ${errorClasses}`}
            required={field.required}
          >
            <option value="">Select...</option>
            {field.options?.map(opt => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        )

      case 'checkbox':
        return (
          <div className="flex items-center">
            <input
              type="checkbox"
              id={field.name}
              checked={formData[field.name] as boolean}
              onChange={(e) => handleChange(field.name, e.target.checked)}
              className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
            />
            <label htmlFor={field.name} className="ml-2 text-sm text-gray-700 dark:text-gray-300">
              {field.label}
            </label>
          </div>
        )

      case 'number':
        return (
          <input
            type="number"
            id={field.name}
            value={formData[field.name] as number}
            onChange={(e) => handleChange(field.name, parseFloat(e.target.value) || 0)}
            placeholder={field.placeholder}
            className={`${commonClasses} ${errorClasses}`}
            required={field.required}
          />
        )

      case 'date':
        return (
          <input
            type="date"
            id={field.name}
            value={formData[field.name] as string}
            onChange={(e) => handleChange(field.name, e.target.value)}
            className={`${commonClasses} ${errorClasses}`}
            required={field.required}
          />
        )

      default:
        return (
          <input
            type="text"
            id={field.name}
            value={formData[field.name] as string}
            onChange={(e) => handleChange(field.name, e.target.value)}
            placeholder={field.placeholder}
            className={`${commonClasses} ${errorClasses}`}
            required={field.required}
          />
        )
    }
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
      <h3 className="text-lg font-semibold mb-2">{title}</h3>
      {description && (
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">{description}</p>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        {fields.map(field => (
          <div key={field.name}>
            {field.type !== 'checkbox' && (
              <label
                htmlFor={field.name}
                className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
              >
                {field.label}
                {field.required && <span className="text-red-500 ml-1">*</span>}
              </label>
            )}
            {renderField(field)}
            {errors[field.name] && (
              <p className="mt-1 text-sm text-red-500">{errors[field.name]}</p>
            )}
          </div>
        ))}

        <button
          type="submit"
          className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          {submitLabel}
        </button>
      </form>
    </div>
  )
}

export default FormWidget
