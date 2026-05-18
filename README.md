# 🍳 Weekly Meal Planner

> Plan semanal de comidas interactivo con lista de la compra y recetas detalladas. Sin frameworks, sin dependencias, un solo archivo.

![HTML](https://img.shields.io/badge/HTML-E34F26?style=flat&logo=html5&logoColor=white)
![CSS](https://img.shields.io/badge/CSS-1572B6?style=flat&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat&logo=javascript&logoColor=black)
![No dependencies](https://img.shields.io/badge/dependencies-none-brightgreen)

## ✨ Características

- **Lista de la compra interactiva** — checkboxes por categoría, contador de progreso y botón de impresión
- **Plan semanal visual** — grid de 7 días × 3 comidas (desayuno, comida, cena) con calorías por día
- **21 recetas completas** — ingredientes, pasos y consejo de chef para cada comida
- **Modal de receta** — se abre al pulsar cualquier comida del plan
- **Acordeón de recetas** — vista alternativa con todas las recetas expandibles
- **Diseño mediterráneo** — paleta terracota, tipografía editorial, 100% responsive
- **Optimizado para imprimir** — la lista de la compra se imprime limpia

## 🚀 Uso

No hay nada que instalar. Descarga o clona el repositorio y abre `index.html` en el navegador.

```bash
git clone https://github.com/tuusuario/weekly-meal-planner.git
cd weekly-meal-planner
open index.html
```

O usa directamente la versión desplegada en GitHub Pages: `https://tuusuario.github.io/weekly-meal-planner`

## 📁 Estructura

```
weekly-meal-planner/
├── index.html      # App completa (HTML + CSS + JS en un solo archivo)
├── CLAUDE.md       # Documentación técnica para desarrollo con IA
└── README.md
```

## 🔧 Personalización

Todos los datos están en el bloque `<script>` de `index.html`, claramente separados de la lógica:

| Objeto | Qué contiene |
|---|---|
| `SHOPPING` | Categorías e ítems de la lista de la compra |
| `RECIPES` | Las 21 recetas con ingredientes, pasos y consejos |
| `WEEK` | Qué receta corresponde a cada día y tipo de comida |

Consulta [`CLAUDE.md`](./CLAUDE.md) para una guía detallada de modificación.

## 🌐 Deploy en GitHub Pages

1. Ve a **Settings → Pages**
2. Source: `Deploy from a branch`
3. Branch: `main` / `root`
4. La app estará disponible en `https://tuusuario.github.io/weekly-meal-planner`

## 📄 Licencia

MIT