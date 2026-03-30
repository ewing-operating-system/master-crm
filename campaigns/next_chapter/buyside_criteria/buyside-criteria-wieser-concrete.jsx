import { useState } from "react";

// ════════════════════════════════════════════════════════════════
// WIESER CONCRETE — BUY-SIDE TARGET CRITERIA
// Populated from: Fireflies transcript "Andy Wieser + Next Chapter" (Dec 15, 2025)
//                 Mark's recap email (Dec 16, 2025)
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
// CONFIG — WIESER CONCRETE (Andy Wieser)
// Sources: Fireflies transcript (Dec 15, 2025), Mark's email recap (Dec 16, 2025)
// ════════════════════════════════════════════════════════════════
const CONFIG = {
  client: {
    companyName: "Wieser Concrete",
    contactName: "Andy Wieser",
    contactTitle: "Owner / Operator",
    contactEmail: "andy@wieserconcrete.com",
    headquarters: "Midwest (ND/SD/MN region)",
    currentPlants: "Multiple (3-4 prior acquisitions)",
    currentStates: "ND, SD, MN, IA, WI",
    strategy: "Platform Expansion — Organic + Acquisition",
    advisorEngaged: "No — no other advisors engaged, opportunistic",
    priorAcquisitions: "3-4",
    dateUpdated: "2026-03-29",
  },

  products: {
    mustHave: [
      { name: "Underground Utility Precast", description: "Manholes, catch basins, utility vaults, underground infrastructure structures" },
      { name: "Septic Tanks", description: "Residential and commercial septic systems — core Wieser product" },
      { name: "Box Culverts", description: "Precast box culverts for highway and drainage crossings" },
      { name: "Highway Products", description: "Barrier walls, median barriers, noise walls, highway-related precast" },
      { name: "Agricultural Precast", description: "Feed bunks, cattle guards, H-bunks, silage walls, ag storage — core Wieser specialty" },
    ],
    niceToHave: [
      { name: "Manholes (all sizes)", description: "Standard and large-diameter manholes for municipal infrastructure" },
      { name: "Noise/Sound Walls", description: "Highway noise barrier panels and sound walls" },
      { name: "Stormwater Products", description: "Detention/retention systems, stormwater treatment structures" },
      { name: "Pre-stressing Capability", description: "Acceptable but not core — bridge beams, double-tees, hollow core if paired with underground/ag" },
      { name: "Retaining Walls", description: "Gravity walls, segmental systems if part of broader mix" },
    ],
    excluded: [
      { name: "Architectural Precast Only", description: "Facade panels, decorative cladding — NOT Wieser's market" },
      { name: "Hardscapes Only", description: "Pavers, decorative stone, landscape products without infrastructure" },
      { name: "Pure Prestressed Structural Only", description: "Companies doing ONLY bridge beams and structural with zero underground/ag overlap" },
    ],
    minimumOverlapPct: "50%",
    notes: "Andy's product wheelhouse is underground + highway + agricultural. Pre-stressing is acceptable as a secondary capability but the core must be infrastructure/utility/ag precast. Hardscapes and architectural are out.",
  },

  geography: {
    primaryStates: ["ND", "SD", "NE", "KS", "MN", "IA", "WI"],
    secondaryStates: ["OK", "North TX", "MO", "AR", "IL", "MI", "IN", "KY", "TN", "OH"],
    excludedStates: [],
    maxShipRadius: "200–400",
    densityPreference: "Rural + small metro — agricultural and DOT markets",
    notes: "Midwest + South expansion corridor. Andy's current footprint is Upper Midwest (Dakotas, MN, IA, WI). Expansion targets are south and east — filling in the heartland. Precast shipping economics limit radius to ~200-400 miles depending on product weight.",
  },

  financials: {
    ebitdaMin: "$500K",
    ebitdaMax: "$5M",
    revenueMin: "$3M",
    revenueMax: "$25M",
    ebitdaMarginMin: "12%",
    multipleRange: "4x–7x EBITDA",
    maxMultiple: "7x (seeing asks of 6-7x; larger at 8-10x)",
    debtFunded: "Yes — family-capitalized with debt",
    equityPartner: "None — family succession, no outside equity",
    notes: "Andy mentioned seeing asking prices of 6-7x EBITDA for typical targets, with larger assets asking 8-10x. Wieser is family-capitalized with no PE involvement. This is a long-term family hold, not a flip. Lower EBITDA floor ($500K) since they're willing to take on smaller add-ons.",
  },

  dealStructure: {
    acquisitionType: "100% buyout only",
    ownerTransition: "Owner exits — team stays",
    earnoutAcceptable: "Possible but prefers clean buyout",
    sellerFinancingAcceptable: "Yes",
    teamRetention: "Required — non-negotiable",
    retentionMethod: "Profit-based bonuses for key operators",
    holdPeriod: "Indefinite — family succession / permanent hold",
    rollupIntent: "Yes — Midwest precast expansion, but at their own pace",
    notes: "Andy is explicit: 100% buyouts only. No minority deals. Owners exit, teams stay. Retention via profit bonuses. Family succession is in place. This is a generational business — they're not building to sell. 3-4 prior acquisitions demonstrate a proven integration playbook. The deal has to 'feel right' — cultural fit matters as much as financials.",
  },

  certifications: {
    required: [
      { name: "NPCA Plant Certification", description: "Wieser Concrete is NPCA certified. Targets should be or be willing to become certified." },
    ],
    preferred: [
      { name: "State DOT Approval", description: "Approved supplier lists for DOTs in target states" },
      { name: "ACPA Quality Cast", description: "For pipe-producing plants" },
      { name: "ASTM Compliance", description: "Meeting relevant ASTM standards for underground and highway products" },
    ],
    excluded: [],
    dotApproval: "Preferred — DOT work is a significant revenue stream",
    stateSpecific: "Target state DOT approved supplier lists as expansion occurs",
    notes: "Wieser is NPCA certified per their own website. They would expect targets to be certified or certifiable. DOT approval is important for highway product sales.",
  },

  facility: {
    minPlantSqFt: "10,000+",
    outdoorYardRequired: "Yes — essential for curing, ag products, and highway barriers",
    craneCapacity: "5+ tons (ag products are lighter than some infrastructure)",
    batchPlantRequired: "Yes — on-site batch plant required",
    ageMaxYears: "No hard limit — but bad facility is a deal breaker",
    environmentalConcerns: "Must be clean — environmental issues kill deals",
    deliveryFleet: "Owned fleet strongly preferred — critical for rural delivery coverage",
    notes: "Andy called out 'bad facility' as a specific deal breaker. The plant doesn't need to be new but it needs to be functional, well-maintained, and expandable. Owned delivery fleet is especially important for ag markets where customers are spread across rural areas.",
  },

  workforce: {
    minEmployees: "10",
    maxEmployees: "100",
    keyRolesRequired: ["Plant Manager", "QC Lead", "Batch Operator", "Delivery Drivers", "Sales/Estimator"],
    laborMarketConcerns: "Non-union (Midwest rural labor market)",
    technicianRetention: "Critical — Andy specifically mentioned 'teams stay'",
    safetyRecord: "Clean record required",
    notes: "In rural Midwest markets, finding and retaining skilled precast workers is the #1 operational challenge. Andy's profit-bonus retention model is designed to keep teams in place post-acquisition. Cultural fit is a major factor.",
  },

  customers: {
    minCustomerCount: "15+",
    maxConcentration: "30% max single customer",
    preferredEndMarkets: [
      "Municipal infrastructure (water/sewer/storm)",
      "State DOT highway programs",
      "Agricultural operations (livestock, grain, dairy)",
      "Residential septic systems",
      "Commercial development",
      "County road departments",
      "Rural water districts",
    ],
    contractType: "Mix of project-based and recurring (ag is seasonal/recurring)",
    backlogRequired: "Preferred — 2+ months",
    govtContractPct: "30–50% preferred (municipal + DOT + county)",
    notes: "Wieser's customer mix is unique vs. other precast: significant agricultural revenue alongside infrastructure. Ag provides seasonal but recurring demand. Municipal and DOT provide project-based stability. Rural water districts and county road departments are bread-and-butter customers in the Midwest.",
  },

  dealBreakers: [
    "Zoning issues that prevent plant expansion or continued operation",
    "Bad facility condition — plant in disrepair or requiring major capital",
    "Wrong product mix — no overlap with underground/highway/ag products",
    "Cultural mismatch — 'the deal has to feel right' (Andy's words)",
    "Owner wants minority deal or partial sale — 100% buyout only",
    "Severe environmental contamination or cleanup liability",
    "Architectural or hardscape only — no infrastructure products",
    "Facility location outside Midwest/South expansion corridor",
    "Key staff planning to leave post-sale with no retention solution",
  ],

  namedTargets: [
    // Andy has an active LOI on one target (unnamed in transcript)
    { name: "[Active LOI Target]", location: "Midwest", status: "LOI", priority: 1, notes: "Andy mentioned active LOI during Dec 2025 call — target name not disclosed" },
  ],

  marketContext: {
    industrySize: "$160B+ global precast concrete market (2025)",
    growthRate: "4.2–6.3% CAGR through 2030-2034",
    keyDrivers: [
      "IIJA infrastructure spending ($1.2T through 2026+) — highways, bridges, water/sewer",
      "Midwest agricultural construction cycle — new dairy, livestock, and grain facilities",
      "Rural water infrastructure investment — EPA Small Community Water Programs",
      "Highway rehabilitation — DOT bridge and culvert replacement programs",
      "Buy America / BABA mandates — domestic manufacturing for federal projects",
      "Data center buildout expanding into Midwest markets (IA, OH, WI)",
      "Population and ag consolidation driving larger farm operations needing more precast",
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
      npca: "NPCA Plant Certification — Wieser is certified. Recognized by 40+ states. ANSI-accredited (ISO/IEC 17065).",
      acpa: "ACPA Quality Cast — for pipe-specific plants. Relevant for targets with pipe in their product mix.",
      pci: "PCI (Prestressed Concrete Institute) — for prestressed structural. Acceptable as secondary capability in Wieser targets.",
    },
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

export default function WieserConcreteCriteria() {
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
        <CriteriaCard label="Current Plants" value={c.client.currentPlants} status="set" />
        <CriteriaCard label="Strategy" value={c.client.strategy} status="set" />
        <CriteriaCard label="Prior Acquisitions" value={c.client.priorAcquisitions} status="set" />
        <CriteriaCard label="Advisor" value={c.client.advisorEngaged} status="set" />
      </div>

      {/* Key Differentiator */}
      <div style={{
        background: `linear-gradient(135deg, ${colors.navy} 0%, ${colors.navyLight} 100%)`,
        borderRadius: 12, padding: 24, marginBottom: 32, color: colors.surface,
      }}>
        <div style={{ fontSize: 14, fontWeight: 600, color: colors.gold, marginBottom: 8, textTransform: "uppercase", letterSpacing: "0.05em" }}>Key Differentiator</div>
        <div style={{ fontSize: 16, lineHeight: 1.6 }}>
          Family-owned, generational hold. 3-4 prior acquisitions with a proven integration playbook. 100% buyouts only — no minority deals. Profit-bonus retention model. Andy's exact words: "The deal has to feel right."
        </div>
      </div>

      <SectionDivider title="Criteria Summary" subtitle="All sections populated from cold call intel" icon="📋" />
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 16 }}>
        {[
          { label: "Products", items: c.products.mustHave.length, desc: `${c.products.mustHave.length} required, ${c.products.niceToHave.length} preferred, ${c.products.excluded.length} excluded` },
          { label: "Geography", items: c.geography.primaryStates.length, desc: `${c.geography.primaryStates.length} primary, ${c.geography.secondaryStates.length} secondary states` },
          { label: "EBITDA Range", items: 1, desc: `${c.financials.ebitdaMin} – ${c.financials.ebitdaMax}` },
          { label: "Deal Structure", items: 1, desc: c.dealStructure.acquisitionType },
          { label: "Certifications", items: c.certifications.required.length, desc: `${c.certifications.required.length} required, ${c.certifications.preferred.length} preferred` },
          { label: "Named Targets", items: c.namedTargets.length, desc: `${c.namedTargets.filter(t => t.status === "LOI").length} with active LOI` },
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
            <SectionDivider title={`Deal Breakers (${expandedBreakers ? "collapse" : "expand"})`} subtitle="Andy's hard stops" icon="🚫" />
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
      <SectionDivider title="Product Criteria" subtitle="Underground + Highway + Agricultural" icon="🧱" />
      <div style={{ marginBottom: 24 }}>
        <CriteriaCard label="Minimum Product Overlap" value={c.products.minimumOverlapPct} subtext="of target's revenue must be in Wieser's core product lines" status="set" />
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
      <SectionDivider title="Geographic Criteria" subtitle="Midwest + South expansion corridor" icon="📍" />
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 16, marginBottom: 24 }}>
        <CriteriaCard label="Max Ship Radius" value={c.geography.maxShipRadius} subtext="miles — varies by product weight" status="set" />
        <CriteriaCard label="Density" value={c.geography.densityPreference} status="set" />
      </div>
      <StateMap primary={c.geography.primaryStates} secondary={c.geography.secondaryStates} excluded={c.geography.excludedStates} />
      <NotesBox notes={c.geography.notes} />
    </div>
  );

  const FinancialsTab = () => (
    <div>
      <SectionDivider title="Financial Criteria" subtitle="Family-capitalized, no outside equity" icon="💰" />
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 16, marginBottom: 32 }}>
        <CriteriaCard label="EBITDA Range" value={`${c.financials.ebitdaMin} – ${c.financials.ebitdaMax}`} status="set" />
        <CriteriaCard label="Revenue Range" value={`${c.financials.revenueMin} – ${c.financials.revenueMax}`} status="set" />
        <CriteriaCard label="Min EBITDA Margin" value={c.financials.ebitdaMarginMin} status="set" />
        <CriteriaCard label="Acceptable Multiple" value={c.financials.multipleRange} status="set" />
        <CriteriaCard label="Walk-Away Multiple" value={c.financials.maxMultiple} status="set" />
        <CriteriaCard label="Debt Funded" value={c.financials.debtFunded} status="set" />
        <CriteriaCard label="Equity Partner" value={c.financials.equityPartner} status="set" />
      </div>
      <SectionDivider title="Industry Multiples" subtitle="What Andy is seeing in the market" icon="📊" />
      <MultipleBar label="Typical Asks (Andy's Intel)" low="6" high="7" highlight />
      <MultipleBar label="Larger Assets (Andy's Intel)" low="8" high="10" />
      <MultipleBar label="Building Materials ($0.5–1M)" low="4" high="6.5" />
      <MultipleBar label="Building Materials ($1–3M)" low="6" high="8.5" highlight />
      <MultipleBar label="Building Materials ($3–5M)" low="8" high="11" />
      <MultipleBar label="PE Average (Construction)" low="9" high="12" />
      <div style={{ marginTop: 8, fontSize: 12, color: colors.textMuted }}>Sources: Andy Wieser (Dec 2025 call), First Page Sage, Capstone Partners</div>
      <NotesBox notes={c.financials.notes} />
    </div>
  );

  const DealTab = () => (
    <div>
      <SectionDivider title="Deal Structure" subtitle="100% buyout — owners exit, teams stay" icon="🤝" />
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
      <SectionDivider title="Facility & Equipment" subtitle="Plant must be functional and expandable" icon="🏭" />
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 16, marginBottom: 24 }}>
        <CriteriaCard label="Min Plant Size" value={c.facility.minPlantSqFt} status="set" />
        <CriteriaCard label="Outdoor Yard" value={c.facility.outdoorYardRequired} status="set" />
        <CriteriaCard label="Crane Capacity" value={c.facility.craneCapacity} status="set" />
        <CriteriaCard label="Batch Plant" value={c.facility.batchPlantRequired} status="set" />
        <CriteriaCard label="Max Facility Age" value={c.facility.ageMaxYears} status="set" />
        <CriteriaCard label="Environmental" value={c.facility.environmentalConcerns} status="set" />
        <CriteriaCard label="Delivery Fleet" value={c.facility.deliveryFleet} status="set" />
      </div>
      <SectionDivider title="Workforce" subtitle="Teams stay — profit-bonus retention" icon="👷" />
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
      <SectionDivider title="Certifications & Compliance" subtitle="Wieser is NPCA certified" icon="✅" />
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
      <SectionDivider title="Named Targets" subtitle={`${c.namedTargets.length} identified — 1 active LOI`} icon="🎯" />
      <div style={{ border: `1px solid ${colors.border}`, borderRadius: 10, overflow: "hidden" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 16, padding: "10px 20px", background: colors.navy, color: colors.surface, fontSize: 11, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em" }}>
          <span style={{ width: 24, textAlign: "right" }}>PRI</span>
          <span style={{ flex: 1 }}>Company</span>
          <span>Status</span>
          <span style={{ maxWidth: 200, textAlign: "right" }}>Notes</span>
        </div>
        {c.namedTargets.map((t, i) => <TargetRow key={i} target={t} index={i} />)}
      </div>

      <div style={{ background: colors.amberBg, border: `1px solid ${colors.amberLight}`, borderRadius: 10, padding: 20, marginTop: 24 }}>
        <div style={{ fontWeight: 600, fontSize: 14, color: colors.amber, marginBottom: 8 }}>Target Pipeline Needed</div>
        <div style={{ fontSize: 14, color: colors.textPrimary, lineHeight: 1.6 }}>
          Wieser has an active LOI on one undisclosed target but no broader pipeline built yet. Next Chapter should build a scored pipeline of Midwest/South precast targets similar to the Design Precast model (470+ scored → 200 → 49 activated → client cuts to final list).
        </div>
      </div>

      <SectionDivider title="Customer Base Requirements" subtitle="Infrastructure + Agricultural mix" icon="👥" />
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
      <SectionDivider title="Market Intelligence" subtitle="Precast concrete — Midwest focus" icon="📈" />
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 16, marginBottom: 32 }}>
        <CriteriaCard label="Industry Size" value={c.marketContext.industrySize} status="set" />
        <CriteriaCard label="Growth Rate" value={c.marketContext.growthRate} status="set" />
        <CriteriaCard label="Construction M&A (2025)" value={c.marketContext.constructionMATrends.totalDeals2025.toString()} subtext={`${c.marketContext.constructionMATrends.yoyGrowth} YOY`} status="set" />
        <CriteriaCard label="PE Buyer Share" value={c.marketContext.constructionMATrends.peBuyerShare} status="set" />
      </div>
      <SectionDivider title="Key Market Drivers" subtitle="Tailwinds for Wieser's Midwest expansion" icon="🌊" />
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
      <MultipleBar label="Andy's Market Intel (Typical)" low="6" high="7" highlight />
      <MultipleBar label="Andy's Market Intel (Larger)" low="8" high="10" />
      <MultipleBar label="Building Materials ($0.5–1M)" low="4" high="6.5" />
      <MultipleBar label="Building Materials ($1–3M)" low="6" high="8.5" highlight />
      <MultipleBar label="PE Average" low="9" high="12" />
      <MultipleBar label="CMC/Foley (2025)" low="10" high="10.5" />
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
              <h1 style={{ margin: 0, fontSize: 32, fontWeight: 800, fontFamily: fonts.heading, lineHeight: 1.2 }}>Wieser Concrete</h1>
              <p style={{ margin: "8px 0 0", fontSize: 16, color: colors.concreteLight, fontWeight: 400 }}>Acquisition Target Screening — Platform Expansion (Family-Owned, Permanent Hold)</p>
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
        <div style={{ maxWidth: 1100, margin: "0 auto" }}>Next Chapter Advisory — Wieser Concrete — Buy-Side Criteria — Confidential</div>
      </div>
    </div>
  );
}
