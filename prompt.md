# Prompt: Evolución del Weekly Meal Planner

## Contexto

Tengo una aplicación web estática (`index.html`) que es un planificador semanal de comidas con lista de la compra y recetas. Actualmente todos los datos están hardcodeados en el propio archivo JS y no hay persistencia. Quiero convertirla en una aplicación real.

Consulta `CLAUDE.md` para entender la arquitectura actual antes de empezar.

---

## Objetivo general

Transformar la app en una aplicación con persistencia de datos, banco de recetas externo y generación aleatoria de planes semanales.

---

## Tareas

### 1. Fuente de recetas externa

No vamos a generar recetas nosotros. Quiero que las recetas vengan de una API pública de recetas ya existente. Elige la más adecuada entre estas opciones (en orden de preferencia):

- **TheMealDB** — `https://www.themealdb.com/api.php` — gratuita, sin API key, amplio catálogo, incluye ingredientes por receta
- **Spoonacular** — requiere API key gratuita, más completa
- **Edamam** — requiere API key gratuita

**Recomendación:** usa TheMealDB si es suficiente para cubrir 21 recetas semanales variadas (3 por día × 7 días). Documenta cuál elegiste y por qué.

La app debe ser capaz de obtener recetas aleatorias de esa API para construir el plan semanal. Cada receta debe aportar al menos: nombre, lista de ingredientes con cantidades y pasos de preparación.

---

### 2. Persistencia de datos

Elige el mecanismo de persistencia más adecuado para esta app (sin backend propio). Opciones:

- **`localStorage`** — si la app sigue siendo puramente estática
- **Supabase** (free tier) — si queremos que los datos persistan entre dispositivos
- **Firebase Firestore** — alternativa a Supabase

**Criterio de elección:** si no hay necesidad de sincronización entre dispositivos, `localStorage` es suficiente y mantiene la app sin dependencias de terceros. Si queremos acceso desde móvil y escritorio, Supabase es la mejor opción gratuita.

Documenta la elección y configúrala. Lo que debe persistir:

- El plan semanal actual (qué receta está asignada a cada día y slot)
- La lista de la compra con el estado de cada ítem (marcado / no marcado)
- El banco de recetas cacheado (para no repetir llamadas a la API innecesariamente)

---

### 3. Botón "Refrescar semana"

Añadir un botón prominente en la UI (sugerencia: en el header o junto a los tabs) con el texto **"🔄 Nueva semana"**.

Al pulsarlo debe ocurrir lo siguiente en orden:

1. Hacer llamadas a la API para obtener 21 recetas aleatorias (o seleccionarlas del banco cacheado si ya tenemos suficientes)
2. Asignarlas aleatoriamente al plan semanal (7 días × 3 slots: desayuno, comida, cena), intentando que no se repitan recetas en la misma semana
3. Recalcular la lista de la compra agregando todos los ingredientes de las 21 recetas (eliminando duplicados y sumando cantidades cuando sea posible)
4. Resetear el estado de todos los checkboxes de la lista de la compra
5. Persistir el nuevo estado
6. Re-renderizar las tres secciones: lista de la compra, plan semanal y recetas

Añadir un estado de carga visible mientras se obtienen las recetas de la API (spinner o mensaje).

---

### 4. Eliminar referencias a calorías

Quitar completamente cualquier mención a calorías (`kcal`) de:

- La UI (tarjetas de día, tarjetas de comida, modal de receta, acordeón)
- Los datos y estructuras JS
- El CSS (clases o estilos asociados si los hay)

---

### 5. Adaptar la estructura de datos a la API elegida

La estructura actual de `RECIPES` está hardcodeada. Hay que crear una capa de adaptación que transforme la respuesta de la API al formato interno que usa la app para renderizar. El formato interno mínimo que necesita la app es:

```js
{
  id: string,          // ID único de la receta (puede ser el de la API)
  name: string,        // Nombre
  tipo: string,        // "Desayuno", "Comida" o "Cena" (asignado al randomizar)
  ingredients: [       // Lista de ingredientes
    { qty: string, name: string }
  ],
  steps: string[],     // Array de pasos como strings
  tip: string          // Opcional: si la API no lo provee, omitir o dejar vacío
}
```

---

## Restricciones

- Mantener el diseño visual actual (colores, tipografía, layout). Solo cambios funcionales.
- No introducir frameworks JS (React, Vue, etc.). Vanilla JS.
- Si se usa una API con key, el mecanismo para configurarla debe estar claro y documentado (variable de entorno o constante al inicio del script).
- Actualizar `CLAUDE.md` al terminar reflejando la nueva arquitectura.

---

## Entregables esperados

- `index.html` actualizado con toda la lógica nueva
- `CLAUDE.md` actualizado
- Si se usa Supabase u otro servicio externo: instrucciones de configuración en un apartado nuevo del README