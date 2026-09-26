import React from "react";

// Every product is drawn as a small technical diagram rather than a photo —
// a deliberate stand-in that fits a "spec sheet" catalog and needs no
// external image assets. Corner ticks make each icon read like a page
// out of an equipment manual.

function BlueprintFrame({ children, label }) {
  return (
    <div className="blueprint-frame" aria-hidden="true">
      <span className="tick tick-tl" />
      <span className="tick tick-tr" />
      <span className="tick tick-bl" />
      <span className="tick tick-br" />
      <svg viewBox="0 0 100 100" className="blueprint-svg">
        {children}
      </svg>
      {label && <span className="blueprint-label">{label}</span>}
    </div>
  );
}

const strokeProps = {
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 2,
  strokeLinecap: "round",
  strokeLinejoin: "round",
};

export function DripperIcon() {
  return (
    <BlueprintFrame label="fig. 01">
      <path d="M28 30 H72 L58 72 H42 Z" {...strokeProps} />
      <path d="M42 72 V84 H58 V72" {...strokeProps} />
      <path d="M35 30 V22 H65 V30" {...strokeProps} />
      <circle cx="50" cy="50" r="1.5" fill="currentColor" />
    </BlueprintFrame>
  );
}

export function GrinderIcon() {
  return (
    <BlueprintFrame label="fig. 02">
      <rect x="34" y="20" width="32" height="20" rx="2" {...strokeProps} />
      <path d="M38 40 L34 78 H66 L62 40" {...strokeProps} />
      <line x1="34" y1="58" x2="66" y2="58" {...strokeProps} />
      <line x1="50" y1="10" x2="50" y2="20" {...strokeProps} />
      <line x1="42" y1="12" x2="58" y2="12" {...strokeProps} />
    </BlueprintFrame>
  );
}

export function KettleIcon() {
  return (
    <BlueprintFrame label="fig. 03">
      <path d="M30 45 Q30 78 50 78 Q70 78 70 45 Z" {...strokeProps} />
      <path d="M30 45 Q50 38 70 45" {...strokeProps} />
      <path d="M70 48 C 84 46, 88 34, 76 26" {...strokeProps} />
      <path d="M38 40 Q38 26 46 22" {...strokeProps} />
      <ellipse cx="46" cy="66" rx="10" ry="5" {...strokeProps} strokeWidth="1.2" opacity="0.5" />
    </BlueprintFrame>
  );
}

export function ScaleIcon() {
  return (
    <BlueprintFrame label="fig. 04">
      <rect x="22" y="60" width="56" height="16" rx="2" {...strokeProps} />
      <rect x="38" y="34" width="24" height="26" rx="2" {...strokeProps} />
      <line x1="42" y1="42" x2="58" y2="42" {...strokeProps} strokeWidth="1.2" />
      <line x1="42" y1="48" x2="58" y2="48" {...strokeProps} strokeWidth="1.2" />
    </BlueprintFrame>
  );
}

export function CarafeIcon() {
  return (
    <BlueprintFrame label="fig. 05">
      <path d="M40 18 H60 V34 L72 76 Q72 84 62 84 H38 Q28 84 28 76 L40 34 Z" {...strokeProps} />
      <line x1="38" y1="18" x2="62" y2="18" {...strokeProps} />
      <line x1="32" y1="60" x2="68" y2="60" {...strokeProps} strokeWidth="1.2" opacity="0.6" />
    </BlueprintFrame>
  );
}

export function FiltersIcon() {
  return (
    <BlueprintFrame label="fig. 06">
      <path d="M30 26 H70 V70 Q50 84 30 70 Z" {...strokeProps} />
      <path d="M36 26 V64 Q50 74 64 64 V26" {...strokeProps} strokeWidth="1.2" opacity="0.55" />
      <path d="M42 26 V58 Q50 66 58 58 V26" {...strokeProps} strokeWidth="1.2" opacity="0.35" />
    </BlueprintFrame>
  );
}

export const ICONS_BY_CATEGORY = {
  dripper: DripperIcon,
  grinder: GrinderIcon,
  kettle: KettleIcon,
  scale: ScaleIcon,
  carafe: CarafeIcon,
  filters: FiltersIcon,
};
