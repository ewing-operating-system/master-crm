import { useState } from "react";

// ════════════════════════════════════════════════════════════════
// DESIGN PRECAST & PIPE — BUY-SIDE TARGET CRITERIA
// Populated from: 14 Fireflies transcripts, 70+ emails (cfore@designprecast.com)
// ════════════════════════════════════════════════════════════════

// ─── COLOR SYSTEM ───
const colors = {
  navy: "#0F1A2E",
  navyLight: "#1B2A45",
  slate: "#334155",
  accent: "#2563EB",
  accentLight: "#3B82F6",
  accentGlow: "#60A5FA",
  gold: "#D4A843",
  goldLight: "#E5C36B",
  concrete: "#6B7280",
  concreteLight: "#9CA3AF",
  surface: "#FFFFFF",
  surfaceMuted: "#F8FAFC",
  surfaceDark: "#F1F5F9",
  border: "#E2E8F0",
  borderLight: "#F1F5F9",
  textPrimary: "#0F172A",
  textSecondary: "#475569",
  textMuted: "#94A3B8",
  green: "#059669",
  greenBg: "#ECFDF5",
  greenLight: "#D1FAE5",
  red: "#DC2626",
  redBg: "#FEF2F2",
  amber: "#D97706",
  amberBg: "#FFFBEB",
  amberLight: "#FEF3C7",
};

const fonts = {
  heading: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
  body: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
  mono: "'JetBrains Mono', 'Fira Code', monospace",
};

