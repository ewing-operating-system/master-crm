import { useState } from "react";

// ════════════════════════════════════════════════════════════════
// HOME SERVICES M&A ADVISORY PROPOSAL — VERCEL COMPONENT SYSTEM
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
  red: "#DC2626",
  redBg: "#FEF2F2",
};

// ─── TYPOGRAPHY ───
const fonts = {
  heading: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
  body: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
  mono: "'JetBrains Mono', 'Fira Code', monospace",
};

// ─── SAMPLE DATA (agents replace this) ───
const PROPOSAL = {
  firm: {
    name: "Next Chapter Advisory",
    tagline: "M&A Advisory for the Trades",
    phone: "(512) 555-0100",
    email: "advisory@chapter.guide",
    website: "chapter.guide",
  },
  client: {
    ownerName: "{{owner_name}}",
    companyName: "{{company_name}}",
    tradeVertical: "HVAC",
    yearFounded: "{{year_founded}}",
    locations: "{{locations}}",
    employeeCount: "{{employee_count}}",
    annualRevenue: "${{annual_revenue}}",
    adjustedEbitda: "${{adjusted_ebitda}}",
    ebitdaMargin: "{{ebitda_margin}}%",
    revenueMix: "{{service_pct}}% Service / {{install_pct}}% Install",
    recurringRevenue: "{{recurring_revenue_pct}}%",
    fleetSize: "{{fleet_size}}",
    serviceArea: "{{service_area}}",
    licenses: "{{licenses}}",
  },
  engagement: {
    type: "Sell-Side Advisory",
    date: "{{proposal_date}}",
    engagementFee: "$15,000",
    monthlyRetainer: "$5,000",
    successFeeStructure: "5% of Enterprise Value",
    minimumFee: "$100,000",
    expectedTimeline: "6–9 Months",
    exclusivityTerm: "12 Months",
    tailPeriod: "18 Months",
  },
  valuation: {
    earningsMetric: "Adjusted EBITDA",
    earningsAmount: "${{adjusted_ebitda}}",
    multLow: "4.0",
    multMid: "6.0",
    multHigh: "8.5",
    evLow: "${{ev_low}}",
    evMid: "${{ev_mid}}",
    evHigh: "${{ev_high}}",
    adjustments: [
      "Owner compensation normalization",
      "One-time / non-recurring expenses",
      "Related party rent adjustment",
      "Personal expenses run through business",
    ],
    upsideFactors: [
      "High recurring revenue from maintenance agreements",
      "Diversified customer base with no concentration risk",
      "Strong technician bench with low turnover",
    ],
    downsideFactors: [
      "High owner dependency in sales/operations",
      "Deferred fleet or equipment maintenance",
    ],
  },
  market: {
    currentMultipleRange: "4x – 12x EBITDA",
    activeBuyers: "40+",
    recentDealCount: "200+",
    averageDealSize: "$5M – $25M",
    timingRationale: [
      "PE dry powder at all-time highs with home services as top deployment target",
      "HVAC consolidation estimated only 50% through its cycle — premium multiples persist",
      "Regulatory tailwinds from energy efficiency mandates driving service demand",
    ],
    comps: [
      { type: "HVAC Platform", size: "$18M", multiple: "8.2x", buyer: "PE-Backed Platform", date: "Q1 2026" },
      { type: "Plumbing Add-on", size: "$4.5M", multiple: "5.5x", buyer: "Strategic Acquirer", date: "Q4 2025" },
      { type: "HVAC + Plumbing", size: "$12M", multiple: "7.0x", buyer: "PE Roll-up", date: "Q3 2025" },
    ],
  },
  process: [
    {
      phase: "Phase 1",
      title: "Preparation",
      weeks: "Weeks 1–6",
      color: colors.accent,
      tasks: [
        "Complete business valuation and financial analysis",
        "Identify and document EBITDA adjustments / add-backs",
        "Create Confidential Information Memorandum (CIM)",
        "Build target buyer list — strategic, PE, independent",
        "Prepare management presentation materials",
        "Establish secure virtual data room",
      ],
    },
    {
      phase: "Phase 2",
      title: "Marketing",
      weeks: "Weeks 7–14",
      color: colors.green,
      tasks: [
        "Distribute blind teaser to qualified buyers",
        "Execute NDAs with interested parties",
        "Distribute CIM to qualified, signed buyers",
        "Manage buyer Q&A process",
        "Solicit Indications of Interest (IOIs)",
        "Evaluate and rank offers",
      ],
    },
    {
      phase: "Phase 3",
      title: "Negotiation",
      weeks: "Weeks 15–22",
      color: colors.gold,
      tasks: [
        "Facilitate management presentations with top bidders",
        "Request Letters of Intent (LOIs)",
        "Negotiate price, terms, structure, and transition",
        "Select preferred buyer and execute LOI",
        "Coordinate with legal counsel on deal structure",
      ],
    },
    {
      phase: "Phase 4",
      title: "Closing",
      weeks: "Weeks 23–36",
      color: colors.navy,
      tasks: [
        "Manage confirmatory due diligence process",
        "Coordinate with buyer's lenders and advisors",
        "Support purchase agreement negotiation",
        "Navigate working capital and earnout mechanics",
        "Close transaction and facilitate ownership transfer",
      ],
    },
  ],
  buyers: {
    strategic: [
      "Wrench Group",
      "Apex Service Partners",
      "Neighborly (Frontdoor)",
      "Service Experts",
      "Sila Services",
    ],
    pePlatforms: [
      { name: "Coolsys", fund: "Ares Management" },
      { name: "Home Alliance", fund: "Goldman Sachs Alternatives" },
      { name: "Horizon Services", fund: "Prospect Capital" },
    ],
    independentCount: "25+",
    regionalBuyers: ["{{regional_buyer_1}}", "{{regional_buyer_2}}"],
    totalUniverse: "80+",
    expectedOutreach: "50–60",
    expectedNDAs: "15–20",
    expectedIOIs: "5–8",
    expectedLOIs: "2–3",
  },
  fees: {
    scenarios: [
      { price: "$3,000,000", fee: "$150,000", net: "$135,000", rate: "4.5%" },
      { price: "$5,000,000", fee: "$250,000", net: "$220,000", rate: "4.4%" },
      { price: "$10,000,000", fee: "$500,000", net: "$455,000", rate: "4.6%" },
    ],
  },
  credentials: {
    description:
      "Next Chapter Advisory is a specialized M&A advisory firm focused exclusively on home services and trades businesses. We advise owners of HVAC, plumbing, electrical, pest control, and roofing companies on sell-side exits, buy-side acquisitions, and recapitalizations. Our team has closed over $150M in home services transactions.",
    deals: [
      { client: "Regional HVAC Co.", trade: "HVAC", size: "$8.2M", buyer: "PE Platform", year: "2025" },
      { client: "Multi-Location Plumbing", trade: "Plumbing", size: "$4.8M", buyer: "Strategic", year: "2025" },
      { client: "Pest Control Platform", trade: "Pest Control", size: "$12.5M", buyer: "PE Roll-up", year: "2024" },
    ],
    team: [
      {
        name: "{{advisor_1_name}}",
        title: "Managing Director",
        bio: "15+ years in home services M&A. Previously at [firm]. Closed 40+ transactions.",
      },
      {
        name: "{{advisor_2_name}}",
        title: "Vice President",
        bio: "Former operator — owned and sold an HVAC business. Deep industry network.",
      },
    ],
    testimonials: [
      {
        quote: "They understood my business from day one. I got 3 offers above my asking price.",
        source: "HVAC Business Owner, Dallas TX",
      },
      {
        quote: "The process was professional and fast. Closed in 5 months.",
        source: "Plumbing Company Owner, Phoenix AZ",
      },
    ],
  },
};

