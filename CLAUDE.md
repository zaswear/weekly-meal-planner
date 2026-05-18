# CLAUDE.md — Plan Semanal de Comidas

## Descripción del proyecto

Aplicación web estática (HTML/CSS/JS puro) que genera un plan de comidas semanal aleatorio desde TheMealDB, con lista de la compra auto-generada y persistencia en `localStorage`. Sin dependencias externas ni frameworks. Una sola página, sin backend.

---

## Stack técnico

| Capa | Detalle |
|---|---|
| **Fuente de recetas** | [TheMealDB](https://www.themealdb.com/api.php) — gratuita, sin API key, catálogo amplio |
| **Persistencia** | `localStorage` — sin backend, sin sincronización entre dispositivos |
| **Hosting** | GitHub Pages o cualquier servidor estático |

**Por qué TheMealDB:** gratuita, sin API key, amplio catálogo internacional. Los nombres de recetas e instrucciones vienen en inglés; los labels de la UI (Desayuno, Comida, Cena, etc.) están en español.

**Por qué `localStorage`:** la app es puramente estática y no requiere sincronización entre dispositivos. Sin dependencias de terceros.

---

## Arquitectura

### Estructura del archivo único (`index.html`)

```
index.html
├── <head>        → Fuentes Google (Playfair Display, DM Sans), CSS variables, estilos
├── <header>      → Título, subtítulo, badge decorativo
├── <nav>         → Tabs de navegación + botón "🔄 Nueva semana"
├── <main>
│   ├── #sec-compra   → Lista de la compra con checkboxes y progreso
│   ├── #sec-plan     → Grid semanal (7 días × 3 comidas)
│   └── #sec-recetas  → Acordeón con todas las recetas
├── #loading-overlay  → Overlay con spinner mientras se cargan recetas de la API
├── .modal-overlay    → Modal de receta (abierto al pulsar una comida)
└── <script>      → Constantes + estado + API + persistencia + renderizado
```

---

## Fuente de datos: TheMealDB

**Endpoint usado:** `https://www.themealdb.com/api/json/v1/1/random.php`

- Devuelve una receta aleatoria por llamada
- La app hace ~30 llamadas en paralelo al generar una semana nueva (para obtener 21 únicas)
- Campos usados: `idMeal`, `strMeal`, `strInstructions`, `strIngredient1-20`, `strMeasure1-20`
- No hay prep time, cook time ni calorías disponibles (no se muestran)

---

## Estado de la app

```js
let recipeCache    = [];  // Recetas adaptadas cacheadas (max 100), persiste entre semanas
let currentRecipes = {};  // Recetas de la semana activa {"L-D": recipeObj, ...}
let currentShopping = []; // Lista de la compra generada [{name, qty, category}]
let checkedItems   = new Set(); // Claves "item-N" de ítems marcados
```

### Claves de `currentRecipes`

Formato `DIA-TIPO` igual que antes:
```
L-D  L-C  L-N   (Lunes: Desayuno, Comida, Cena)
M-D  M-C  M-N   (Martes)
X-D  X-C  X-N   (Miércoles)
J-D  J-C  J-N   (Jueves)
V-D  V-C  V-N   (Viernes)
S-D  S-C  S-N   (Sábado)
D-D  D-C  D-N   (Domingo)
```

---

## Persistencia en `localStorage`

| Clave | Contenido |
|---|---|
| `mealplanner_recipes` | `currentRecipes` serializado (JSON) |
| `mealplanner_shopping` | `currentShopping` serializado (JSON) |
| `mealplanner_checked` | Array de claves marcadas serializado (JSON) |
| `mealplanner_cache` | `recipeCache` serializado (JSON), máx. 100 entradas |

Al cargar la página, `loadState()` restaura el último estado. Si no hay datos guardados, se muestra un empty state en cada sección.

---

## Formato interno de receta

```js
{
  id:          "12345",          // ID de TheMealDB
  name:        "Chicken Tikka",  // Nombre (en inglés, viene de la API)
  tipo:        "Desayuno · Lunes", // Asignado al generar la semana
  mealType:    "desayuno",       // "desayuno" | "comida" | "cena"
  ingredients: [                 // Lista de ingredientes de TheMealDB
    { qty: "200g", name: "Chicken" }
  ],
  steps:       ["Step 1...", "Step 2..."], // Instrucciones parseadas
  tip:         "",               // Siempre vacío (TheMealDB no provee tips)
}
```

---

## Funciones principales

| Función | Descripción |
|---|---|
| `generateNewWeek()` | Orquesta la generación: API → adaptar → asignar → shopping → guardar → renderizar |
| `fetchUniqueRawMeals(count, excludeIds)` | Hace llamadas paralelas a TheMealDB y devuelve `count` recetas únicas |
| `adaptMeal(rawMeal)` | Transforma la respuesta cruda de TheMealDB al formato interno |
| `parseSteps(instructions)` | Divide las instrucciones en array de pasos (detecta numeración y párrafos) |
| `categorizeIngredient(name)` | Clasifica un ingrediente en categoría por regex sobre nombre en inglés |
| `buildShoppingFromCurrentRecipes()` | Agrega todos los ingredientes de las 21 recetas, deduplica y categoriza |
| `saveState()` / `loadState()` | Serializa/deserializa todo el estado en `localStorage` |
| `buildShoppingList()` | Renderiza lista de la compra agrupada por categoría |
| `buildWeekGrid()` | Renderiza el grid de 7 columnas con las 3 comidas por día |
| `buildAllRecipes()` | Renderiza acordeón de todas las recetas |
| `openRecipe(id)` | Abre el modal con detalle de la receta (clave "L-D", etc.) |
| `showLoading(active)` | Muestra/oculta el overlay de carga y deshabilita el botón |

---

## Categorías de la lista de la compra

Los ingredientes (en inglés) se clasifican por regex al nombre:

- 🥩 Carnes, pescado y marisco
- 🧀 Lácteos y huevos
- 🥦 Verduras y hortalizas
- 🍎 Frutas
- 🌾 Cereales y legumbres
- 🧴 Salsas y condimentos
- 🌿 Hierbas y especias
- 🍯 Dulces y repostería
- 🛒 Otros

---

## Botón "Nueva semana"

Situado en la barra de navegación (derecha). Al pulsarlo:

1. Muestra overlay de carga con estado visible
2. Usa recetas del caché (mezcladas) si hay ≥ 21; si no, descarga las que falten de TheMealDB
3. Asigna las 21 recetas a los 21 slots (7 días × 3 comidas), intentando no repetir
4. Regenera la lista de la compra a partir de los ingredientes de las 21 recetas
5. Resetea todos los checkboxes
6. Guarda el nuevo estado en `localStorage`
7. Re-renderiza las tres secciones

---

## Sistema de diseño (CSS variables)

```css
--cream:             #fdf8f2   /* Fondo general */
--warm-white:        #fffcf7   /* Fondo de tarjetas */
--terracotta:        #c1502a   /* Color primario (headers, botones activos) */
--terracotta-light:  #e8734a   /* Barra de cena */
--olive:             #5c6b2e   /* Color secundario (barra comida, botón nueva semana) */
--olive-light:       #8a9e45
--sand:              #e8d5b7   /* Fondos suaves, hover */
--sand-dark:         #c9b89a   /* Bordes de ingredientes */
--charcoal:          #2d2416   /* Texto principal */
--text-muted:        #7a6a55   /* Texto secundario */
--border:            #e2d0b8   /* Bordes de tarjetas */
--green-check:       #4a7c59   /* Checkbox marcado */
```

---

## Convenciones de código

- Variables cortas para DOM: `el`, `div`, `card`, `catEl`
- Template literals para todo el HTML generado dinámicamente
- Sin clases JS, todo en funciones sueltas
- Sin librerías externas (solo Google Fonts vía CDN)
- Fuentes: `Playfair Display` para títulos, `DM Sans` para cuerpo
- No hay calorías en ninguna parte (UI, datos, CSS)

---

## Funcionalidad de impresión

La sección `#sec-compra` está optimizada para imprimir via `@media print`. El botón "Imprimir lista" llama a `window.print()`. El resto de la UI queda oculto en impresión.