// ════════════════════════════════════════════════════════════════
// CONFIG — DESIGN PRECAST & PIPE (Chris Fore)
// Sources: Fireflies transcripts (14), Gmail (70+ emails to/from cfore@designprecast.com)
// ════════════════════════════════════════════════════════════════
const CONFIG = {
  client: {
    companyName: "Design Precast & Pipe",
    contactName: "Chris Fore",
    contactTitle: "Owner / CEO",
    contactEmail: "cfore@designprecast.com",
    headquarters: "Mississippi",
    currentPlants: "1+",
    currentStates: "MS",
    strategy: "Platform + Bolt-On (Debt-Funded, PE Later)",
    advisorEngaged: "Yes — Next Chapter Advisory",
    priorAcquisitions: "0 (building platform for first)",
    dateUpdated: "2026-03-29",
  },

  products: {
    mustHave: [
      { name: "Storm & Sewer Pipe", description: "RCP (reinforced concrete pipe), elliptical, arch pipe for storm and sanitary sewer systems" },
      { name: "Drainage Products", description: "Catch basins, drop inlets, junction boxes, drainage structures" },
      { name: "Utility Precast", description: "Manholes, utility vaults, pull boxes, underground utility structures" },
      { name: "Underground Infrastructure", description: "Any precast serving underground storm, sewer, or utility applications" },
      { name: "Box Culverts", description: "Precast box culverts for drainage crossings and stormwater conveyance" },
    ],
    niceToHave: [
      { name: "Retaining Walls", description: "Segmental or gravity retaining wall systems (if paired with underground)" },
      { name: "Sound/Noise Walls", description: "Highway noise barrier panels" },
      { name: "Septic Tanks", description: "Residential and commercial septic systems" },
      { name: "Headwalls & Endwalls", description: "Pipe termination structures" },
      { name: "Custom Precast", description: "Engineered-to-order specialty structures for DOT or municipal specs" },
    ],
    excluded: [
      { name: "Architectural Precast Only", description: "Companies whose primary revenue is architectural facades, cladding, panels — NOT underground" },
      { name: "Contractors / Installers", description: "Companies that install but don't manufacture precast" },
      { name: "Chemical Companies", description: "Admixture, sealant, or chemical supply businesses" },
      { name: "Form Manufacturers", description: "Companies that build the molds/forms, not the precast itself" },
      { name: "Wall-Manufacturer Only", description: "Companies that ONLY make retaining walls with no underground products" },
      { name: "PCI-Focused Prestressed", description: "Companies focused solely on prestressed structural (bridges, beams, double-tees) with zero underground overlap" },
    ],
    minimumOverlapPct: "40%",
    notes: "Chris is explicit: minimum 40% of target's revenue must be in underground precast (storm, sewer, utility). Architectural-only is a hard no. Wall-only is a hard no. The target must have meaningful overlap with Design Precast's core underground product lines.",
  },

  geography: {
    primaryStates: ["MS", "AL", "GA", "SC", "NC", "TN"],
    secondaryStates: ["East TX", "Savannah area (GA)", "FL Panhandle"],
    excludedStates: ["AR"],
    maxShipRadius: "150–300",
    densityPreference: "Mix — municipal & DOT markets in both metro and rural",
    notes: "Southeast focus. Savannah GA flagged as high priority. Chris specifically requested Lee's Precast in North MS. Not as interested in AR. FL and GA searches mostly returned contractors, not manufacturers. East TX is secondary.",
  },

  financials: {
    ebitdaMin: "$1M",
    ebitdaMax: "$5M",
    revenueMin: "$5M",
    revenueMax: "$30M",
    ebitdaMarginMin: "15%",
    multipleRange: "4x–7x EBITDA",
    maxMultiple: "8x (walk-away above this)",
    debtFunded: "Yes — debt-funded acquisitions",
    equityPartner: "PE later (not for initial platform)",
    notes: "Chris wants to build the platform with debt first, then potentially bring in PE for accelerated roll-up. Target EBITDA of $1M–$5M. Fee structure with Next Chapter: 2% on existing pipeline deals, 2.5% on new sourced deals, $30K retainer with 90-day option.",
  },

  dealStructure: {
    acquisitionType: "100% buyout (platform), majority for bolt-ons",
    ownerTransition: "Flexible — owner can stay or exit",
    earnoutAcceptable: "Yes",
    sellerFinancingAcceptable: "Yes",
    teamRetention: "Required",
    retentionMethod: "Retention bonuses, key-man agreements",
    holdPeriod: "Long-term (building permanent platform)",
    rollupIntent: "Yes — Southeast precast consolidation play",
    notes: "Platform strategy: acquire first anchor, then bolt on 3-5 additional plants across the Southeast. Chris has deep industry knowledge and will be hands-on operator. Intent is to build a regional precast powerhouse, then potentially bring in PE capital.",
  },

  certifications: {
    required: [
      { name: "NPCA Plant Certification", description: "National Precast Concrete Association — Chris says this is 'damn near required.' Recognized by 40+ states." },
      { name: "ACPA Quality Cast", description: "American Concrete Pipe Association — critical for pipe-focused plants. Chris considers this nearly mandatory." },
    ],
    preferred: [
      { name: "State DOT Approval", description: "Approved supplier lists for state DOTs in target geography (MS, AL, GA, SC, NC, TN)" },
      { name: "ASTM Compliance", description: "Meeting ASTM C76, C478, C506, C507 and related standards for concrete pipe and manholes" },
    ],
    excluded: [
      { name: "PCI Plant Certification", description: "Chris explicitly stated: 'NOT interested in PCI plant certification.' PCI is for prestressed structural, not his market." },
    ],
    dotApproval: "Required — must be on state DOT approved lists",
    stateSpecific: "MS, AL, GA DOT approved supplier status preferred",
    notes: "NPCA or ACPA certification is 'damn near required' per Chris. PCI is explicitly excluded — that's a different market (prestressed structural like bridge beams and double-tees). DOT approval in target states is a major plus since much of the underground market is publicly funded.",
  },

  facility: {
    minPlantSqFt: "15,000+",
    outdoorYardRequired: "Yes — substantial yard for curing and inventory staging",
    craneCapacity: "10+ tons",
    batchPlantRequired: "Yes — on-site batch plant strongly preferred",
    ageMaxYears: "No hard limit — condition matters more than age",
    environmentalConcerns: "Clean environmental history preferred; washout water management important",
    deliveryFleet: "Owned fleet preferred — delivery is a competitive differentiator in precast",
    notes: "Precast plants need significant outdoor yard space for curing, inventory, and staging. Delivery fleet is important because precast products are heavy and shipping radius is limited. A plant with its own trucks has a major competitive advantage.",
  },

  workforce: {
    minEmployees: "15",
    maxEmployees: "150",
    keyRolesRequired: ["Plant Manager/Superintendent", "QC Manager", "Batch Plant Operator", "Estimator/Sales", "Delivery Drivers"],
    laborMarketConcerns: "Non-union preferred but not required",
    technicianRetention: "Critical — experienced precast workers are hard to replace",
    safetyRecord: "Clean OSHA history required; precast has heavy-lift safety risks",
    notes: "Workforce is a key value driver. Experienced plant crews that can produce quality precast to spec are hard to find and train. Retention of key personnel is non-negotiable in any deal.",
  },

  customers: {
    minCustomerCount: "20+",
    maxConcentration: "25% max single customer",
    preferredEndMarkets: [
      "Municipal storm/sewer infrastructure",
      "State DOT highway drainage",
      "Commercial site development",
      "Residential subdivision infrastructure",
      "Water/wastewater treatment facilities",
      "Data center site infrastructure",
      "Industrial facility drainage",
    ],
    contractType: "Project-based with repeat municipal/DOT relationships",
    backlogRequired: "Yes — 3+ months preferred",
    govtContractPct: "40–60% preferred (municipal + DOT)",
    notes: "Underground precast is heavily driven by public infrastructure spending. A healthy mix of municipal, DOT, and private development customers reduces cyclicality. IIJA funding is a major tailwind for DOT and municipal drainage projects through 2026+.",
  },

  dealBreakers: [
    "Architectural precast only — no underground products",
    "No NPCA or ACPA certification and unwilling to pursue",
    "Zoning issues that prevent plant expansion or continued operation",
    "Severe environmental contamination or cleanup liability",
    "Owner is a contractor/installer, not a manufacturer",
    "Product mix is 60%+ wall systems with minimal underground",
    "Company is a form/mold manufacturer, not a precast producer",
    "Chemical/admixture company misclassified as precast",
    "Less than 40% revenue overlap in underground precast products",
    "Facility in state outside Southeast target geography",
  ],

  namedTargets: [
    { name: "Triple M Precast", location: "Southeast US", status: "active", priority: 1, notes: "Identified in pipeline" },
    { name: "Precast Solutions NC", location: "North Carolina", status: "active", priority: 1, notes: "NC market entry" },
    { name: "Georgia Concrete & Precast", location: "Georgia", status: "active", priority: 1, notes: "GA market presence" },
    { name: "Lee's Precast", location: "North Mississippi", status: "active", priority: 1, notes: "Chris specifically requested — North MS target" },
    { name: "Piedmont Precast", location: "Piedmont region (NC/SC/VA)", status: "active", priority: 2, notes: "Carolinas footprint" },
    { name: "Jarrett Precast", location: "Southeast US", status: "active", priority: 2, notes: "In pipeline scoring" },
    { name: "Gossett Concrete Pipe", location: "Southeast US", status: "active", priority: 2, notes: "Concrete pipe specialist" },
    { name: "Select Precast / KK Ausbon", location: "Southeast US", status: "active", priority: 2, notes: "Two linked entities" },
    { name: "Panhandle Precast", location: "FL Panhandle / AL", status: "active", priority: 3, notes: "Gulf Coast coverage" },
  ],

  marketContext: {
    industrySize: "$160B+ global precast concrete market (2025)",
    growthRate: "4.2–6.3% CAGR through 2030-2034",
    keyDrivers: [
      "IIJA infrastructure spending ($1.2T through 2026+) — direct demand driver for storm/sewer pipe and drainage",
      "Data center construction boom (+138% YOY to $53.7B) — site infrastructure needs precast drainage",
      "Buy America / BABA domestic manufacturing mandates — must be made in USA for federal projects",
      "Aging municipal water and sewer infrastructure — EPA estimates $271B needed for wastewater infrastructure",
      "Highway and bridge rehabilitation programs — DOT drainage replacement projects",
      "Stormwater management regulatory expansion — MS4 permits driving precast demand",
      "Southeast population growth — FL, GA, NC, SC, TN leading in new housing and commercial development",
    ],
    ebitdaMultiples: {
      buildingMaterials_0_1M: "5.4x",
      buildingMaterials_1_3M: "7.3x",
      buildingMaterials_3_5M: "9.8x",
      civilEngineering_0_1M: "6.8x",
      civilEngineering_1_3M: "8.7x",
      civilEngineering_3_5M: "11.9x",
      peAverage: "10.6x",
      strategicAverage: "7.5x",
    },
    recentDeals: [
      { buyer: "CMC (Commercial Metals)", target: "Foley Products", value: "$1.84B", multiple: "10.3x EBITDA", year: 2025 },
      { buyer: "CMC", target: "Concrete Pipe & Precast (CP&P)", value: "Undisclosed", multiple: "~10x est.", year: 2025 },
      { buyer: "CP&P (pre-CMC)", target: "Dellinger / Winchester / Precast Supply", value: "Undisclosed", multiple: "N/A", year: 2024 },
      { buyer: "NWPX Infrastructure", target: "Boughton's Precast", value: "Undisclosed", multiple: "N/A", year: 2026 },
    ],
    constructionMATrends: {
      totalDeals2025: 562,
      yoyGrowth: "+18.2%",
      peBuyerShare: "54.3%",
      newPlatforms: 68,
      sponsorAddOns: 237,
    },
    certificationLandscape: {
      npca: "NPCA Plant Certification — recognized by 40+ states, 75+ municipalities. ANSI-accredited (ISO/IEC 17065). Annual inspections by independent engineering firms. Chris considers this 'damn near required.'",
      acpa: "ACPA Quality Cast — American Concrete Pipe Association certification for pipe-specific plants. Critical for Design Precast's core market.",
      pci: "PCI (Prestressed Concrete Institute) — for prestressed/precast structural products. Chris explicitly NOT interested in PCI-certified-only plants.",
    },
  },

  // ─── PIPELINE STATS (from email data) ───
  pipelineStats: {
    totalScored: 470,
    narrowedTo: 200,
    activated: 49,
    chrisCutTo: 31,
    notes: "Chris personally reviewed and cut 297 targets down to 31 after the pipeline was scored and filtered. This is a highly curated, hands-on approach.",
  },
};