// ════════════════════════════════════════════════════════
// COMPONENTS
// ════════════════════════════════════════════════════════

function SectionDivider({ number, title }) {
  return (
    <div style={{ margin: "64px 0 32px", display: "flex", alignItems: "center", gap: 16 }}>
      <div
        style={{
          width: 48,
          height: 48,
          borderRadius: "50%",
          background: `linear-gradient(135deg, ${colors.navy}, ${colors.navyLight})`,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          color: colors.gold,
          fontSize: 18,
          fontWeight: 700,
          fontFamily: fonts.mono,
          flexShrink: 0,
        }}
      >
        {number}
      </div>
      <div>
        <div
          style={{
            fontSize: 11,
            fontWeight: 600,
            letterSpacing: "0.12em",
            textTransform: "uppercase",
            color: colors.textMuted,
            fontFamily: fonts.body,
            marginBottom: 2,
          }}
        >
          Section {number}
        </div>
        <h2
          style={{
            fontSize: 26,
            fontWeight: 700,
            color: colors.textPrimary,
            fontFamily: fonts.heading,
            margin: 0,
            lineHeight: 1.2,
          }}
        >
          {title}
        </h2>
      </div>
    </div>
  );
}

function MetricCard({ label, value, sublabel }) {
  return (
    <div
      style={{
        background: colors.surface,
        border: `1px solid ${colors.border}`,
        borderRadius: 12,
        padding: "20px 24px",
        flex: "1 1 160px",
        minWidth: 160,
      }}
    >
      <div
        style={{
          fontSize: 11,
          fontWeight: 600,
          textTransform: "uppercase",
          letterSpacing: "0.08em",
          color: colors.textMuted,
          marginBottom: 6,
          fontFamily: fonts.body,
        }}
      >
        {label}
      </div>
      <div
        style={{
          fontSize: 22,
          fontWeight: 700,
          color: colors.textPrimary,
          fontFamily: fonts.heading,
          lineHeight: 1.2,
        }}
      >
        {value}
      </div>
      {sublabel && (
        <div style={{ fontSize: 13, color: colors.textSecondary, marginTop: 4, fontFamily: fonts.body }}>
          {sublabel}
        </div>
      )}
    </div>
  );
}

