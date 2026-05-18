# Weekly Meal Planner

> Plan semanal de comidas interactivo con lista de la compra automática y recetas detalladas. Sin frameworks, sin dependencias externas, un solo archivo HTML.

![HTML](https://img.shields.io/badge/HTML-E34F26?style=flat&logo=html5&logoColor=white)
![CSS](https://img.shields.io/badge/CSS-1572B6?style=flat&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat&logo=javascript&logoColor=black)
![No dependencies](https://img.shields.io/badge/dependencies-none-brightgreen)

## Características

- **Plan semanal generado al azar** — 7 días × 2 turnos (comida + cena), sin repetir receta
- **1097 recetas en español** — base de datos local extraída de Arguiñano y El Comidista
- **Lista de la compra automática** — se genera a partir de los ingredientes de la semana, agrupada por categorías con checkboxes y contador de progreso
- **Modal de receta** — ingredientes con cantidades y pasos de elaboración al pulsar cualquier comida
- **Acordeón de recetas** — vista alternativa con todas las recetas de la semana expandibles
- **Persistencia en localStorage** — el plan y la lista de la compra se guardan entre sesiones
- **Diseño mediterráneo** — paleta terracota, tipografía editorial, 100% responsive
- **Optimizado para imprimir** — la lista de la compra se imprime limpia

## Uso

No hay nada que instalar. Clona el repositorio y abre `index.html` en el navegador.

```bash
git clone https://github.com/zaswear/weekly-meal-planner.git
cd weekly-meal-planner
open index.html   # o arrastra index.html al navegador
```

Al cargar, si hay un plan guardado se restaura. El botón **Nueva semana** genera un plan completamente nuevo con recetas aleatorias.

## Estructura

```
weekly-meal-planner/
├── index.html          # App completa (HTML + CSS + JS en un solo archivo)
├── recetas.json        # Base de datos local: 1097 recetas en español
├── parse_recipes.py    # Script Python para regenerar recetas.json desde los markdown fuente
├── CLAUDE.md           # Documentación técnica para desarrollo con IA
└── README.md
```

## Base de datos de recetas

Las recetas se sirven desde `recetas.json` — un fichero estático generado por `parse_recipes.py` a partir de los libros de cocina en formato markdown. Cada receta tiene la estructura:

```json
{
  "id": "r0001",
  "name": "Nombre de la receta",
  "ingredients": [
    { "qty": "200 g", "name": "pollo" }
  ],
  "steps": ["Paso 1...", "Paso 2..."],
  "tip": ""
}
```

Para regenerar la base de datos desde nuevos ficheros fuente, coloca los markdown en la carpeta `recetas/` y ejecuta:

```bash
python3 parse_recipes.py
```

## Estado en localStorage

| Clave | Contenido |
|---|---|
| `mealplanner_recipes` | Plan de la semana actual (`{ "L-C": {...}, "L-N": {...}, ... }`) |
| `mealplanner_shopping` | Lista de la compra generada |
| `mealplanner_checked` | Ítems marcados como comprados |

Para resetear completamente: abre la consola del navegador y ejecuta `localStorage.clear()`.

## Deploy en GitHub Pages

1. Ve a **Settings → Pages**
2. Source: `Deploy from a branch`
3. Branch: `main` / raíz `/`
4. La app estará disponible en `https://zaswear.github.io/weekly-meal-planner`

## Licencia

MIT
