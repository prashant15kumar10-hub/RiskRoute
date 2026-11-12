import {
  buildPptx,
  createDeck,
} from "/skills/pptx/scripts/pptx_builder_runtime.mjs"
import { applyRecipeDeckPlan } from "/skills/pptx/scripts/slide_recipes.mjs"
import fs from "node:fs"

const root = new URL("../", import.meta.url).pathname
const metrics = JSON.parse(fs.readFileSync(`${root}artifacts/metrics.json`, "utf8"))
const cf = JSON.parse(
  fs.readFileSync(`${root}artifacts/counterfactual_summary.json`, "utf8"),
)

const deck = createDeck({ width: 1280, height: 720 })

const slidePlan = [
  {
    recipeId: "cover-image-split",
    content: {
      title: "RiskRoute",
      subtitle: "From delay prediction to feasible action",
      image: { src: `${root}assets/truck_hub.jpg` },
    },
  },
  {
    recipeId: "big-claim",
    content: {
      claim: "What if a delay prediction could also recommend the next action?",
      support: "RiskRoute combines prediction with constrained what-if simulation.",
    },
  },
  {
    recipeId: "process-with-image",
    content: {
      title: "A complete full-stack system",
      image: { src: `${root}assets/control_room.jpg` },
      steps: [
        { title: "React", body: "Responsive frontend" },
        { title: "FastAPI", body: "REST backend" },
        { title: "ML engine", body: "Prediction + what-if" },
        { title: "SQLite", body: "Users + history" },
      ],
    },
  },
  {
    recipeId: "full-bleed-image-title",
    content: {
      image: { src: `${root}assets/highway.jpg` },
      title: "A risk score warns you.\nIt does not tell you what to change.",
    },
  },
  {
    recipeId: "image-left-story",
    content: {
      image: { src: `${root}assets/control_room.jpg` },
      title: "Prediction becomes a decision",
      body: "Smallest allowed change.\nLower predicted risk.",
    },
  },
  {
    recipeId: "process-with-image",
    content: {
      title: "A visible path from shipment to action",
      image: { src: `${root}assets/loading_dock.jpg` },
      steps: [
        { title: "Observe", body: "Shipment conditions" },
        { title: "Predict", body: "Delay probability" },
        { title: "Simulate", body: "Allowed what-if actions" },
        { title: "Recommend", body: "Minimal feasible change" },
      ],
    },
  },
  {
    recipeId: "image-comparison",
    content: {
      title: "Context stays fixed. Operations can change.",
      items: [
        {
          image: { src: `${root}assets/highway.jpg` },
          label: "FIXED CONTEXT",
          caption: "Distance · traffic · weather · driver",
        },
        {
          image: { src: `${root}assets/loading_dock.jpg` },
          label: "ALLOWED ACTIONS",
          caption: "Load less · leave earlier · add buffer",
        },
      ],
    },
  },
  {
    recipeId: "metric-grid",
    content: {
      eyebrow: "Measured results",
      title: "The prototype is accurate enough to test the idea",
      metrics: [
        { value: metrics.roc_auc.toFixed(3), label: "ROC-AUC", highlight: true },
        { value: `${(cf.validity_rate * 100).toFixed(0)}%`, label: "Cases reaching target" },
        { value: `${(cf.constraint_satisfaction_rate * 100).toFixed(0)}%`, label: "Constraint compliance" },
        { value: cf.mean_action_count.toFixed(2), label: "Mean actions changed" },
      ],
    },
  },
  {
    recipeId: "image-evidence-strip",
    content: {
      title: "The recommendation must pass three gates",
      image: { src: `${root}assets/tablet_route.jpg` },
      callouts: [
        { label: "VALID", body: "Crosses the target risk" },
        { label: "FEASIBLE", body: "Preserves fixed context" },
        { label: "MINIMAL", body: "Changes as little as possible" },
      ],
    },
  },
  {
    recipeId: "image-quote",
    content: {
      image: { src: `${root}assets/control_room.jpg` },
      quote:
        `${(cf.validity_rate * 100).toFixed(0)}% reached the target. ` +
        `${(cf.constraint_satisfaction_rate * 100).toFixed(0)}% of returned actions obeyed every constraint.`,
      attribution: "150 high-risk synthetic shipments",
    },
  },
  {
    recipeId: "full-bleed-image-title",
    content: {
      image: { src: `${root}assets/truck_hub.jpg` },
      title: "A reproducible prototype.\nReal shipment data comes next.",
    },
  },
  {
    recipeId: "timeline-clean",
    content: {
      eyebrow: "Publication path",
      title: "From mini-project to publishable study",
      events: [
        { label: "01", title: "Prototype", body: "Working simulator" },
        { label: "02", title: "Validate", body: "Real shipment data" },
        { label: "03", title: "Compare", body: "DiCE and optimization" },
        { label: "04", title: "Study", body: "Planner usefulness" },
      ],
    },
  },
  {
    recipeId: "big-claim",
    content: {
      claim: "Don’t just predict delay.\nShow what can change it.",
      support: "Valid. Feasible. Minimal.",
    },
  },
  {
    recipeId: "full-bleed-image-title",
    content: {
      image: { src: `${root}assets/sunrise_truck.jpg` },
      title: "Thank you",
    },
  },
]

applyRecipeDeckPlan(deck, slidePlan)

await buildPptx(deck, {
  scenePath: `${root}build/presentation.scene.json`,
  outputPath: `${root}docs/RiskRoute_Presentation.pptx`,
  reportPath: `${root}build/presentation.build-report.json`,
  previewDir: `${root}build/presentation-preview`,
  layoutDir: `${root}build/presentation-layout`,
})
