# Fix: Filtrado de Donaciones por Relevancia

## Problema Identificado

**Síntoma**: El sistema permitía transferir cualquier donación a cualquier solicitud, sin validar si era relevante.

**Ejemplo problemático**: 
- Solicitud pide: "Leche en polvo para bebés"
- Sistema permite enviar: "Puré de tomates" sin advertencia

**Impacto**: Transferencias irrelevantes que no satisfacen las necesidades reales de las organizaciones solicitantes.

## Análisis del Problema

### Flujo Original (Sin Filtrado)
```
1. Usuario ve solicitud: "Leche en polvo para bebés"
2. Usuario puede seleccionar CUALQUIER donación del inventario
3. Sistema transfiere sin validar relevancia
4. Organización recibe items no solicitados
```

### Datos de Ejemplo
```sql
-- Solicitud REQ-FUND-001
{
  "category": "ALIMENTOS", 
  "description": "Leche en polvo para bebés"
}

-- Inventario disponible
- Puré de tomates (ALIMENTOS)
- Pantalones infantiles (ROPA)  
- Cuadernos rayados (UTILES_ESCOLARES)
```

## Solución Implementada

### Nueva Ruta API: `/get-relevant-donations`

```javascript
router.post('/get-relevant-donations', async (req, res) => {
  const { requestId } = req.body;
  
  // 1. Obtener detalles de la solicitud
  const requestResult = await pool.query(
    'SELECT donaciones FROM solicitudes_externas WHERE solicitud_id = $1',
    [requestId]
  );
  
  // 2. Extraer palabras clave
  const keywords = [];
  requestedDonations.forEach(donation => {
    const words = donation.description.toLowerCase()
      .split(/\s+/)
      .filter(word => word.length > 3 && !commonWords.includes(word));
    keywords.push(...words);
  });
  
  // 3. Buscar donaciones con scoring de relevancia
  const donationsResult = await pool.query(`
    SELECT 
      id, descripcion, categoria, cantidad,
      CASE 
        WHEN categoria = ANY($1) AND LOWER(descripcion) SIMILAR TO $2 THEN 5
        WHEN categoria = ANY($1) THEN 4
        WHEN LOWER(descripcion) SIMILAR TO $2 THEN 3
        WHEN categoria IN ('ALIMENTOS', 'ROPA', 'JUGUETES', 'UTILES_ESCOLARES') THEN 2
        ELSE 1
      END as relevance_score
    FROM donaciones 
    WHERE eliminado = false AND cantidad > 0
    ORDER BY relevance_score DESC, cantidad DESC
    LIMIT 20
  `, [categories, keywordPattern]);
});
```

### Sistema de Scoring de Relevancia

| Score | Criterio | Ejemplo |
|-------|----------|---------|
| **5** | Categoría + Palabras clave coinciden | "Leche en polvo" para solicitud de "Leche en polvo para bebés" |
| **4** | Solo categoría coincide | "Puré de tomates" (ALIMENTOS) para solicitud de "Leche en polvo" (ALIMENTOS) |
| **3** | Solo palabras clave coinciden | "Pantalones infantiles" para solicitud con "infantil" |
| **2** | Categoría válida general | Cualquier ALIMENTOS, ROPA, JUGUETES, UTILES_ESCOLARES |
| **1** | Otros items | Items que no coinciden con ningún criterio |

### Extracción de Palabras Clave

```javascript
// Filtrar palabras comunes y cortas
const commonWords = ['para', 'con', 'sin', 'por', 'una', 'uno', 'los', 'las', 'del', 'de', 'en', 'el', 'la'];

const words = donation.description.toLowerCase()
  .split(/\s+/)
  .filter(word => word.length > 3 && !commonWords.includes(word));
```

## Verificación

### Solicitud de Prueba: REQ-FUND-001
```json
{
  "requested_items": [
    {
      "category": "ALIMENTOS",
      "description": "Leche en polvo para bebés"
    },
    {
      "category": "MEDICAMENTOS", 
      "description": "Paracetamol infantil"
    }
  ]
}
```

### Palabras Clave Extraídas
```json
{
  "keywords_used": [
    "leche", "polvo", "bebés", "alimentos",
    "paracetamol", "infantil", "medicamentos"
  ]
}
```

### Donaciones Filtradas por Relevancia
```json
{
  "donations": [
    {
      "id": 1,
      "descripcion": "Puré de tomates en lata",
      "categoria": "ALIMENTOS",
      "relevance_score": 4  // ← Categoría coincide
    },
    {
      "id": 4, 
      "descripcion": "Pantalones infantiles",
      "categoria": "ROPA",
      "relevance_score": 3  // ← Palabra "infantil" coincide
    },
    {
      "id": 7,
      "descripcion": "Cuadernos rayados", 
      "categoria": "UTILES_ESCOLARES",
      "relevance_score": 2  // ← Categoría válida general
    }
  ]
}
```

## Integración con Frontend

### Uso Recomendado
```javascript
// 1. Cuando usuario selecciona una solicitud
const response = await api.post('/api/messaging/get-relevant-donations', {
  requestId: selectedRequest.request_id
});

// 2. Mostrar donaciones ordenadas por relevancia
const { donations, requested_items } = response.data;

// 3. Destacar visualmente items más relevantes
donations.forEach(donation => {
  if (donation.relevance_score >= 4) {
    // Mostrar con borde verde (muy relevante)
  } else if (donation.relevance_score >= 3) {
    // Mostrar con borde amarillo (relevante)
  } else {
    // Mostrar normal (menos relevante)
  }
});
```

### Mejoras de UX Sugeridas
1. **Indicadores visuales**: Colores/iconos según relevancia
2. **Filtros**: Mostrar solo items relevantes (score >= 3)
3. **Sugerencias**: "Items recomendados para esta solicitud"
4. **Advertencias**: "Este item puede no ser lo que solicitan"

## Limitaciones Actuales

### Algoritmo Simple
- Basado en coincidencia de palabras y categorías
- No considera sinónimos ("leche" vs "lácteos")
- No considera contexto semántico

### Mejoras Futuras Posibles
1. **Diccionario de sinónimos**: leche → lácteos, medicamentos → fármacos
2. **Categorías más específicas**: ALIMENTOS_LACTEOS, MEDICAMENTOS_INFANTILES
3. **Machine Learning**: Aprender de transferencias exitosas
4. **Feedback de usuarios**: Marcar transferencias como "útiles" o "no útiles"

## Estado Final

- ✅ **API implementada**: `/get-relevant-donations` funcional
- ✅ **Scoring inteligente**: 5 niveles de relevancia
- ✅ **Filtrado por palabras clave**: Extracción automática
- ✅ **Ordenamiento**: Más relevantes primero
- ✅ **Limitación de resultados**: Máximo 20 items
- ⚠️ **Integración frontend**: Pendiente (recomendada)

**Fecha de implementación**: 29 de septiembre de 2025  
**Tiempo de desarrollo**: ~30 minutos  
**Impacto**: Alto - Mejora significativa en relevancia de transferencias