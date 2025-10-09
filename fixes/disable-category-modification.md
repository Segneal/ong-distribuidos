# Fix: Deshabilitar Modificación de Categoría en Donaciones

## 🐛 Problema Identificado

La categoría de las donaciones se podía modificar durante la edición, lo cual no debería ser permitido por razones de integridad de datos y trazabilidad.

## 🔍 Justificación

### ¿Por qué no se debe modificar la categoría?

1. **Integridad de datos**: Cambiar la categoría puede afectar reportes históricos
2. **Trazabilidad**: Es importante mantener la categoría original para auditorías
3. **Consistencia**: Las donaciones deben mantener su clasificación inicial
4. **Reglas de negocio**: Una vez categorizada, la donación debe mantener su tipo

## ✅ Solución Implementada

### 1. Frontend - Campo Deshabilitado

**Archivo**: `frontend/src/components/inventory/DonationForm.jsx`

```jsx
// ✅ Campo deshabilitado en modo edición
<select
  id="category"
  name="category"
  value={formData.category}
  onChange={handleInputChange}
  className={validationErrors.category ? 'error' : ''}
  disabled={loading || donation} // ← Deshabilitar si estamos editando
>
```

### 2. Indicador Visual

```jsx
// ✅ Nota explicativa para el usuario
<label htmlFor="category">
  Categoría <span className="required">*</span>
  {donation && <span className="field-note"> (No modificable)</span>}
</label>
```

### 3. Estilos CSS

**Archivo**: `frontend/src/components/inventory/Inventory.css`

```css
/* Nota para campos deshabilitados */
.field-note {
  font-size: 0.8em;
  color: #666;
  font-weight: normal;
  font-style: italic;
}

/* Estilo para select deshabilitado */
select:disabled {
  background-color: #f5f5f5;
  color: #666;
  cursor: not-allowed;
}
```

### 4. Backend - Seguridad Adicional

**Archivo**: `inventory-service/src/inventory_service.py`

```python
# ✅ Categoría ignorada en actualizaciones
donation = self.repository.update_donation(
    donation_id=request.id,
    description=request.description,
    quantity=request.quantity,
    updated_by=request.updated_by
    # category=category  # ❌ Comentado - no se permite modificar categoría
)
```

**Archivo**: `inventory-service/src/inventory_repository_simple.py`

```python
# ✅ Categoría no se procesa en actualizaciones
if category is not None:
    print(f"REPO: Category update ignored for security: {category}")
    # No agregar categoría a los updates
```

## 🧪 Comportamiento Esperado

### ✅ Creación de Donación (Nuevo)
- ✅ Campo de categoría **habilitado**
- ✅ Usuario puede seleccionar cualquier categoría
- ✅ Categoría es **obligatoria**

### ✅ Edición de Donación (Existente)
- ✅ Campo de categoría **deshabilitado**
- ✅ Muestra la categoría actual (solo lectura)
- ✅ Nota explicativa: "(No modificable)"
- ✅ Usuario puede modificar descripción y cantidad
- ✅ Backend ignora intentos de modificar categoría

## 📊 Impacto

### Seguridad
- **Integridad de datos**: Previene modificaciones accidentales de categoría
- **Consistencia**: Mantiene la clasificación original de las donaciones
- **Auditoría**: Preserva la trazabilidad de las categorías

### UX/UI
- **Claridad**: El usuario entiende que la categoría no se puede cambiar
- **Feedback visual**: Campo deshabilitado con nota explicativa
- **Consistencia**: Comportamiento predecible entre creación y edición

## 🔧 Archivos Modificados

1. **frontend/src/components/inventory/DonationForm.jsx**
   - Campo categoría deshabilitado en modo edición
   - Nota explicativa agregada

2. **frontend/src/components/inventory/Inventory.css**
   - Estilos para campo deshabilitado y nota

3. **inventory-service/src/inventory_service.py**
   - Categoría ignorada en actualizaciones

4. **inventory-service/src/inventory_repository_simple.py**
   - Lógica de seguridad para ignorar categoría

## 🎯 Estado Final

✅ **Creación**: Categoría seleccionable y obligatoria
✅ **Edición**: Categoría no modificable (deshabilitada)
✅ **Seguridad**: Backend ignora intentos de modificar categoría
✅ **UX**: Usuario informado sobre la restricción

---

**Fecha**: 2025-10-02
**Severidad**: Media - Integridad de datos
**Estado**: ✅ Resuelto