function PhaseCard({ phase, title, weeks, color, tasks, isExpanded, onToggle }) {
  return (
    <div
      style={{
        background: colors.surface,
        border: `1px solid ${colors.border}`,
        borderRadius: 12,
        overflow: "hidden",
        marginBottom: 16,
      }}
    >
      <button
        onClick={onToggle}
        style={{
          width: "100%",
          display: "flex",
          alignItems: "center",
          gap: 16,
          padding: "20px 24px",
          background: "none",
          border: "none",
          cursor: "pointer",
          textAlign: "left",
        }}
      >
        <div
          style={{
            width: 6,
            height: 48,
            borderRadius: 3,
            background: color,
            flexShrink: 0,
          }}
        />
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: 12, fontWeight: 600, color: colors.textMuted, letterSpacing: "0.06em", fontFamily: fonts.body }}>
            {phase} — {weeks}
          </div>
          <div style={{ fontSize: 20, fontWeight: 700, color: colors.textPrimary, fontFamily: fonts.heading }}>{title}</div>
        </div>
        <div
          style={{
            fontSize: 20,
            color: colors.textMuted,
            transform: isExpanded ? "rotate(180deg)" : "rotate(0deg)",
            transition: "transform 0.2s ease",
          }}
        >
          ▾
        </div>
      </button>
      {isExpanded && (
        <div style={{ padding: "0 24px 20px 46px" }}>
          {tasks.map((task, i) => (
            <div
              key={i}
              style={{
                display: "flex",
                alignItems: "flex-start",
                gap: 12,
                padding: "8px 0",
                borderTop: i > 0 ? `1px solid ${colors.borderLight}` : "none",
              }}
            >
              <div
                style={{
                  width: 20,
                  height: 20,
                  borderRadius: 4,
                  border: `2px solid ${colors.border}`,
                  flexShrink: 0,
                  marginTop: 1,
                }}
              />
              <span style={{ fontSize: 15, color: colors.textSecondary, fontFamily: fonts.body, lineHeight: 1.5 }}>
                {task}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function ValuationBar({ label, multiple, value, maxWidth, color }) {
  return (
    <div style={{ marginBottom: 16 }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
        <span style={{ fontSize: 13, fontWeight: 600, color: colors.textSecondary, fontFamily: fonts.body }}>{label}</span>
        <span style={{ fontSize: 13, fontWeight: 700, color: colors.textPrimary, fontFamily: fonts.mono }}>{value}</span>
      </div>
      <div style={{ background: colors.surfaceDark, borderRadius: 8, height: 12, overflow: "hidden" }}>
        <div
          style={{
            width: `${maxWidth}%`,
            height: "100%",
            borderRadius: 8,
            background: `linear-gradient(90deg, ${color}, ${color}CC)`,
          }}
        />
      </div>
      <div style={{ fontSize: 12, color: colors.textMuted, marginTop: 4, fontFamily: fonts.mono }}>{multiple}x EBITDA</div>
    </div>
  );
}

function BuyerTag({ name, type }) {
  const bgMap = { strategic: colors.accentLight + "18", pe: colors.gold + "22", independent: colors.green + "18" };
  const colorMap = { strategic: colors.accent, pe: "#92600A", independent: colors.green };
  return (
    <span
      style={{
        display: "inline-block",
        padding: "6px 14px",
        borderRadius: 20,
        background: bgMap[type] || colors.surfaceDark,
        color: colorMap[type] || colors.textSecondary,
        fontSize: 13,
        fontWeight: 600,
        fontFamily: fonts.body,
        margin: "4px 6px 4px 0",
      }}
    >
      {name}
    </span>
  );
}

function FeeTable({ scenarios }) {
  return (
    <div style={{ overflowX: "auto" }}>
      <table
        style={{
          width: "100%",
          borderCollapse: "separate",
          borderSpacing: 0,
          fontFamily: fonts.body,
          fontSize: 14,
        }}
      >
        <thead>
          <tr>
            {["Sale Price", "Success Fee", "Net After Credits", "Effective Rate"].map((h) => (
              <th
                key={h}
                style={{
                  padding: "14px 20px",
                  textAlign: "left",
                  fontWeight: 600,
                  fontSize: 12,
                  textTransform: "uppercase",
                  letterSpacing: "0.06em",
                  color: colors.textMuted,
                  borderBottom: `2px solid ${colors.border}`,
                  background: colors.surfaceMuted,
                }}
              >
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {scenarios.map((s, i) => (
            <tr key={i}>
              <td style={{ padding: "14px 20px", fontWeight: 700, color: colors.textPrimary, borderBottom: `1px solid ${colors.borderLight}`, fontFamily: fonts.mono }}>{s.price}</td>
              <td style={{ padding: "14px 20px", color: colors.textSecondary, borderBottom: `1px solid ${colors.borderLight}`, fontFamily: fonts.mono }}>{s.fee}</td>
              <td style={{ padding: "14px 20px", color: colors.textSecondary, borderBottom: `1px solid ${colors.borderLight}`, fontFamily: fonts.mono }}>{s.net}</td>
              <td style={{ padding: "14px 20px", borderBottom: `1px solid ${colors.borderLight}` }}>
                <span
                  style={{
                    background: colors.greenBg,
                    color: colors.green,
                    padding: "4px 10px",
                    borderRadius: 6,
                    fontWeight: 700,
                    fontSize: 13,
                    fontFamily: fonts.mono,
                  }}
                >
                  {s.rate}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function TestimonialCard({ quote, source }) {
  return (
    <div
      style={{
        background: colors.surfaceMuted,
        borderRadius: 12,
        padding: 28,
        borderLeft: `4px solid ${colors.gold}`,
        marginBottom: 16,
      }}
    >
      <div style={{ fontSize: 16, color: colors.textPrimary, fontStyle: "italic", lineHeight: 1.6, fontFamily: fonts.body, marginBottom: 12 }}>
        "{quote}"
      </div>
      <div style={{ fontSize: 13, fontWeight: 600, color: colors.textMuted, fontFamily: fonts.body }}>— {source}</div>
    </div>
  );
}

function DealRow({ client, trade, size, buyer, year }) {
  return (
    <tr>
      <td style={{ padding: "12px 16px", fontWeight: 600, color: colors.textPrimary, borderBottom: `1px solid ${colors.borderLight}`, fontFamily: fonts.body, fontSize: 14 }}>{client}</td>
      <td style={{ padding: "12px 16px", color: colors.textSecondary, borderBottom: `1px solid ${colors.borderLight}`, fontFamily: fonts.body, fontSize: 14 }}>{trade}</td>
      <td style={{ padding: "12px 16px", fontWeight: 700, color: colors.textPrimary, borderBottom: `1px solid ${colors.borderLight}`, fontFamily: fonts.mono, fontSize: 14 }}>{size}</td>
      <td style={{ padding: "12px 16px", color: colors.textSecondary, borderBottom: `1px solid ${colors.borderLight}`, fontFamily: fonts.body, fontSize: 14 }}>{buyer}</td>
      <td style={{ padding: "12px 16px", color: colors.textMuted, borderBottom: `1px solid ${colors.borderLight}`, fontFamily: fonts.mono, fontSize: 14 }}>{year}</td>
    </tr>
  );
}

// ════════════════════════════════════════════════════════
// MAIN PAGE
// ════════════════════════════════════════════════════════

export default function ProposalPage() {
  const [expandedPhase, setExpandedPhase] = useState(0);
  const [activeTab, setActiveTab] = useState("overview");
  const d = PROPOSAL;

  const navItems = [
    { id: "overview", label: "Overview" },
    { id: "market", label: "Market" },
    { id: "valuation", label: "Valuation" },
    { id: "process", label: "Process" },
    { id: "buyers", label: "Buyers" },
    { id: "fees", label: "Fees" },
    { id: "credentials", label: "Credentials" },
    { id: "next", label: "Next Steps" },
  ];

  return (
    <div style={{ fontFamily: fonts.body, color: colors.textPrimary, background: "#F8FAFC", minHeight: "100vh" }}>
      {/* ─── HEADER ─── */}
      <header
        style={{
          background: `linear-gradient(135deg, ${colors.navy} 0%, ${colors.navyLight} 100%)`,
          padding: "56px 0 64px",
          position: "relative",
          overflow: "hidden",
        }}
      >
        <div style={{ position: "absolute", top: 0, right: 0, width: 400, height: 400, borderRadius: "50%", background: colors.accent + "08", transform: "translate(30%, -40%)" }} />
        <div style={{ maxWidth: 900, margin: "0 auto", padding: "0 32px", position: "relative", zIndex: 1 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 40 }}>
            <div>
              <div style={{ fontSize: 14, fontWeight: 600, color: colors.gold, letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 4 }}>
                {d.firm.name}
              </div>
              <div style={{ fontSize: 13, color: colors.accentGlow + "88" }}>{d.firm.tagline}</div>
            </div>
            <div style={{ fontSize: 13, color: colors.accentGlow + "66", textAlign: "right", lineHeight: 1.8 }}>
              Confidential
              <br />
              {d.engagement.date}
            </div>
          </div>

          <div style={{ marginBottom: 8, fontSize: 13, color: colors.accentGlow + "55", textTransform: "uppercase", letterSpacing: "0.15em", fontWeight: 500 }}>
            {d.engagement.type} Proposal
          </div>
          <h1
            style={{
              fontSize: 42,
              fontWeight: 800,
              color: "#FFFFFF",
              fontFamily: fonts.heading,
              margin: "0 0 16px",
              lineHeight: 1.15,
              letterSpacing: "-0.02em",
            }}
          >
            Advisory Proposal for
            <br />
            <span style={{ color: colors.gold }}>{d.client.companyName}</span>
          </h1>
          <p style={{ fontSize: 17, color: colors.accentGlow + "99", lineHeight: 1.7, maxWidth: 600, margin: 0 }}>
            Prepared exclusively for {d.client.ownerName} — a confidential proposal to represent {d.client.companyName} in a {d.engagement.type.toLowerCase()} transaction.
          </p>
        </div>
      </header>

      {/* ─── NAV ─── */}
      <nav
        style={{
          background: colors.surface,
          borderBottom: `1px solid ${colors.border}`,
          position: "sticky",
          top: 0,
          zIndex: 100,
        }}
      >
        <div
          style={{
            maxWidth: 900,
            margin: "0 auto",
            padding: "0 32px",
            display: "flex",
            gap: 0,
            overflowX: "auto",
          }}
        >
          {navItems.map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              style={{
                padding: "16px 20px",
                fontSize: 13,
                fontWeight: activeTab === item.id ? 700 : 500,
                color: activeTab === item.id ? colors.accent : colors.textMuted,
                background: "none",
                border: "none",
                borderBottom: activeTab === item.id ? `2px solid ${colors.accent}` : "2px solid transparent",
                cursor: "pointer",
                fontFamily: fonts.body,
                whiteSpace: "nowrap",
                transition: "all 0.15s ease",
              }}
            >
              {item.label}
            </button>
          ))}
        </div>
      </nav>

      {/* ─── CONTENT ─── */}
      <main style={{ maxWidth: 900, margin: "0 auto", padding: "0 32px 80px" }}>
        {/* ═══ OVERVIEW ═══ */}
        {activeTab === "overview" && (
          <div>
            <SectionDivider number="01" title="Executive Summary" />
            <div
              style={{
                background: colors.surface,
                borderRadius: 16,
                padding: 36,
                border: `1px solid ${colors.border}`,
                lineHeight: 1.8,
                fontSize: 16,
                color: colors.textSecondary,
              }}
            >
              <p style={{ margin: "0 0 20px" }}>
                <strong style={{ color: colors.textPrimary }}>Dear {d.client.ownerName},</strong>
              </p>
              <p style={{ margin: "0 0 20px" }}>
                Thank you for the opportunity to discuss the future of {d.client.companyName}. Based on our preliminary review of your operations,
                financial performance, and position within the {d.client.tradeVertical} market, we believe your company represents a compelling
                acquisition opportunity for strategic and financial buyers.
              </p>
              <p style={{ margin: "0 0 20px" }}>
                {d.firm.name} proposes to serve as your exclusive sell-side advisor. Our role is to maximize your outcome — in both price and terms —
                by running a structured, competitive process that brings multiple qualified buyers to the table.
              </p>
              <div
                style={{
                  background: `linear-gradient(135deg, ${colors.navy}, ${colors.navyLight})`,
                  borderRadius: 12,
                  padding: 28,
                  marginTop: 24,
                }}
              >
                <div style={{ fontSize: 12, fontWeight: 600, color: colors.gold, textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 12 }}>
                  Preliminary Valuation Range
                </div>
                <div style={{ display: "flex", alignItems: "baseline", gap: 8, flexWrap: "wrap" }}>
                  <span style={{ fontSize: 36, fontWeight: 800, color: "#FFF", fontFamily: fonts.heading }}>{d.valuation.evLow}</span>
                  <span style={{ fontSize: 20, color: colors.accentGlow + "66" }}>to</span>
                  <span style={{ fontSize: 36, fontWeight: 800, color: "#FFF", fontFamily: fonts.heading }}>{d.valuation.evHigh}</span>
                </div>
                <div style={{ fontSize: 14, color: colors.accentGlow + "77", marginTop: 8 }}>
                  Based on {d.valuation.multLow}x – {d.valuation.multHigh}x {d.valuation.earningsMetric}
                </div>
              </div>
            </div>

            {/* Company Snapshot */}
            <SectionDivider number="02" title="Company Snapshot" />
            <div style={{ display: "flex", flexWrap: "wrap", gap: 12 }}>
              <MetricCard label="Annual Revenue" value={d.client.annualRevenue} />
              <MetricCard label="Adjusted EBITDA" value={d.client.adjustedEbitda} />
              <MetricCard label="EBITDA Margin" value={d.client.ebitdaMargin} />
              <MetricCard label="Recurring Revenue" value={d.client.recurringRevenue} sublabel="Maintenance agreements" />
              <MetricCard label="Employees" value={d.client.employeeCount} />
              <MetricCard label="Fleet" value={d.client.fleetSize} sublabel="Service vehicles" />
              <MetricCard label="Revenue Mix" value={d.client.revenueMix} />
              <MetricCard label="Founded" value={d.client.yearFounded} />
            </div>
          </div>
        )}

        {/* ═══ MARKET ═══ */}
        {activeTab === "market" && (
          <div>
            <SectionDivider number="03" title="Market Overview" />
            <div style={{ display: "flex", flexWrap: "wrap", gap: 12, marginBottom: 32 }}>
              <MetricCard label="Current Multiples" value={d.market.currentMultipleRange} sublabel={d.client.tradeVertical + " businesses"} />
              <MetricCard label="Active Buyers" value={d.market.activeBuyers} sublabel="In home services" />
              <MetricCard label="Recent Deals" value={d.market.recentDealCount} sublabel="Past 12 months" />
              <MetricCard label="Avg Deal Size" value={d.market.averageDealSize} />
            </div>

            <h3 style={{ fontSize: 18, fontWeight: 700, marginBottom: 16, color: colors.textPrimary }}>Why Now</h3>
            <div style={{ background: colors.surface, borderRadius: 12, border: `1px solid ${colors.border}`, overflow: "hidden" }}>
              {d.market.timingRationale.map((r, i) => (
                <div key={i} style={{ padding: "16px 24px", borderBottom: i < d.market.timingRationale.length - 1 ? `1px solid ${colors.borderLight}` : "none", display: "flex", gap: 12, alignItems: "flex-start" }}>
                  <span style={{ color: colors.green, fontWeight: 700, fontSize: 18, lineHeight: 1.4 }}>+</span>
                  <span style={{ fontSize: 15, color: colors.textSecondary, lineHeight: 1.6 }}>{r}</span>
                </div>
              ))}
            </div>

            <h3 style={{ fontSize: 18, fontWeight: 700, margin: "32px 0 16px", color: colors.textPrimary }}>Comparable Transactions</h3>
            <div style={{ background: colors.surface, borderRadius: 12, border: `1px solid ${colors.border}`, overflow: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 14, fontFamily: fonts.body }}>
                <thead>
                  <tr>
                    {["Type", "Size", "Multiple", "Buyer", "Date"].map((h) => (
                      <th key={h} style={{ padding: "14px 16px", textAlign: "left", fontWeight: 600, fontSize: 12, textTransform: "uppercase", letterSpacing: "0.06em", color: colors.textMuted, borderBottom: `2px solid ${colors.border}`, background: colors.surfaceMuted }}>
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {d.market.comps.map((c, i) => (
                    <tr key={i}>
                      <td style={{ padding: "12px 16px", fontWeight: 600, color: colors.textPrimary, borderBottom: `1px solid ${colors.borderLight}` }}>{c.type}</td>
                      <td style={{ padding: "12px 16px", fontFamily: fonts.mono, fontWeight: 700, color: colors.textPrimary, borderBottom: `1px solid ${colors.borderLight}` }}>{c.size}</td>
                      <td style={{ padding: "12px 16px", fontFamily: fonts.mono, color: colors.accent, fontWeight: 700, borderBottom: `1px solid ${colors.borderLight}` }}>{c.multiple}</td>
                      <td style={{ padding: "12px 16px", color: colors.textSecondary, borderBottom: `1px solid ${colors.borderLight}` }}>{c.buyer}</td>
                      <td style={{ padding: "12px 16px", color: colors.textMuted, fontFamily: fonts.mono, borderBottom: `1px solid ${colors.borderLight}` }}>{c.date}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* ═══ VALUATION ═══ */}
        {activeTab === "valuation" && (
          <div>
            <SectionDivider number="04" title="Preliminary Valuation" />
            <div style={{ background: colors.surface, borderRadius: 16, border: `1px solid ${colors.border}`, padding: 36 }}>
              <div style={{ fontSize: 14, color: colors.textMuted, marginBottom: 24 }}>
                Based on {d.valuation.earningsMetric} of <strong style={{ color: colors.textPrimary }}>{d.valuation.earningsAmount}</strong>
              </div>
              <ValuationBar label="Conservative" multiple={d.valuation.multLow} value={d.valuation.evLow} maxWidth={40} color={colors.textMuted} />
              <ValuationBar label="Base Case" multiple={d.valuation.multMid} value={d.valuation.evMid} maxWidth={65} color={colors.accent} />
              <ValuationBar label="Optimistic" multiple={d.valuation.multHigh} value={d.valuation.evHigh} maxWidth={90} color={colors.green} />
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginTop: 24 }}>
              <div style={{ background: colors.greenBg, borderRadius: 12, padding: 24, border: `1px solid ${colors.green}22` }}>
                <div style={{ fontSize: 13, fontWeight: 700, color: colors.green, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 16 }}>Upside Factors</div>
                {d.valuation.upsideFactors.map((f, i) => (
                  <div key={i} style={{ display: "flex", gap: 8, marginBottom: 10, fontSize: 14, color: colors.textSecondary, lineHeight: 1.5 }}>
                    <span style={{ color: colors.green, fontWeight: 700 }}>+</span> {f}
                  </div>
                ))}
              </div>
              <div style={{ background: colors.redBg, borderRadius: 12, padding: 24, border: `1px solid ${colors.red}22` }}>
                <div style={{ fontSize: 13, fontWeight: 700, color: colors.red, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 16 }}>Risk Factors</div>
                {d.valuation.downsideFactors.map((f, i) => (
                  <div key={i} style={{ display: "flex", gap: 8, marginBottom: 10, fontSize: 14, color: colors.textSecondary, lineHeight: 1.5 }}>
                    <span style={{ color: colors.red, fontWeight: 700 }}>-</span> {f}
                  </div>
                ))}
              </div>
            </div>

            <h3 style={{ fontSize: 18, fontWeight: 700, margin: "32px 0 16px", color: colors.textPrimary }}>EBITDA Adjustments Considered</h3>
            <div style={{ background: colors.surface, borderRadius: 12, border: `1px solid ${colors.border}`, overflow: "hidden" }}>
              {d.valuation.adjustments.map((a, i) => (
                <div key={i} style={{ padding: "14px 24px", borderBottom: i < d.valuation.adjustments.length - 1 ? `1px solid ${colors.borderLight}` : "none", fontSize: 15, color: colors.textSecondary, display: "flex", gap: 12, alignItems: "center" }}>
                  <span style={{ color: colors.accent, fontSize: 8 }}>●</span> {a}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ═══ PROCESS ═══ */}
        {activeTab === "process" && (
          <div>
            <SectionDivider number="05" title="Our Process" />
            <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 24, background: colors.surface, borderRadius: 12, padding: "16px 24px", border: `1px solid ${colors.border}` }}>
              <span style={{ fontSize: 13, color: colors.textMuted }}>Expected Timeline:</span>
              <span style={{ fontSize: 18, fontWeight: 700, color: colors.textPrimary, fontFamily: fonts.heading }}>{d.engagement.expectedTimeline}</span>
            </div>
            {d.process.map((p, i) => (
              <PhaseCard
                key={i}
                {...p}
                isExpanded={expandedPhase === i}
                onToggle={() => setExpandedPhase(expandedPhase === i ? -1 : i)}
              />
            ))}
          </div>
        )}

        {/* ═══ BUYERS ═══ */}
        {activeTab === "buyers" && (
          <div>
            <SectionDivider number="06" title="Buyer Universe" />
            <div style={{ display: "flex", flexWrap: "wrap", gap: 12, marginBottom: 32 }}>
              <MetricCard label="Total Universe" value={d.buyers.totalUniverse} sublabel="Qualified prospects" />
              <MetricCard label="Expected Outreach" value={d.buyers.expectedOutreach} sublabel="Targeted contacts" />
              <MetricCard label="Expected NDAs" value={d.buyers.expectedNDAs} />
              <MetricCard label="Expected IOIs" value={d.buyers.expectedIOIs} />
              <MetricCard label="Expected LOIs" value={d.buyers.expectedLOIs} />
            </div>

            <h3 style={{ fontSize: 16, fontWeight: 700, color: colors.textPrimary, marginBottom: 12 }}>Strategic Acquirers</h3>
            <div style={{ marginBottom: 24 }}>
              {d.buyers.strategic.map((b) => <BuyerTag key={b} name={b} type="strategic" />)}
            </div>

            <h3 style={{ fontSize: 16, fontWeight: 700, color: colors.textPrimary, marginBottom: 12 }}>PE-Backed Platforms</h3>
            <div style={{ marginBottom: 24 }}>
              {d.buyers.pePlatforms.map((b) => (
                <BuyerTag key={b.name} name={`${b.name} (${b.fund})`} type="pe" />
              ))}
            </div>

            <h3 style={{ fontSize: 16, fontWeight: 700, color: colors.textPrimary, marginBottom: 12 }}>Independent Sponsors & Search Funds</h3>
            <div style={{ marginBottom: 24 }}>
              <BuyerTag name={`${d.buyers.independentCount} Active Sponsors`} type="independent" />
            </div>
          </div>
        )}

        {/* ═══ FEES ═══ */}
        {activeTab === "fees" && (
          <div>
            <SectionDivider number="07" title="Fee Structure" />
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 32 }}>
              <div style={{ background: colors.surface, borderRadius: 12, border: `1px solid ${colors.border}`, padding: 28 }}>
                <div style={{ fontSize: 12, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.08em", color: colors.textMuted, marginBottom: 8 }}>Engagement Fee</div>
                <div style={{ fontSize: 28, fontWeight: 800, color: colors.textPrimary, fontFamily: fonts.heading }}>{d.engagement.engagementFee}</div>
                <div style={{ fontSize: 13, color: colors.textSecondary, marginTop: 8, lineHeight: 1.6 }}>Due upon execution. Credited 100% against Success Fee at closing.</div>
              </div>
              <div style={{ background: colors.surface, borderRadius: 12, border: `1px solid ${colors.border}`, padding: 28 }}>
                <div style={{ fontSize: 12, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.08em", color: colors.textMuted, marginBottom: 8 }}>Monthly Retainer</div>
                <div style={{ fontSize: 28, fontWeight: 800, color: colors.textPrimary, fontFamily: fonts.heading }}>{d.engagement.monthlyRetainer}<span style={{ fontSize: 14, fontWeight: 400, color: colors.textMuted }}>/mo</span></div>
                <div style={{ fontSize: 13, color: colors.textSecondary, marginTop: 8, lineHeight: 1.6 }}>Begins Month 2. Credited against Success Fee.</div>
              </div>
              <div style={{ background: `linear-gradient(135deg, ${colors.navy}, ${colors.navyLight})`, borderRadius: 12, padding: 28 }}>
                <div style={{ fontSize: 12, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.08em", color: colors.gold, marginBottom: 8 }}>Success Fee</div>
                <div style={{ fontSize: 28, fontWeight: 800, color: "#FFF", fontFamily: fonts.heading }}>{d.engagement.successFeeStructure}</div>
                <div style={{ fontSize: 13, color: colors.accentGlow + "88", marginTop: 8, lineHeight: 1.6 }}>Payable at closing from transaction proceeds.</div>
              </div>
              <div style={{ background: colors.surface, borderRadius: 12, border: `1px solid ${colors.border}`, padding: 28 }}>
                <div style={{ fontSize: 12, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.08em", color: colors.textMuted, marginBottom: 8 }}>Minimum Fee</div>
                <div style={{ fontSize: 28, fontWeight: 800, color: colors.textPrimary, fontFamily: fonts.heading }}>{d.engagement.minimumFee}</div>
                <div style={{ fontSize: 13, color: colors.textSecondary, marginTop: 8, lineHeight: 1.6 }}>Floor regardless of transaction size.</div>
              </div>
            </div>

            <h3 style={{ fontSize: 18, fontWeight: 700, color: colors.textPrimary, marginBottom: 16 }}>Fee Illustration by Sale Price</h3>
            <div style={{ background: colors.surface, borderRadius: 12, border: `1px solid ${colors.border}`, overflow: "hidden" }}>
              <FeeTable scenarios={d.fees.scenarios} />
            </div>

            <div style={{ display: "flex", gap: 12, marginTop: 24, flexWrap: "wrap" }}>
              <MetricCard label="Exclusivity Term" value={d.engagement.exclusivityTerm} />
              <MetricCard label="Tail Period" value={d.engagement.tailPeriod} sublabel="Post-expiration" />
            </div>
          </div>
        )}

        {/* ═══ CREDENTIALS ═══ */}
        {activeTab === "credentials" && (
          <div>
            <SectionDivider number="08" title="Firm Credentials" />
            <div style={{ background: colors.surface, borderRadius: 16, border: `1px solid ${colors.border}`, padding: 36, marginBottom: 24, fontSize: 16, lineHeight: 1.8, color: colors.textSecondary }}>
              {d.credentials.description}
            </div>

            <h3 style={{ fontSize: 18, fontWeight: 700, color: colors.textPrimary, marginBottom: 16 }}>Recent Transactions</h3>
            <div style={{ background: colors.surface, borderRadius: 12, border: `1px solid ${colors.border}`, overflow: "auto", marginBottom: 32 }}>
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr>
                    {["Client", "Trade", "Deal Size", "Buyer", "Year"].map((h) => (
                      <th key={h} style={{ padding: "14px 16px", textAlign: "left", fontWeight: 600, fontSize: 12, textTransform: "uppercase", letterSpacing: "0.06em", color: colors.textMuted, borderBottom: `2px solid ${colors.border}`, background: colors.surfaceMuted }}>
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {d.credentials.deals.map((deal, i) => <DealRow key={i} {...deal} />)}
                </tbody>
              </table>
            </div>

            <h3 style={{ fontSize: 18, fontWeight: 700, color: colors.textPrimary, marginBottom: 16 }}>Client Testimonials</h3>
            {d.credentials.testimonials.map((t, i) => <TestimonialCard key={i} {...t} />)}

            <h3 style={{ fontSize: 18, fontWeight: 700, color: colors.textPrimary, margin: "32px 0 16px" }}>Your Advisory Team</h3>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
              {d.credentials.team.map((m, i) => (
                <div key={i} style={{ background: colors.surface, borderRadius: 12, border: `1px solid ${colors.border}`, padding: 24 }}>
                  <div style={{ fontSize: 18, fontWeight: 700, color: colors.textPrimary, marginBottom: 4 }}>{m.name}</div>
                  <div style={{ fontSize: 13, fontWeight: 600, color: colors.accent, marginBottom: 12 }}>{m.title}</div>
                  <div style={{ fontSize: 14, color: colors.textSecondary, lineHeight: 1.6 }}>{m.bio}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ═══ NEXT STEPS ═══ */}
        {activeTab === "next" && (
          <div>
            <SectionDivider number="09" title="Next Steps" />
            <div
              style={{
                background: `linear-gradient(135deg, ${colors.navy}, ${colors.navyLight})`,
                borderRadius: 16,
                padding: 48,
                textAlign: "center",
              }}
            >
              <div style={{ fontSize: 13, fontWeight: 600, color: colors.gold, textTransform: "uppercase", letterSpacing: "0.15em", marginBottom: 16 }}>
                To Proceed
              </div>
              <h2 style={{ fontSize: 32, fontWeight: 800, color: "#FFF", margin: "0 0 32px", lineHeight: 1.3 }}>
                Three steps to get started.
              </h2>

              <div style={{ display: "flex", justifyContent: "center", gap: 24, flexWrap: "wrap", marginBottom: 40 }}>
                {[
                  { num: "1", text: "Sign the attached Engagement Letter" },
                  { num: "2", text: `Submit engagement fee of ${d.engagement.engagementFee}` },
                  { num: "3", text: "Schedule your kickoff call" },
                ].map((step) => (
                  <div key={step.num} style={{ background: "#FFFFFF11", borderRadius: 12, padding: "24px 28px", maxWidth: 220, textAlign: "center" }}>
                    <div style={{ width: 40, height: 40, borderRadius: "50%", background: colors.gold, color: colors.navy, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 18, fontWeight: 800, margin: "0 auto 12px" }}>
                      {step.num}
                    </div>
                    <div style={{ fontSize: 15, color: "#FFFFFFCC", lineHeight: 1.5 }}>{step.text}</div>
                  </div>
                ))}
              </div>

              <div style={{ borderTop: "1px solid #FFFFFF22", paddingTop: 32 }}>
                <div style={{ fontSize: 16, fontWeight: 600, color: "#FFF" }}>{d.firm.name}</div>
                <div style={{ fontSize: 14, color: colors.accentGlow + "88", marginTop: 8, lineHeight: 1.8 }}>
                  {d.firm.phone} &nbsp;|&nbsp; {d.firm.email} &nbsp;|&nbsp; {d.firm.website}
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* ─── FOOTER ─── */}
      <footer style={{ borderTop: `1px solid ${colors.border}`, padding: "24px 32px", textAlign: "center" }}>
        <div style={{ fontSize: 12, color: colors.textMuted }}>
          Confidential — Prepared by {d.firm.name} — {d.engagement.date}
        </div>
      </footer>
    </div>
  );
}