// ════════════════════════════════════════════════════════════════
// COMPONENTS (same as master template)
// ════════════════════════════════════════════════════════════════

const SectionDivider = ({ title, subtitle, icon }) => (
  <div style={{ marginBottom: 32, paddingBottom: 16, borderBottom: `2px solid ${colors.border}` }}>
    <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
      {icon && <span style={{ fontSize: 24 }}>{icon}</span>}
      <div>
        <h2 style={{ margin: 0, fontSize: 22, fontWeight: 700, fontFamily: fonts.heading, color: colors.navy }}>{title}</h2>
        {subtitle && <p style={{ margin: "4px 0 0", fontSize: 14, color: colors.textSecondary, fontFamily: fonts.body }}>{subtitle}</p>}
      </div>
    </div>
  </div>
);

const CriteriaCard = ({ label, value, subtext, status }) => {
  const statusColors = { set: { bg: colors.greenBg, border: colors.green, dot: colors.green }, partial: { bg: colors.amberBg, border: colors.amber, dot: colors.amber }, unset: { bg: colors.surfaceDark, border: colors.border, dot: colors.textMuted } };
  const s = statusColors[status] || statusColors.unset;
  return (
    <div style={{ background: colors.surface, border: `1px solid ${colors.border}`, borderRadius: 10, padding: "16px 20px", display: "flex", flexDirection: "column", gap: 6, borderLeft: `4px solid ${s.border}` }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span style={{ fontSize: 12, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em", color: colors.textMuted, fontFamily: fonts.body }}>{label}</span>
        <span style={{ width: 8, height: 8, borderRadius: "50%", background: s.dot }} />
      </div>
      <span style={{ fontSize: 18, fontWeight: 700, color: colors.textPrimary, fontFamily: fonts.mono }}>{value || "—"}</span>
      {subtext && <span style={{ fontSize: 13, color: colors.textSecondary }}>{subtext}</span>}
    </div>
  );
};

const TagList = ({ items, color, emptyText }) => {
  if (!items || items.length === 0) return <span style={{ fontSize: 13, color: colors.textMuted, fontStyle: "italic" }}>{emptyText || "None specified"}</span>;
  return (
    <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
      {items.map((item, i) => (
        <span key={i} style={{
          display: "inline-block", padding: "6px 14px", borderRadius: 20, fontSize: 13, fontWeight: 500, fontFamily: fonts.body,
          background: color === "green" ? colors.greenBg : color === "red" ? colors.redBg : color === "amber" ? colors.amberBg : colors.surfaceDark,
          color: color === "green" ? colors.green : color === "red" ? colors.red : color === "amber" ? colors.amber : colors.textSecondary,
          border: `1px solid ${color === "green" ? colors.greenLight : color === "red" ? "#FECACA" : color === "amber" ? colors.amberLight : colors.border}`,
        }}>
          {typeof item === "string" ? item : item.name}
        </span>
      ))}
    </div>
  );
};

const ProductRow = ({ item, type }) => {
  const typeColors = { must: colors.green, nice: colors.accent, excluded: colors.red };
  const typeLabels = { must: "REQUIRED", nice: "PREFERRED", excluded: "EXCLUDED" };
  return (
    <div style={{ display: "flex", alignItems: "flex-start", gap: 14, padding: "12px 0", borderBottom: `1px solid ${colors.borderLight}` }}>
      <span style={{ fontSize: 10, fontWeight: 700, padding: "3px 8px", borderRadius: 4, background: type === "must" ? colors.greenBg : type === "excluded" ? colors.redBg : colors.surfaceDark, color: typeColors[type], letterSpacing: "0.05em", whiteSpace: "nowrap", marginTop: 2 }}>{typeLabels[type]}</span>
      <div>
        <div style={{ fontWeight: 600, fontSize: 14, color: colors.textPrimary }}>{item.name}</div>
        {item.description && <div style={{ fontSize: 13, color: colors.textSecondary, marginTop: 2 }}>{item.description}</div>}
      </div>
    </div>
  );
};

const StateMap = ({ primary, secondary, excluded }) => (
  <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
    <div>
      <div style={{ fontSize: 12, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em", color: colors.green, marginBottom: 8 }}>Primary Markets</div>
      <TagList items={primary} color="green" emptyText="No primary states set" />
    </div>
    <div>
      <div style={{ fontSize: 12, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em", color: colors.accent, marginBottom: 8 }}>Secondary Markets</div>
      <TagList items={secondary} color="default" emptyText="No secondary states set" />
    </div>
    {excluded && excluded.length > 0 && (
      <div>
        <div style={{ fontSize: 12, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em", color: colors.red, marginBottom: 8 }}>Excluded</div>
        <TagList items={excluded} color="red" />
      </div>
    )}
  </div>
);

const TargetRow = ({ target, index }) => {
  const statusStyles = { active: { bg: colors.greenBg, color: colors.green, label: "ACTIVE" }, contacted: { bg: colors.amberBg, color: colors.amber, label: "CONTACTED" }, passed: { bg: colors.redBg, color: colors.red, label: "PASSED" }, LOI: { bg: "#EDE9FE", color: "#7C3AED", label: "LOI" }, watching: { bg: colors.surfaceDark, color: colors.textSecondary, label: "WATCHING" } };
  const s = statusStyles[target.status] || statusStyles.watching;
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 16, padding: "14px 20px", background: index % 2 === 0 ? colors.surface : colors.surfaceMuted, borderBottom: `1px solid ${colors.borderLight}` }}>
      <span style={{ fontFamily: fonts.mono, fontSize: 13, color: colors.textMuted, width: 24, textAlign: "right" }}>{target.priority || "—"}</span>
      <div style={{ flex: 1 }}>
        <div style={{ fontWeight: 600, fontSize: 14, color: colors.textPrimary }}>{target.name}</div>
        <div style={{ fontSize: 13, color: colors.textSecondary }}>{target.location}</div>
      </div>
      <span style={{ fontSize: 10, fontWeight: 700, padding: "3px 10px", borderRadius: 4, background: s.bg, color: s.color, letterSpacing: "0.05em" }}>{s.label}</span>
      {target.notes && <span style={{ fontSize: 12, color: colors.textMuted, maxWidth: 200, textAlign: "right" }}>{target.notes}</span>}
    </div>
  );
};

const DealRow = ({ deal }) => (
  <div style={{ display: "flex", alignItems: "center", gap: 16, padding: "12px 0", borderBottom: `1px solid ${colors.borderLight}` }}>
    <div style={{ flex: 1 }}>
      <div style={{ fontWeight: 600, fontSize: 14, color: colors.textPrimary }}>{deal.buyer}</div>
      <div style={{ fontSize: 13, color: colors.textSecondary }}>acquired {deal.target}</div>
    </div>
    <span style={{ fontFamily: fonts.mono, fontSize: 14, fontWeight: 600, color: colors.accent }}>{deal.value}</span>
    <span style={{ fontFamily: fonts.mono, fontSize: 13, color: colors.textSecondary }}>{deal.multiple}</span>
    <span style={{ fontSize: 12, color: colors.textMuted }}>{deal.year}</span>
  </div>
);

const MultipleBar = ({ label, low, high, highlight }) => {
  const maxVal = 14;
  const leftPct = (parseFloat(low) / maxVal) * 100;
  const widthPct = ((parseFloat(high) - parseFloat(low)) / maxVal) * 100;
  return (
    <div style={{ marginBottom: 12 }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
        <span style={{ fontSize: 13, fontWeight: 500, color: colors.textPrimary }}>{label}</span>
        <span style={{ fontFamily: fonts.mono, fontSize: 13, color: colors.textSecondary }}>{low}x – {high}x</span>
      </div>
      <div style={{ height: 8, background: colors.surfaceDark, borderRadius: 4, position: "relative" }}>
        <div style={{ position: "absolute", left: `${leftPct}%`, width: `${widthPct}%`, height: "100%", background: highlight ? `linear-gradient(90deg, ${colors.gold}, ${colors.accent})` : colors.concreteLight, borderRadius: 4 }} />
      </div>
    </div>
  );
};

const NotesBox = ({ notes }) => {
  if (!notes || notes.startsWith("{{")) return null;
  return (
    <div style={{ background: colors.surfaceMuted, border: `1px solid ${colors.border}`, borderRadius: 8, padding: "12px 16px", marginTop: 16, fontSize: 13, color: colors.textSecondary, fontStyle: "italic", lineHeight: 1.6 }}>{notes}</div>
  );
};

// ════════════════════════════════════════════════════════════════
const TABS = [
  { id: "overview", label: "Overview" },
  { id: "products", label: "Products" },
  { id: "geography", label: "Geography" },
  { id: "financials", label: "Financials" },
  { id: "deal", label: "Deal Structure" },
  { id: "facility", label: "Facility" },
  { id: "certs", label: "Certifications" },
  { id: "targets", label: "Targets" },
  { id: "market", label: "Market Intel" },
];

export default function DesignPrecastCriteria() {
  const [activeTab, setActiveTab] = useState("overview");
  const [expandedBreakers, setExpandedBreakers] = useState(false);
  const c = CONFIG;

  const isSet = (v) => v && !v.startsWith("{{");
  const statusOf = (v) => isSet(v) ? "set" : "unset";

  const OverviewTab = () => (
    <div>
      <SectionDivider title="Client Overview" subtitle="Buyer profile and acquisition strategy" icon="🏗️" />
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 16, marginBottom: 32 }}>
        <CriteriaCard label="Company" value={c.client.companyName} status="set" />
        <CriteriaCard label="Contact" value={c.client.contactName} subtext={c.client.contactTitle} status="set" />
        <CriteriaCard label="Email" value={c.client.contactEmail} status="set" />
        <CriteriaCard label="Headquarters" value={c.client.headquarters} status="set" />
        <CriteriaCard label="Strategy" value={c.client.strategy} status="set" />
        <CriteriaCard label="Prior Acquisitions" value={c.client.priorAcquisitions} status="set" />
        <CriteriaCard label="Advisor" value={c.client.advisorEngaged} status="set" />
        <CriteriaCard label="Last Updated" value={c.client.dateUpdated} status="set" />
      </div>

      {/* Pipeline Stats */}
      <SectionDivider title="Pipeline Stats" subtitle="Target funnel from scoring to activation" icon="📊" />
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: 16, marginBottom: 32 }}>
        {[
          { label: "Total Scored", value: c.pipelineStats.totalScored, color: colors.textSecondary },
          { label: "Narrowed To", value: c.pipelineStats.narrowedTo, color: colors.accent },
          { label: "Activated", value: c.pipelineStats.activated, color: colors.amber },
          { label: "Chris Cut To", value: c.pipelineStats.chrisCutTo, color: colors.green },
        ].map((s, i) => (
          <div key={i} style={{ background: colors.surface, border: `1px solid ${colors.border}`, borderRadius: 10, padding: "20px", textAlign: "center" }}>
            <div style={{ fontSize: 32, fontWeight: 800, fontFamily: fonts.mono, color: s.color }}>{s.value}</div>
            <div style={{ fontSize: 12, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em", color: colors.textMuted, marginTop: 4 }}>{s.label}</div>
          </div>
        ))}
      </div>

      <SectionDivider title="Criteria Summary" subtitle="All sections fully populated" icon="📋" />
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 16 }}>
        {[
          { label: "Products", items: c.products.mustHave.length, desc: `${c.products.mustHave.length} required, ${c.products.niceToHave.length} preferred, ${c.products.excluded.length} excluded` },
          { label: "Geography", items: c.geography.primaryStates.length, desc: `${c.geography.primaryStates.length} primary states, ${c.geography.secondaryStates.length} secondary` },
          { label: "EBITDA Range", items: 1, desc: `${c.financials.ebitdaMin} – ${c.financials.ebitdaMax}` },
          { label: "Deal Structure", items: 1, desc: c.dealStructure.acquisitionType },
          { label: "Certifications", items: c.certifications.required.length, desc: `${c.certifications.required.length} required, ${c.certifications.preferred.length} preferred` },
          { label: "Named Targets", items: c.namedTargets.length, desc: `${c.namedTargets.filter(t => t.status === "active").length} active` },
          { label: "Deal Breakers", items: c.dealBreakers.length, desc: `${c.dealBreakers.length} hard stops` },
        ].map((s, i) => (
          <div key={i} style={{ background: colors.surface, border: `1px solid ${colors.border}`, borderRadius: 10, padding: "16px 20px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <div style={{ fontWeight: 600, fontSize: 15, color: colors.textPrimary }}>{s.label}</div>
              <div style={{ fontSize: 13, color: colors.textSecondary, marginTop: 2 }}>{s.desc}</div>
            </div>
            <div style={{ width: 36, height: 36, borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", background: s.items > 0 ? colors.greenBg : colors.surfaceDark, color: s.items > 0 ? colors.green : colors.textMuted, fontWeight: 700, fontSize: 14, fontFamily: fonts.mono }}>{s.items}</div>
          </div>
        ))}
      </div>

      {c.dealBreakers.length > 0 && (
        <div style={{ marginTop: 32 }}>
          <div onClick={() => setExpandedBreakers(!expandedBreakers)} style={{ cursor: "pointer" }}>
            <SectionDivider title={`Deal Breakers (${expandedBreakers ? "collapse" : "expand"})`} subtitle="Hard stops — any one kills the deal" icon="🚫" />
          </div>
          {expandedBreakers && (
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {c.dealBreakers.map((b, i) => (
                <div key={i} style={{ background: colors.redBg, border: `1px solid #FECACA`, borderRadius: 8, padding: "12px 16px", fontSize: 14, color: colors.red, fontWeight: 500 }}>{b}</div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );

  const ProductsTab = () => (
    <div>
      <SectionDivider title="Product Criteria" subtitle="What the target must manufacture" icon="🧱" />
      <div style={{ marginBottom: 24 }}>
        <CriteriaCard label="Minimum Product Overlap" value={c.products.minimumOverlapPct} subtext="of target's revenue must be in buyer's core underground products" status="set" />
      </div>
      <div style={{ marginBottom: 24 }}>
        <h3 style={{ fontSize: 16, fontWeight: 600, color: colors.green, marginBottom: 12 }}>Must-Have Products</h3>
        {c.products.mustHave.map((p, i) => <ProductRow key={i} item={p} type="must" />)}
      </div>
      <div style={{ marginBottom: 24 }}>
        <h3 style={{ fontSize: 16, fontWeight: 600, color: colors.accent, marginBottom: 12 }}>Nice-to-Have Products</h3>
        {c.products.niceToHave.map((p, i) => <ProductRow key={i} item={p} type="nice" />)}
      </div>
      <div style={{ marginBottom: 24 }}>
        <h3 style={{ fontSize: 16, fontWeight: 600, color: colors.red, marginBottom: 12 }}>Excluded Products</h3>
        {c.products.excluded.map((p, i) => <ProductRow key={i} item={p} type="excluded" />)}
      </div>
      <NotesBox notes={c.products.notes} />
    </div>
  );

  const GeographyTab = () => (
    <div>
      <SectionDivider title="Geographic Criteria" subtitle="Southeast focus" icon="📍" />
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 16, marginBottom: 24 }}>
        <CriteriaCard label="Max Ship Radius" value={c.geography.maxShipRadius} subtext="miles from plant" status="set" />
        <CriteriaCard label="Density" value={c.geography.densityPreference} status="set" />
      </div>
      <StateMap primary={c.geography.primaryStates} secondary={c.geography.secondaryStates} excluded={c.geography.excludedStates} />
      <NotesBox notes={c.geography.notes} />
    </div>
  );

  const FinancialsTab = () => (
    <div>
      <SectionDivider title="Financial Criteria" subtitle="Target size and valuation guardrails" icon="💰" />
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 16, marginBottom: 32 }}>
        <CriteriaCard label="EBITDA Range" value={`${c.financials.ebitdaMin} – ${c.financials.ebitdaMax}`} status="set" />
        <CriteriaCard label="Revenue Range" value={`${c.financials.revenueMin} – ${c.financials.revenueMax}`} status="set" />
        <CriteriaCard label="Min EBITDA Margin" value={c.financials.ebitdaMarginMin} status="set" />
        <CriteriaCard label="Acceptable Multiple" value={c.financials.multipleRange} status="set" />
        <CriteriaCard label="Walk-Away Multiple" value={c.financials.maxMultiple} status="set" />
        <CriteriaCard label="Debt Funded" value={c.financials.debtFunded} status="set" />
        <CriteriaCard label="Equity Partner" value={c.financials.equityPartner} status="set" />
      </div>
      <SectionDivider title="Industry Multiples" subtitle="Current market data for precast concrete" icon="📊" />
      <MultipleBar label="Building Materials ($0–1M EBITDA)" low="4" high="6.5" />
      <MultipleBar label="Building Materials ($1–3M EBITDA)" low="6" high="8.5" highlight />
      <MultipleBar label="Building Materials ($3–5M EBITDA)" low="8" high="11" />
      <MultipleBar label="PE Average (Construction)" low="9" high="12" />
      <MultipleBar label="CMC/Foley Deal (2025)" low="10" high="10.5" highlight />
      <div style={{ marginTop: 8, fontSize: 12, color: colors.textMuted }}>Sources: First Page Sage Q4 2024, Capstone Partners Feb 2026</div>
      <NotesBox notes={c.financials.notes} />
    </div>
  );

  const DealTab = () => (
    <div>
      <SectionDivider title="Deal Structure" subtitle="How Design Precast wants to transact" icon="🤝" />
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 16 }}>
        <CriteriaCard label="Acquisition Type" value={c.dealStructure.acquisitionType} status="set" />
        <CriteriaCard label="Owner Transition" value={c.dealStructure.ownerTransition} status="set" />
        <CriteriaCard label="Earnout Acceptable" value={c.dealStructure.earnoutAcceptable} status="set" />
        <CriteriaCard label="Seller Financing" value={c.dealStructure.sellerFinancingAcceptable} status="set" />
        <CriteriaCard label="Team Retention" value={c.dealStructure.teamRetention} subtext={c.dealStructure.retentionMethod} status="set" />
        <CriteriaCard label="Hold Period" value={c.dealStructure.holdPeriod} status="set" />
        <CriteriaCard label="Rollup Intent" value={c.dealStructure.rollupIntent} status="set" />
      </div>
      <NotesBox notes={c.dealStructure.notes} />
    </div>
  );

  const FacilityTab = () => (
    <div>
      <SectionDivider title="Facility & Equipment" subtitle="Physical plant requirements" icon="🏭" />
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 16, marginBottom: 24 }}>
        <CriteriaCard label="Min Plant Size" value={c.facility.minPlantSqFt} status="set" />
        <CriteriaCard label="Outdoor Yard" value={c.facility.outdoorYardRequired} status="set" />
        <CriteriaCard label="Crane Capacity" value={c.facility.craneCapacity} status="set" />
        <CriteriaCard label="Batch Plant" value={c.facility.batchPlantRequired} status="set" />
        <CriteriaCard label="Max Facility Age" value={c.facility.ageMaxYears} status="set" />
        <CriteriaCard label="Environmental" value={c.facility.environmentalConcerns} status="set" />
        <CriteriaCard label="Delivery Fleet" value={c.facility.deliveryFleet} status="set" />
      </div>
      <SectionDivider title="Workforce" subtitle="Staffing and labor requirements" icon="👷" />
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 16, marginBottom: 16 }}>
        <CriteriaCard label="Headcount Range" value={`${c.workforce.minEmployees} – ${c.workforce.maxEmployees}`} status="set" />
        <CriteriaCard label="Labor Preference" value={c.workforce.laborMarketConcerns} status="set" />
        <CriteriaCard label="Technician Retention" value={c.workforce.technicianRetention} status="set" />
        <CriteriaCard label="Safety Record" value={c.workforce.safetyRecord} status="set" />
      </div>
      <div style={{ marginTop: 8 }}>
        <div style={{ fontSize: 12, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em", color: colors.textMuted, marginBottom: 8 }}>Key Roles Required</div>
        <TagList items={c.workforce.keyRolesRequired} color="default" />
      </div>
      <NotesBox notes={c.facility.notes} />
    </div>
  );

  const CertsTab = () => (
    <div>
      <SectionDivider title="Certifications & Compliance" subtitle="Quality and regulatory requirements" icon="✅" />
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 16, marginBottom: 24 }}>
        <CriteriaCard label="DOT Approval" value={c.certifications.dotApproval} status="set" />
        <CriteriaCard label="State-Specific" value={c.certifications.stateSpecific} status="set" />
      </div>
      <div style={{ marginBottom: 24 }}>
        <h3 style={{ fontSize: 16, fontWeight: 600, color: colors.green, marginBottom: 12 }}>Required Certifications</h3>
        {c.certifications.required.map((cert, i) => <ProductRow key={i} item={cert} type="must" />)}
      </div>
      <div style={{ marginBottom: 24 }}>
        <h3 style={{ fontSize: 16, fontWeight: 600, color: colors.accent, marginBottom: 12 }}>Preferred Certifications</h3>
        {c.certifications.preferred.map((cert, i) => <ProductRow key={i} item={cert} type="nice" />)}
      </div>
      <div style={{ marginBottom: 24 }}>
        <h3 style={{ fontSize: 16, fontWeight: 600, color: colors.red, marginBottom: 12 }}>Not Relevant / Excluded</h3>
        {c.certifications.excluded.map((cert, i) => <ProductRow key={i} item={cert} type="excluded" />)}
      </div>
      <div style={{ background: colors.surfaceMuted, border: `1px solid ${colors.border}`, borderRadius: 10, padding: 20, marginTop: 16 }}>
        <h4 style={{ fontSize: 14, fontWeight: 600, color: colors.navy, marginBottom: 12 }}>Certification Landscape</h4>
        {Object.entries(c.marketContext.certificationLandscape).map(([key, val]) => (
          <div key={key} style={{ marginBottom: 10 }}>
            <span style={{ fontWeight: 600, fontSize: 13, color: colors.textPrimary, textTransform: "uppercase" }}>{key}: </span>
            <span style={{ fontSize: 13, color: colors.textSecondary }}>{val}</span>
          </div>
        ))}
      </div>
      <NotesBox notes={c.certifications.notes} />
    </div>
  );

  const TargetsTab = () => (
    <div>
      <SectionDivider title="Named Targets" subtitle={`${c.namedTargets.length} companies identified`} icon="🎯" />
      <div style={{ border: `1px solid ${colors.border}`, borderRadius: 10, overflow: "hidden" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 16, padding: "10px 20px", background: colors.navy, color: colors.surface, fontSize: 11, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em" }}>
          <span style={{ width: 24, textAlign: "right" }}>PRI</span>
          <span style={{ flex: 1 }}>Company</span>
          <span>Status</span>
          <span style={{ maxWidth: 200, textAlign: "right" }}>Notes</span>
        </div>
        {c.namedTargets.map((t, i) => <TargetRow key={i} target={t} index={i} />)}
      </div>

      <SectionDivider title="Customer Base Requirements" subtitle="End-market and concentration criteria" icon="👥" />
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 16, marginBottom: 16 }}>
        <CriteriaCard label="Min Customers" value={c.customers.minCustomerCount} status="set" />
        <CriteriaCard label="Max Concentration" value={c.customers.maxConcentration} subtext="single customer" status="set" />
        <CriteriaCard label="Contract Type" value={c.customers.contractType} status="set" />
        <CriteriaCard label="Backlog Required" value={c.customers.backlogRequired} status="set" />
        <CriteriaCard label="Govt Contract %" value={c.customers.govtContractPct} status="set" />
      </div>
      <div style={{ marginTop: 8 }}>
        <div style={{ fontSize: 12, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em", color: colors.textMuted, marginBottom: 8 }}>Preferred End Markets</div>
        <TagList items={c.customers.preferredEndMarkets} color="green" />
      </div>
      <NotesBox notes={c.customers.notes} />
    </div>
  );

  const MarketTab = () => (
    <div>
      <SectionDivider title="Market Intelligence" subtitle="Precast concrete industry landscape" icon="📈" />
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 16, marginBottom: 32 }}>
        <CriteriaCard label="Industry Size" value={c.marketContext.industrySize} status="set" />
        <CriteriaCard label="Growth Rate" value={c.marketContext.growthRate} status="set" />
        <CriteriaCard label="Construction M&A (2025)" value={c.marketContext.constructionMATrends.totalDeals2025.toString()} subtext={`${c.marketContext.constructionMATrends.yoyGrowth} YOY`} status="set" />
        <CriteriaCard label="PE Buyer Share" value={c.marketContext.constructionMATrends.peBuyerShare} status="set" />
      </div>
      <SectionDivider title="Key Market Drivers" subtitle="Tailwinds for Design Precast's SE strategy" icon="🌊" />
      <div style={{ display: "flex", flexDirection: "column", gap: 8, marginBottom: 32 }}>
        {c.marketContext.keyDrivers.map((d, i) => (
          <div key={i} style={{ background: colors.surface, border: `1px solid ${colors.border}`, borderRadius: 8, padding: "12px 16px", fontSize: 14, color: colors.textPrimary, borderLeft: `3px solid ${colors.accent}` }}>{d}</div>
        ))}
      </div>
      <SectionDivider title="Recent Precast Deals" subtitle="Comparable transactions" icon="📄" />
      <div style={{ border: `1px solid ${colors.border}`, borderRadius: 10, padding: 20 }}>
        {c.marketContext.recentDeals.map((d, i) => <DealRow key={i} deal={d} />)}
      </div>
      <SectionDivider title="Valuation Multiples" icon="📊" />
      <MultipleBar label="Building Materials ($1–3M)" low="6" high="8.5" highlight />
      <MultipleBar label="Building Materials ($3–5M)" low="8" high="11" />
      <MultipleBar label="Civil/Infrastructure ($1–3M)" low="7.5" high="10" highlight />
      <MultipleBar label="PE Average" low="9" high="12" />
      <MultipleBar label="CMC/Foley (2025)" low="10" high="10.5" highlight />
    </div>
  );

  const tabContent = { overview: <OverviewTab />, products: <ProductsTab />, geography: <GeographyTab />, financials: <FinancialsTab />, deal: <DealTab />, facility: <FacilityTab />, certs: <CertsTab />, targets: <TargetsTab />, market: <MarketTab /> };

  return (
    <div style={{ minHeight: "100vh", background: colors.surfaceMuted, fontFamily: fonts.body }}>
      <div style={{ background: `linear-gradient(135deg, ${colors.navy} 0%, ${colors.navyLight} 100%)`, padding: "40px 0 0", color: colors.surface }}>
        <div style={{ maxWidth: 1100, margin: "0 auto", padding: "0 24px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 24 }}>
            <div>
              <div style={{ fontSize: 12, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.12em", color: colors.gold, marginBottom: 8 }}>Buy-Side Target Criteria</div>
              <h1 style={{ margin: 0, fontSize: 32, fontWeight: 800, fontFamily: fonts.heading, lineHeight: 1.2 }}>Design Precast & Pipe</h1>
              <p style={{ margin: "8px 0 0", fontSize: 16, color: colors.concreteLight, fontWeight: 400 }}>Acquisition Target Screening — Platform + Bolt-On (Debt-Funded, PE Later)</p>
            </div>
            <div style={{ textAlign: "right" }}>
              <div style={{ fontSize: 13, color: colors.concreteLight }}>Next Chapter Advisory</div>
              <div style={{ fontSize: 13, color: colors.gold, fontWeight: 600, marginTop: 4 }}>Updated 2026-03-29</div>
            </div>
          </div>
          <div style={{ display: "flex", gap: 0, overflowX: "auto" }}>
            {TABS.map((tab) => (
              <button key={tab.id} onClick={() => setActiveTab(tab.id)} style={{
                padding: "12px 20px", border: "none", cursor: "pointer", fontSize: 13,
                fontWeight: activeTab === tab.id ? 700 : 500, fontFamily: fonts.body, whiteSpace: "nowrap",
                background: activeTab === tab.id ? colors.surface : "transparent",
                color: activeTab === tab.id ? colors.navy : colors.concreteLight,
                borderTopLeftRadius: 8, borderTopRightRadius: 8, transition: "all 0.15s ease",
              }}>{tab.label}</button>
            ))}
          </div>
        </div>
      </div>
      <div style={{ maxWidth: 1100, margin: "0 auto", padding: "32px 24px 64px" }}>{tabContent[activeTab]}</div>
      <div style={{ borderTop: `1px solid ${colors.border}`, padding: "24px 0", textAlign: "center", fontSize: 12, color: colors.textMuted }}>
        <div style={{ maxWidth: 1100, margin: "0 auto" }}>Next Chapter Advisory — Design Precast & Pipe — Buy-Side Criteria — Confidential</div>
      </div>
    </div>
  );
}
