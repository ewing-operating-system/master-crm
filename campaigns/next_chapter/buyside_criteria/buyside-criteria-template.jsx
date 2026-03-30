import { useState } from "react";

// ════════════════════════════════════════════════════════════════
// PRECAST CONCRETE — BUY-SIDE TARGET CRITERIA TEMPLATE
// Master template: agents swap the CONFIG object to populate
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
// CONFIG — Agents replace this entire object per client
// ════════════════════════════════════════════════════════════════
const CONFIG = {
  // ─── CLIENT INFO ───
  client: {
    companyName: "{{company_name}}",
    contactName: "{{contact_name}}",
    contactTitle: "{{contact_title}}",
    contactEmail: "{{contact_email}}",
    headquarters: "{{headquarters_city_state}}",
    currentPlants: "{{number_of_plants}}",
    currentStates: "{{states_of_operation}}",
    strategy: "{{platform_or_bolt_on}}",
    advisorEngaged: "{{yes_or_no}}",
    priorAcquisitions: "{{number}}",
    dateUpdated: "{{YYYY-MM-DD}}",
  },

  // ─── PRODUCT CRITERIA ───
  products: {
    mustHave: [
      // Each: { name, description }
      // e.g. { name: "Storm/Sewer Pipe", description: "RCP, elliptical, arch pipe for storm and sanitary sewer" }
    ],
    niceToHave: [
      // Same format
    ],
    excluded: [
      // Same format — products the buyer does NOT want
    ],
    minimumOverlapPct: "{{minimum_product_overlap_percentage}}",
    notes: "{{product_notes}}",
  },

  // ─── GEOGRAPHIC CRITERIA ───
  geography: {
    primaryStates: [],    // Array of state abbreviations — highest priority
    secondaryStates: [],  // Acceptable but lower priority
    excludedStates: [],   // Will not consider
    maxShipRadius: "{{miles}}",
    densityPreference: "{{urban_suburban_rural_mix}}",
    notes: "{{geography_notes}}",
  },

  // ─── FINANCIAL CRITERIA ───
  financials: {
    ebitdaMin: "{{min_ebitda}}",
    ebitdaMax: "{{max_ebitda}}",
    revenueMin: "{{min_revenue}}",
    revenueMax: "{{max_revenue}}",
    ebitdaMarginMin: "{{min_margin_pct}}",
    multipleRange: "{{acceptable_multiple_range}}",
    maxMultiple: "{{walk_away_multiple}}",
    debtFunded: "{{yes_or_no}}",
    equityPartner: "{{pe_or_none}}",
    notes: "{{financial_notes}}",
  },

  // ─── DEAL STRUCTURE ───
  dealStructure: {
    acquisitionType: "{{100pct_buyout_or_majority_or_minority}}",
    ownerTransition: "{{owner_stays_or_exits}}",
    earnoutAcceptable: "{{yes_or_no}}",
    sellerFinancingAcceptable: "{{yes_or_no}}",
    teamRetention: "{{required_or_preferred}}",
    retentionMethod: "{{bonuses_equity_etc}}",
    holdPeriod: "{{years_or_indefinite}}",
    rollupIntent: "{{yes_no_description}}",
    notes: "{{deal_structure_notes}}",
  },

  // ─── CERTIFICATIONS & COMPLIANCE ───
  certifications: {
    required: [
      // e.g. { name: "NPCA Plant Certification", description: "National Precast Concrete Association — required by 40+ states" }
    ],
    preferred: [],
    excluded: [],
    dotApproval: "{{required_preferred_not_needed}}",
    stateSpecific: "{{list_of_state_specific_certs}}",
    notes: "{{certification_notes}}",
  },

  // ─── FACILITY & EQUIPMENT ───
  facility: {
    minPlantSqFt: "{{minimum_sq_ft}}",
    outdoorYardRequired: "{{yes_or_no}}",
    craneCapacity: "{{minimum_tons}}",
    batchPlantRequired: "{{yes_or_no}}",
    ageMaxYears: "{{max_facility_age_years}}",
    environmentalConcerns: "{{brownfield_acceptable}}",
    deliveryFleet: "{{owned_fleet_required_or_third_party_ok}}",
    notes: "{{facility_notes}}",
  },

  // ─── WORKFORCE ───
  workforce: {
    minEmployees: "{{minimum_headcount}}",
    maxEmployees: "{{maximum_headcount}}",
    keyRolesRequired: [
      // e.g. "QC Manager", "Plant Superintendent", "Estimator"
    ],
    laborMarketConcerns: "{{union_nonunion_preference}}",
    technicianRetention: "{{critical_important_standard}}",
    safetyRecord: "{{OSHA_requirements}}",
    notes: "{{workforce_notes}}",
  },

  // ─── CUSTOMER BASE ───
  customers: {
    minCustomerCount: "{{minimum_customers}}",
    maxConcentration: "{{max_pct_single_customer}}",
    preferredEndMarkets: [
      // e.g. "Municipal infrastructure", "DOT/highway", "Commercial development"
    ],
    contractType: "{{project_based_or_recurring_or_both}}",
    backlogRequired: "{{yes_and_minimum_months}}",
    govtContractPct: "{{preferred_govt_pct}}",
    notes: "{{customer_notes}}",
  },

  // ─── DEAL BREAKERS ───
  dealBreakers: [
    // Array of strings — hard nos
    // e.g. "Zoning issues that prevent expansion"
  ],

  // ─── NAMED TARGETS ───
  namedTargets: [
    // Each: { name, location, status, priority, notes }
    // status: "active" | "contacted" | "passed" | "LOI" | "watching"
    // priority: 1-5
  ],

  // ─── MARKET CONTEXT (auto-populated from research) ───
  marketContext: {
    industrySize: "$160B+ global precast concrete market (2025)",
    growthRate: "4.2–6.3% CAGR through 2030-2034",
    keyDrivers: [
      "IIJA infrastructure spending ($1.2T through 2026+)",
      "Data center construction boom (+138% YOY to $53.7B)",
      "Buy America / BABA domestic manufacturing mandates",
      "Aging municipal water and sewer infrastructure replacement",
      "Highway and bridge rehabilitation programs",
      "Stormwater management regulatory expansion",
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
      npca: "NPCA Plant Certification — recognized by 40+ states, 75+ municipalities. ANSI-accredited (ISO/IEC 17065). Annual inspections by independent engineering firms.",
      acpa: "ACPA Quality Cast — American Concrete Pipe Association certification for pipe-specific plants.",
      pci: "PCI (Prestressed Concrete Institute) — for prestressed/precast structural products. Different market segment.",
    },
  },
};

// ════════════════════════════════════════════════════════════════
// COMPONENTS
// ════════════════════════════════════════════════════════════════

const SectionDivider = ({ title, subtitle, icon }) => (
  <div style={{ marginBottom: 32, paddingBottom: 16, borderBottom: `2px solid ${colors.border}` }}>
    <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
      {icon && <span style={{ fontSize: 24 }}>{icon}</span>}
      <div>
        <h2 style={{ margin: 0, fontSize: 22, fontWeight: 700, fontFamily: fonts.heading, color: colors.navy }}>
          {title}
        </h2>
        {subtitle && (
          <p style={{ margin: "4px 0 0", fontSize: 14, color: colors.textSecondary, fontFamily: fonts.body }}>
            {subtitle}
          </p>
        )}
      </div>
    </div>
  </div>
);

const CriteriaCard = ({ label, value, subtext, status }) => {
  const statusColors = {
    set: { bg: colors.greenBg, border: colors.green, dot: colors.green },
    partial: { bg: colors.amberBg, border: colors.amber, dot: colors.amber },
    unset: { bg: colors.surfaceDark, border: colors.border, dot: colors.textMuted },
  };
  const s = statusColors[status] || statusColors.unset;
  return (
    <div style={{
      background: colors.surface, border: `1px solid ${colors.border}`, borderRadius: 10,
      padding: "16px 20px", display: "flex", flexDirection: "column", gap: 6,
      borderLeft: `4px solid ${s.border}`,
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span style={{ fontSize: 12, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em", color: colors.textMuted, fontFamily: fonts.body }}>
          {label}
        </span>
        <span style={{ width: 8, height: 8, borderRadius: "50%", background: s.dot }} />
      </div>
      <span style={{ fontSize: 18, fontWeight: 700, color: colors.textPrimary, fontFamily: fonts.mono }}>
        {value || "—"}
      </span>
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
          display: "inline-block", padding: "6px 14px", borderRadius: 20,
          fontSize: 13, fontWeight: 500, fontFamily: fonts.body,
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
    <div style={{
      display: "flex", alignItems: "flex-start", gap: 14, padding: "12px 0",
      borderBottom: `1px solid ${colors.borderLight}`,
    }}>
      <span style={{
        fontSize: 10, fontWeight: 700, padding: "3px 8px", borderRadius: 4,
        background: type === "must" ? colors.greenBg : type === "excluded" ? colors.redBg : colors.surfaceDark,
        color: typeColors[type], letterSpacing: "0.05em", whiteSpace: "nowrap", marginTop: 2,
      }}>
        {typeLabels[type]}
      </span>
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
      <div style={{ fontSize: 12, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em", color: colors.green, marginBottom: 8 }}>
        Primary Markets
      </div>
      <TagList items={primary} color="green" emptyText="No primary states set" />
    </div>
    <div>
      <div style={{ fontSize: 12, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em", color: colors.accent, marginBottom: 8 }}>
        Secondary Markets
      </div>
      <TagList items={secondary} color="default" emptyText="No secondary states set" />
    </div>
    {excluded && excluded.length > 0 && (
      <div>
        <div style={{ fontSize: 12, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em", color: colors.red, marginBottom: 8 }}>
          Excluded
        </div>
        <TagList items={excluded} color="red" />
      </div>
    )}
  </div>
);

const TargetRow = ({ target, index }) => {
  const statusStyles = {
    active: { bg: colors.greenBg, color: colors.green, label: "ACTIVE" },
    contacted: { bg: colors.amberBg, color: colors.amber, label: "CONTACTED" },
    passed: { bg: colors.redBg, color: colors.red, label: "PASSED" },
    LOI: { bg: "#EDE9FE", color: "#7C3AED", label: "LOI" },
    watching: { bg: colors.surfaceDark, color: colors.textSecondary, label: "WATCHING" },
  };
  const s = statusStyles[target.status] || statusStyles.watching;
  return (
    <div style={{
      display: "flex", alignItems: "center", gap: 16, padding: "14px 20px",
      background: index % 2 === 0 ? colors.surface : colors.surfaceMuted,
      borderBottom: `1px solid ${colors.borderLight}`,
    }}>
      <span style={{ fontFamily: fonts.mono, fontSize: 13, color: colors.textMuted, width: 24, textAlign: "right" }}>
        {target.priority || "—"}
      </span>
      <div style={{ flex: 1 }}>
        <div style={{ fontWeight: 600, fontSize: 14, color: colors.textPrimary }}>{target.name}</div>
        <div style={{ fontSize: 13, color: colors.textSecondary }}>{target.location}</div>
      </div>
      <span style={{
        fontSize: 10, fontWeight: 700, padding: "3px 10px", borderRadius: 4,
        background: s.bg, color: s.color, letterSpacing: "0.05em",
      }}>
        {s.label}
      </span>
      {target.notes && <span style={{ fontSize: 12, color: colors.textMuted, maxWidth: 200, textAlign: "right" }}>{target.notes}</span>}
    </div>
  );
};

const DealRow = ({ deal }) => (
  <div style={{
    display: "flex", alignItems: "center", gap: 16, padding: "12px 0",
    borderBottom: `1px solid ${colors.borderLight}`,
  }}>
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
        <div style={{
          position: "absolute", left: `${leftPct}%`, width: `${widthPct}%`, height: "100%",
          background: highlight ? `linear-gradient(90deg, ${colors.gold}, ${colors.accent})` : colors.concreteLight,
          borderRadius: 4,
        }} />
      </div>
    </div>
  );
};

const NotesBox = ({ notes }) => {
  if (!notes || notes.startsWith("{{")) return null;
  return (
    <div style={{
      background: colors.surfaceMuted, border: `1px solid ${colors.border}`, borderRadius: 8,
      padding: "12px 16px", marginTop: 16, fontSize: 13, color: colors.textSecondary,
      fontStyle: "italic", lineHeight: 1.6,
    }}>
      {notes}
    </div>
  );
};

// ════════════════════════════════════════════════════════════════
// TABS
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

// ════════════════════════════════════════════════════════════════
// MAIN COMPONENT
// ════════════════════════════════════════════════════════════════
export default function BuySideCriteriaPage() {
  const [activeTab, setActiveTab] = useState("overview");
  const [expandedBreakers, setExpandedBreakers] = useState(false);
  const c = CONFIG;

  const isSet = (v) => v && !v.startsWith("{{");
  const statusOf = (v) => isSet(v) ? "set" : "unset";

  // ─── TAB: OVERVIEW ───
  const OverviewTab = () => (
    <div>
      <SectionDivider title="Client Overview" subtitle="Buyer profile and acquisition strategy" icon="🏗️" />
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 16, marginBottom: 32 }}>
        <CriteriaCard label="Company" value={c.client.companyName} status={statusOf(c.client.companyName)} />
        <CriteriaCard label="Contact" value={c.client.contactName} subtext={c.client.contactTitle} status={statusOf(c.client.contactName)} />
        <CriteriaCard label="Headquarters" value={c.client.headquarters} status={statusOf(c.client.headquarters)} />
        <CriteriaCard label="Current Plants" value={c.client.currentPlants} status={statusOf(c.client.currentPlants)} />
        <CriteriaCard label="Strategy" value={c.client.strategy} status={statusOf(c.client.strategy)} />
        <CriteriaCard label="Prior Acquisitions" value={c.client.priorAcquisitions} status={statusOf(c.client.priorAcquisitions)} />
        <CriteriaCard label="Advisor Engaged" value={c.client.advisorEngaged} status={statusOf(c.client.advisorEngaged)} />
        <CriteriaCard label="Last Updated" value={c.client.dateUpdated} status={statusOf(c.client.dateUpdated)} />
      </div>

      <SectionDivider title="Criteria Summary" subtitle="Quick view of all configured sections" icon="📋" />
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 16 }}>
        {[
          { label: "Products", items: c.products.mustHave.length, desc: `${c.products.mustHave.length} required, ${c.products.niceToHave.length} preferred, ${c.products.excluded.length} excluded` },
          { label: "Geography", items: c.geography.primaryStates.length, desc: `${c.geography.primaryStates.length} primary states, ${c.geography.secondaryStates.length} secondary` },
          { label: "EBITDA Range", items: isSet(c.financials.ebitdaMin) ? 1 : 0, desc: `${c.financials.ebitdaMin} – ${c.financials.ebitdaMax}` },
          { label: "Deal Structure", items: isSet(c.dealStructure.acquisitionType) ? 1 : 0, desc: c.dealStructure.acquisitionType },
          { label: "Certifications", items: c.certifications.required.length, desc: `${c.certifications.required.length} required, ${c.certifications.preferred.length} preferred` },
          { label: "Named Targets", items: c.namedTargets.length, desc: `${c.namedTargets.filter(t => t.status === "active").length} active` },
          { label: "Deal Breakers", items: c.dealBreakers.length, desc: `${c.dealBreakers.length} hard stops` },
        ].map((s, i) => (
          <div key={i} style={{
            background: colors.surface, border: `1px solid ${colors.border}`, borderRadius: 10,
            padding: "16px 20px", display: "flex", justifyContent: "space-between", alignItems: "center",
          }}>
            <div>
              <div style={{ fontWeight: 600, fontSize: 15, color: colors.textPrimary }}>{s.label}</div>
              <div style={{ fontSize: 13, color: colors.textSecondary, marginTop: 2 }}>{s.desc}</div>
            </div>
            <div style={{
              width: 36, height: 36, borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center",
              background: s.items > 0 ? colors.greenBg : colors.surfaceDark,
              color: s.items > 0 ? colors.green : colors.textMuted,
              fontWeight: 700, fontSize: 14, fontFamily: fonts.mono,
            }}>
              {s.items}
            </div>
          </div>
        ))}
      </div>

      {c.dealBreakers.length > 0 && (
        <div style={{ marginTop: 32 }}>
          <div
            onClick={() => setExpandedBreakers(!expandedBreakers)}
            style={{ cursor: "pointer", display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}
          >
            <SectionDivider title="Deal Breakers" subtitle="Hard stops — any one kills the deal" icon="🚫" />
          </div>
          {expandedBreakers && (
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {c.dealBreakers.map((b, i) => (
                <div key={i} style={{
                  background: colors.redBg, border: `1px solid #FECACA`, borderRadius: 8,
                  padding: "12px 16px", fontSize: 14, color: colors.red, fontWeight: 500,
                }}>
                  {b}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );

  // ─── TAB: PRODUCTS ───
  const ProductsTab = () => (
    <div>
      <SectionDivider title="Product Criteria" subtitle="What the target must manufacture" icon="🧱" />
      <div style={{ marginBottom: 24 }}>
        <CriteriaCard label="Minimum Product Overlap" value={c.products.minimumOverlapPct} subtext="of target's revenue must be in buyer's core products" status={statusOf(c.products.minimumOverlapPct)} />
      </div>

      <div style={{ marginBottom: 24 }}>
        <h3 style={{ fontSize: 16, fontWeight: 600, color: colors.green, marginBottom: 12 }}>Must-Have Products</h3>
        {c.products.mustHave.length > 0
          ? c.products.mustHave.map((p, i) => <ProductRow key={i} item={p} type="must" />)
          : <span style={{ fontSize: 13, color: colors.textMuted, fontStyle: "italic" }}>No must-have products configured</span>
        }
      </div>

      <div style={{ marginBottom: 24 }}>
        <h3 style={{ fontSize: 16, fontWeight: 600, color: colors.accent, marginBottom: 12 }}>Nice-to-Have Products</h3>
        {c.products.niceToHave.length > 0
          ? c.products.niceToHave.map((p, i) => <ProductRow key={i} item={p} type="nice" />)
          : <span style={{ fontSize: 13, color: colors.textMuted, fontStyle: "italic" }}>No preferred products configured</span>
        }
      </div>

      <div style={{ marginBottom: 24 }}>
        <h3 style={{ fontSize: 16, fontWeight: 600, color: colors.red, marginBottom: 12 }}>Excluded Products</h3>
        {c.products.excluded.length > 0
          ? c.products.excluded.map((p, i) => <ProductRow key={i} item={p} type="excluded" />)
          : <span style={{ fontSize: 13, color: colors.textMuted, fontStyle: "italic" }}>No excluded products configured</span>
        }
      </div>

      <NotesBox notes={c.products.notes} />
    </div>
  );

  // ─── TAB: GEOGRAPHY ───
  const GeographyTab = () => (
    <div>
      <SectionDivider title="Geographic Criteria" subtitle="Where the buyer wants to acquire" icon="📍" />
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 16, marginBottom: 24 }}>
        <CriteriaCard label="Max Ship Radius" value={c.geography.maxShipRadius} subtext="miles from plant" status={statusOf(c.geography.maxShipRadius)} />
        <CriteriaCard label="Density" value={c.geography.densityPreference} status={statusOf(c.geography.densityPreference)} />
      </div>
      <StateMap primary={c.geography.primaryStates} secondary={c.geography.secondaryStates} excluded={c.geography.excludedStates} />
      <NotesBox notes={c.geography.notes} />
    </div>
  );

  // ─── TAB: FINANCIALS ───
  const FinancialsTab = () => (
    <div>
      <SectionDivider title="Financial Criteria" subtitle="Target size and valuation guardrails" icon="💰" />
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 16, marginBottom: 32 }}>
        <CriteriaCard label="EBITDA Range" value={`${c.financials.ebitdaMin} – ${c.financials.ebitdaMax}`} status={isSet(c.financials.ebitdaMin) ? "set" : "unset"} />
        <CriteriaCard label="Revenue Range" value={`${c.financials.revenueMin} – ${c.financials.revenueMax}`} status={isSet(c.financials.revenueMin) ? "set" : "unset"} />
        <CriteriaCard label="Min EBITDA Margin" value={c.financials.ebitdaMarginMin} status={statusOf(c.financials.ebitdaMarginMin)} />
        <CriteriaCard label="Acceptable Multiple" value={c.financials.multipleRange} status={statusOf(c.financials.multipleRange)} />
        <CriteriaCard label="Walk-Away Multiple" value={c.financials.maxMultiple} status={statusOf(c.financials.maxMultiple)} />
        <CriteriaCard label="Debt Funded" value={c.financials.debtFunded} status={statusOf(c.financials.debtFunded)} />
        <CriteriaCard label="Equity Partner" value={c.financials.equityPartner} status={statusOf(c.financials.equityPartner)} />
      </div>

      <SectionDivider title="Industry Multiples" subtitle="Current market data for precast concrete" icon="📊" />
      <MultipleBar label="Building Materials ($0–1M EBITDA)" low="4" high="6" />
      <MultipleBar label="Building Materials ($1–3M EBITDA)" low="6" high="8" highlight />
      <MultipleBar label="Building Materials ($3–5M EBITDA)" low="8" high="11" />
      <MultipleBar label="Civil Engineering ($1–3M EBITDA)" low="7" high="10" highlight />
      <MultipleBar label="PE Avg (All Construction)" low="9" high="12" />
      <MultipleBar label="Strategic Avg (All Construction)" low="6" high="9" />
      <div style={{ marginTop: 8, fontSize: 12, color: colors.textMuted }}>
        Sources: First Page Sage Q4 2024, Capstone Partners Feb 2026, Equidam 2026
      </div>

      <NotesBox notes={c.financials.notes} />
    </div>
  );

  // ─── TAB: DEAL STRUCTURE ───
  const DealTab = () => (
    <div>
      <SectionDivider title="Deal Structure" subtitle="How the buyer wants to transact" icon="🤝" />
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 16 }}>
        <CriteriaCard label="Acquisition Type" value={c.dealStructure.acquisitionType} status={statusOf(c.dealStructure.acquisitionType)} />
        <CriteriaCard label="Owner Transition" value={c.dealStructure.ownerTransition} status={statusOf(c.dealStructure.ownerTransition)} />
        <CriteriaCard label="Earnout Acceptable" value={c.dealStructure.earnoutAcceptable} status={statusOf(c.dealStructure.earnoutAcceptable)} />
        <CriteriaCard label="Seller Financing" value={c.dealStructure.sellerFinancingAcceptable} status={statusOf(c.dealStructure.sellerFinancingAcceptable)} />
        <CriteriaCard label="Team Retention" value={c.dealStructure.teamRetention} subtext={c.dealStructure.retentionMethod} status={statusOf(c.dealStructure.teamRetention)} />
        <CriteriaCard label="Hold Period" value={c.dealStructure.holdPeriod} status={statusOf(c.dealStructure.holdPeriod)} />
        <CriteriaCard label="Rollup Intent" value={c.dealStructure.rollupIntent} status={statusOf(c.dealStructure.rollupIntent)} />
      </div>
      <NotesBox notes={c.dealStructure.notes} />
    </div>
  );

  // ─── TAB: FACILITY ───
  const FacilityTab = () => (
    <div>
      <SectionDivider title="Facility & Equipment" subtitle="Physical plant requirements" icon="🏭" />
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 16, marginBottom: 24 }}>
        <CriteriaCard label="Min Plant Size" value={c.facility.minPlantSqFt} status={statusOf(c.facility.minPlantSqFt)} />
        <CriteriaCard label="Outdoor Yard" value={c.facility.outdoorYardRequired} status={statusOf(c.facility.outdoorYardRequired)} />
        <CriteriaCard label="Crane Capacity" value={c.facility.craneCapacity} status={statusOf(c.facility.craneCapacity)} />
        <CriteriaCard label="Batch Plant" value={c.facility.batchPlantRequired} status={statusOf(c.facility.batchPlantRequired)} />
        <CriteriaCard label="Max Facility Age" value={c.facility.ageMaxYears} status={statusOf(c.facility.ageMaxYears)} />
        <CriteriaCard label="Environmental" value={c.facility.environmentalConcerns} status={statusOf(c.facility.environmentalConcerns)} />
        <CriteriaCard label="Delivery Fleet" value={c.facility.deliveryFleet} status={statusOf(c.facility.deliveryFleet)} />
      </div>

      <SectionDivider title="Workforce" subtitle="Staffing and labor requirements" icon="👷" />
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 16, marginBottom: 16 }}>
        <CriteriaCard label="Headcount Range" value={`${c.workforce.minEmployees} – ${c.workforce.maxEmployees}`} status={isSet(c.workforce.minEmployees) ? "set" : "unset"} />
        <CriteriaCard label="Labor Preference" value={c.workforce.laborMarketConcerns} status={statusOf(c.workforce.laborMarketConcerns)} />
        <CriteriaCard label="Technician Retention" value={c.workforce.technicianRetention} status={statusOf(c.workforce.technicianRetention)} />
        <CriteriaCard label="Safety Record" value={c.workforce.safetyRecord} status={statusOf(c.workforce.safetyRecord)} />
      </div>
      {c.workforce.keyRolesRequired.length > 0 && (
        <div style={{ marginTop: 8 }}>
          <div style={{ fontSize: 12, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em", color: colors.textMuted, marginBottom: 8 }}>Key Roles Required</div>
          <TagList items={c.workforce.keyRolesRequired} color="default" />
        </div>
      )}
      <NotesBox notes={c.facility.notes} />
      <NotesBox notes={c.workforce.notes} />
    </div>
  );

  // ─── TAB: CERTIFICATIONS ───
  const CertsTab = () => (
    <div>
      <SectionDivider title="Certifications & Compliance" subtitle="Quality and regulatory requirements" icon="✅" />
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 16, marginBottom: 24 }}>
        <CriteriaCard label="DOT Approval" value={c.certifications.dotApproval} status={statusOf(c.certifications.dotApproval)} />
        <CriteriaCard label="State-Specific" value={c.certifications.stateSpecific} status={statusOf(c.certifications.stateSpecific)} />
      </div>

      <div style={{ marginBottom: 24 }}>
        <h3 style={{ fontSize: 16, fontWeight: 600, color: colors.green, marginBottom: 12 }}>Required Certifications</h3>
        {c.certifications.required.length > 0
          ? c.certifications.required.map((cert, i) => <ProductRow key={i} item={cert} type="must" />)
          : <span style={{ fontSize: 13, color: colors.textMuted, fontStyle: "italic" }}>None configured</span>
        }
      </div>

      <div style={{ marginBottom: 24 }}>
        <h3 style={{ fontSize: 16, fontWeight: 600, color: colors.accent, marginBottom: 12 }}>Preferred Certifications</h3>
        {c.certifications.preferred.length > 0
          ? c.certifications.preferred.map((cert, i) => <ProductRow key={i} item={cert} type="nice" />)
          : <span style={{ fontSize: 13, color: colors.textMuted, fontStyle: "italic" }}>None configured</span>
        }
      </div>

      {c.certifications.excluded.length > 0 && (
        <div style={{ marginBottom: 24 }}>
          <h3 style={{ fontSize: 16, fontWeight: 600, color: colors.red, marginBottom: 12 }}>Not Relevant / Excluded</h3>
          {c.certifications.excluded.map((cert, i) => <ProductRow key={i} item={cert} type="excluded" />)}
        </div>
      )}

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

  // ─── TAB: TARGETS ───
  const TargetsTab = () => (
    <div>
      <SectionDivider title="Named Targets" subtitle={`${c.namedTargets.length} companies identified`} icon="🎯" />
      {c.namedTargets.length > 0 ? (
        <div style={{ border: `1px solid ${colors.border}`, borderRadius: 10, overflow: "hidden" }}>
          <div style={{
            display: "flex", alignItems: "center", gap: 16, padding: "10px 20px",
            background: colors.navy, color: colors.surface, fontSize: 11, fontWeight: 600,
            textTransform: "uppercase", letterSpacing: "0.05em",
          }}>
            <span style={{ width: 24, textAlign: "right" }}>PRI</span>
            <span style={{ flex: 1 }}>Company</span>
            <span>Status</span>
            <span style={{ maxWidth: 200, textAlign: "right" }}>Notes</span>
          </div>
          {c.namedTargets.map((t, i) => <TargetRow key={i} target={t} index={i} />)}
        </div>
      ) : (
        <div style={{
          background: colors.surfaceMuted, border: `1px solid ${colors.border}`, borderRadius: 10,
          padding: 40, textAlign: "center", color: colors.textMuted, fontSize: 15,
        }}>
          No named targets configured yet
        </div>
      )}

      <SectionDivider title="Customer Base Requirements" subtitle="End-market and concentration criteria" icon="👥" />
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 16, marginBottom: 16 }}>
        <CriteriaCard label="Min Customers" value={c.customers.minCustomerCount} status={statusOf(c.customers.minCustomerCount)} />
        <CriteriaCard label="Max Concentration" value={c.customers.maxConcentration} subtext="single customer" status={statusOf(c.customers.maxConcentration)} />
        <CriteriaCard label="Contract Type" value={c.customers.contractType} status={statusOf(c.customers.contractType)} />
        <CriteriaCard label="Backlog Required" value={c.customers.backlogRequired} status={statusOf(c.customers.backlogRequired)} />
        <CriteriaCard label="Govt Contract %" value={c.customers.govtContractPct} status={statusOf(c.customers.govtContractPct)} />
      </div>
      {c.customers.preferredEndMarkets.length > 0 && (
        <div style={{ marginTop: 8 }}>
          <div style={{ fontSize: 12, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em", color: colors.textMuted, marginBottom: 8 }}>Preferred End Markets</div>
          <TagList items={c.customers.preferredEndMarkets} color="green" />
        </div>
      )}
      <NotesBox notes={c.customers.notes} />
    </div>
  );

  // ─── TAB: MARKET INTEL ───
  const MarketTab = () => (
    <div>
      <SectionDivider title="Market Intelligence" subtitle="Precast concrete industry landscape" icon="📈" />
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 16, marginBottom: 32 }}>
        <CriteriaCard label="Industry Size" value={c.marketContext.industrySize} status="set" />
        <CriteriaCard label="Growth Rate" value={c.marketContext.growthRate} status="set" />
        <CriteriaCard label="Construction M&A Deals (2025)" value={c.marketContext.constructionMATrends.totalDeals2025.toString()} subtext={`${c.marketContext.constructionMATrends.yoyGrowth} YOY`} status="set" />
        <CriteriaCard label="PE Buyer Share" value={c.marketContext.constructionMATrends.peBuyerShare} subtext={`${c.marketContext.constructionMATrends.newPlatforms} new platforms`} status="set" />
      </div>

      <SectionDivider title="Key Market Drivers" subtitle="Tailwinds for precast concrete" icon="🌊" />
      <div style={{ display: "flex", flexDirection: "column", gap: 8, marginBottom: 32 }}>
        {c.marketContext.keyDrivers.map((d, i) => (
          <div key={i} style={{
            background: colors.surface, border: `1px solid ${colors.border}`, borderRadius: 8,
            padding: "12px 16px", fontSize: 14, color: colors.textPrimary,
            borderLeft: `3px solid ${colors.accent}`,
          }}>
            {d}
          </div>
        ))}
      </div>

      <SectionDivider title="Recent Precast Deals" subtitle="Comparable transactions" icon="📄" />
      <div style={{ border: `1px solid ${colors.border}`, borderRadius: 10, padding: 20 }}>
        {c.marketContext.recentDeals.map((d, i) => <DealRow key={i} deal={d} />)}
      </div>

      <SectionDivider title="Valuation Multiples" subtitle="EBITDA multiples by segment and size" icon="📊" />
      <MultipleBar label="Building Materials ($0–1M EBITDA)" low="4" high="6.5" />
      <MultipleBar label="Building Materials ($1–3M EBITDA)" low="6" high="8.5" highlight />
      <MultipleBar label="Building Materials ($3–5M EBITDA)" low="8" high="11" />
      <MultipleBar label="Civil/Infrastructure ($0–1M)" low="5.5" high="8" />
      <MultipleBar label="Civil/Infrastructure ($1–3M)" low="7.5" high="10" highlight />
      <MultipleBar label="PE Average (Construction)" low="9" high="12" />
      <MultipleBar label="CMC/Foley Deal (2025)" low="10" high="10.5" highlight />
      <div style={{ marginTop: 8, fontSize: 12, color: colors.textMuted }}>
        Sources: First Page Sage, Capstone Partners, Equidam, CMC SEC filings
      </div>
    </div>
  );

  const tabContent = {
    overview: <OverviewTab />,
    products: <ProductsTab />,
    geography: <GeographyTab />,
    financials: <FinancialsTab />,
    deal: <DealTab />,
    facility: <FacilityTab />,
    certs: <CertsTab />,
    targets: <TargetsTab />,
    market: <MarketTab />,
  };

  return (
    <div style={{ minHeight: "100vh", background: colors.surfaceMuted, fontFamily: fonts.body }}>
      {/* Header */}
      <div style={{
        background: `linear-gradient(135deg, ${colors.navy} 0%, ${colors.navyLight} 100%)`,
        padding: "40px 0 0", color: colors.surface,
      }}>
        <div style={{ maxWidth: 1100, margin: "0 auto", padding: "0 24px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 24 }}>
            <div>
              <div style={{ fontSize: 12, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.12em", color: colors.gold, marginBottom: 8 }}>
                Buy-Side Target Criteria
              </div>
              <h1 style={{ margin: 0, fontSize: 32, fontWeight: 800, fontFamily: fonts.heading, lineHeight: 1.2 }}>
                {isSet(c.client.companyName) ? c.client.companyName : "Precast Concrete"}
              </h1>
              <p style={{ margin: "8px 0 0", fontSize: 16, color: colors.concreteLight, fontWeight: 400 }}>
                Acquisition Target Screening — {isSet(c.client.strategy) ? c.client.strategy : "Platform + Bolt-On"} Strategy
              </p>
            </div>
            <div style={{ textAlign: "right" }}>
              <div style={{ fontSize: 13, color: colors.concreteLight }}>Next Chapter Advisory</div>
              <div style={{ fontSize: 13, color: colors.gold, fontWeight: 600, marginTop: 4 }}>
                {isSet(c.client.dateUpdated) ? `Updated ${c.client.dateUpdated}` : "Draft"}
              </div>
            </div>
          </div>

          {/* Tab Navigation */}
          <div style={{ display: "flex", gap: 0, overflowX: "auto" }}>
            {TABS.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                style={{
                  padding: "12px 20px", border: "none", cursor: "pointer",
                  fontSize: 13, fontWeight: activeTab === tab.id ? 700 : 500,
                  fontFamily: fonts.body, whiteSpace: "nowrap",
                  background: activeTab === tab.id ? colors.surface : "transparent",
                  color: activeTab === tab.id ? colors.navy : colors.concreteLight,
                  borderTopLeftRadius: 8, borderTopRightRadius: 8,
                  transition: "all 0.15s ease",
                }}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      <div style={{ maxWidth: 1100, margin: "0 auto", padding: "32px 24px 64px" }}>
        {tabContent[activeTab]}
      </div>

      {/* Footer */}
      <div style={{
        borderTop: `1px solid ${colors.border}`, padding: "24px 0",
        textAlign: "center", fontSize: 12, color: colors.textMuted,
      }}>
        <div style={{ maxWidth: 1100, margin: "0 auto" }}>
          Next Chapter Advisory — Precast Concrete Buy-Side Criteria — Confidential
        </div>
      </div>
    </div>
  );
}
