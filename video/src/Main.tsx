import React from "react";
import { AbsoluteFill, Audio, Img, Sequence, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";

export const FPS = 30;
const INK = "#1d2320", BG = "#f7f4ee", ACCENT = "#c2541b", SEV = "#b3261e", OK = "#2e7d4f";
const FONT = "'Segoe UI', 'Nirmala UI', system-ui, sans-serif";
// words per narration paragraph (video/narration.txt): scene lengths follow the voice
const WORDS = [41, 34, 39, 39, 78, 23, 61, 15, 34, 14];
const HINDI =
  "आशा की लंबाई उम्र के हिसाब से बहुत कम है। वजन लंबाई के हिसाब से ठीक है, यह अच्छी बात है। आप बहुत अच्छा ध्यान रख रही हैं। कृपया आज ही स्वास्थ्य केंद्र जाकर डॉक्टर से मिलें।";

const fadeIn = (f: number, d = 15) => interpolate(f, [0, d], [0, 1], { extrapolateRight: "clamp" });

const Photo: React.FC<{ src: string; caption: string; sub?: string }> = ({ src, caption, sub }) => {
  const f = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const scale = interpolate(f, [0, durationInFrames], [1.04, 1.16]); // slow Ken Burns push-in
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      <Img src={staticFile(src)} style={{ width: "100%", height: "100%", objectFit: "cover", transform: `scale(${scale})` }} />
      <AbsoluteFill style={{ background: "linear-gradient(transparent 55%, rgba(0,0,0,.75))" }} />
      <div style={{ position: "absolute", left: 90, bottom: 80, color: "#fff", fontFamily: FONT, opacity: fadeIn(f, 20) }}>
        <div style={{ fontSize: 64, fontWeight: 800 }}>{caption}</div>
        {sub && <div style={{ fontSize: 34, marginTop: 10, opacity: 0.9 }}>{sub}</div>}
      </div>
    </AbsoluteFill>
  );
};

const Card: React.FC<{ children: React.ReactNode; title?: string }> = ({ children, title }) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: BG, color: INK, fontFamily: FONT, padding: 100, opacity: fadeIn(f) }}>
      {title && <div style={{ fontSize: 40, fontWeight: 700, color: ACCENT, letterSpacing: 2, textTransform: "uppercase" }}>{title}</div>}
      {children}
    </AbsoluteFill>
  );
};

// a phone that slides left and right, with a child silhouette on its screen
const Phone: React.FC<{ outline?: boolean; children?: React.ReactNode; slide?: boolean }> = ({ outline, children, slide }) => {
  const f = useCurrentFrame();
  const x = slide ? 160 * Math.sin(f / 22) : 0;
  return (
    <div style={{ position: "absolute", left: 1180 + x, top: 120, width: 420, height: 840, borderRadius: 56, background: "#111",
                  padding: 18, boxShadow: "0 30px 80px rgba(0,0,0,.35)" }}>
      <div style={{ width: "100%", height: "100%", borderRadius: 40, background: "#e9e4da", overflow: "hidden", position: "relative" }}>
        {children ?? (
          <svg viewBox="0 0 100 200" style={{ position: "absolute", left: "25%", top: "10%", width: "50%", height: "80%" }}>
            <g fill={outline ? "rgba(255,120,40,.55)" : "#8a8f99"} stroke={outline ? "#ff7828" : "none"} strokeWidth={2}>
              <circle cx={50} cy={22} r={16} />
              <rect x={28} y={42} width={44} height={70} rx={14} />
              <rect x={31} y={108} width={16} height={78} rx={7} />
              <rect x={53} y={108} width={16} height={78} rx={7} />
            </g>
          </svg>
        )}
      </div>
    </div>
  );
};

const Big: React.FC<{ children: React.ReactNode; size?: number; color?: string; delay?: number }> = ({ children, size = 72, color = INK, delay = 0 }) => {
  const f = useCurrentFrame();
  return <div style={{ fontSize: size, fontWeight: 800, color, marginTop: 30, opacity: fadeIn(f - delay), lineHeight: 1.15, maxWidth: 1000 }}>{children}</div>;
};

const Solution = () => (
  <Card title="The idea">
    <Big size={110} color={ACCENT}>Poshan Lens</Big>
    <Big size={52} delay={20}>Point an ordinary Android phone.<br />Slide it left and right for 9 seconds.</Big>
    <Big size={40} color="#5d6862" delay={45}>No measuring board · no depth camera · no special hardware</Big>
    <Phone slide />
  </Card>
);

const Sam = () => (
  <Card title="Step 1 · Meta SAM 3.1">
    <Big size={64}>Finds the child in every frame</Big>
    <Big size={44} delay={20}>Text prompt: <span style={{ color: ACCENT }}>"child"</span></Big>
    <Big size={40} color="#5d6862" delay={40}>No training data. No photos of real children.<br />ARCore records exactly how the phone moved.</Big>
    <Phone outline slide />
  </Card>
);

const Pluto = () => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const bars = [107, 148, 148];
  return (
    <Card title="Step 2 · Pluto, my measurement method">
      <Big size={60}>Three independent measurements.<br />At least two must agree.</Big>
      <div style={{ display: "flex", gap: 70, alignItems: "flex-end", height: 520, marginTop: 40 }}>
        {bars.map((v, i) => {
          const h = spring({ frame: f - 30 - i * 25, fps, config: { damping: 18 } }) * v * 3;
          const out = i === 0 && f > 160;
          return (
            <div key={i} style={{ textAlign: "center", fontSize: 40, fontWeight: 700 }}>
              <div style={{ width: 170, height: h, background: out ? "#c9c2b5" : OK, borderRadius: 12, position: "relative" }}>
                {out && <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 150, color: SEV }}>✕</div>}
              </div>
              <div style={{ marginTop: 12 }}>{v} cm</div>
            </div>
          );
        })}
        <div style={{ fontSize: 56, fontWeight: 800, color: OK, marginLeft: 60, opacity: fadeIn(f - 190) }}>
          2 of 3 agree<br /><span style={{ fontSize: 36, color: "#5d6862" }}>first real phone test</span>
        </div>
      </div>
    </Card>
  );
};

const Who = () => (
  <Card title="Step 3 · WHO growth standards">
    <Big size={64}>z-scores computed in plain code</Big>
    <Big size={44} delay={20}>Height-for-age · weight-for-height · WHO 2006 tables</Big>
    <Big size={44} color={OK} delay={40}>The language model never does the maths.<br />Every number can be audited.</Big>
  </Card>
);

const Spark = () => (
  <Card title="Step 4 · Meta Muse Spark">
    <Big size={60}>Checks the photo.<br />Explains the result.</Big>
    <Big size={40} delay={25}>✓ Worker checklist<br />✓ Parent message in her language and script<br />✓ Read aloud on the phone</Big>
    <Big size={36} color="#5d6862" delay={45}>Hindi · Telugu · Tamil · Kannada · Marathi · Bengali …</Big>
    <Phone>
      <div style={{ padding: 26, fontFamily: FONT }}>
        <div style={{ fontSize: 54, fontWeight: 800 }}>78.4 cm</div>
        <div style={{ background: SEV, color: "#fff", borderRadius: 10, padding: "10px 14px", fontSize: 22, marginTop: 10, fontWeight: 700 }}>Severe stunting · Refer today</div>
        <div style={{ background: "#fff", borderLeft: `6px solid ${ACCENT}`, borderRadius: 10, padding: 16, fontSize: 25, lineHeight: 1.5, marginTop: 18 }}>{HINDI}</div>
        <div style={{ background: ACCENT, color: "#fff", borderRadius: 12, padding: "12px 16px", fontSize: 24, fontWeight: 700, marginTop: 16, width: "fit-content" }}>🔊 Read aloud</div>
      </div>
    </Phone>
  </Card>
);

const Refer = () => (
  <AbsoluteFill style={{ background: SEV, color: "#fff", fontFamily: FONT, justifyContent: "center", alignItems: "center", textAlign: "center" }}>
    <div style={{ fontSize: 96, fontWeight: 800 }}>Severe? Visit the health centre today.</div>
    <div style={{ fontSize: 40, marginTop: 24 }}>A screening aid, not a diagnosis.</div>
  </AbsoluteFill>
);

const Impact = () => (
  <Card title="Impact">
    <Big size={84}>≈ $0.15 per child</Big>
    <Big size={52} delay={15}>Runs on phones workers already carry</Big>
    <Big size={52} delay={30}>1.4 million Anganwadi centres</Big>
    <Big size={52} color={ACCENT} delay={45}>So no child is missed.</Big>
  </Card>
);

const Title = () => (
  <AbsoluteFill style={{ background: INK, color: "#fff", fontFamily: FONT, justifyContent: "center", alignItems: "center", textAlign: "center" }}>
    <div style={{ fontSize: 130, fontWeight: 800, color: "#ffb070" }}>Poshan Lens</div>
    <div style={{ fontSize: 48, marginTop: 20 }}>Built with SAM 3.1 + Muse Spark on the Meta Model API</div>
    <div style={{ fontSize: 34, marginTop: 30, opacity: 0.75 }}>github.com/SankeerthNara/meta-hackathon-2026</div>
  </AbsoluteFill>
);

const SCENES: React.FC[] = [
  () => <Photo src="img1.png" caption="1.4 million Anganwadi centres" sub="Every child under five, measured every month" />,
  () => <Photo src="img2.png" caption="35.5 % of children under 5 are stunted" sub="NFHS-5 · height is the number most often skipped or wrong" />,
  Solution, Sam, Pluto, Who, Spark, Refer, Impact, Title,
];

export const Main: React.FC = () => {
  const { durationInFrames } = useVideoConfig();
  const speech = durationInFrames - 2 * FPS;
  const total = WORDS.reduce((a, b) => a + b, 0);
  let start = 0;
  return (
    <AbsoluteFill style={{ background: BG }}>
      <Audio src={staticFile("narration.mp3")} />
      {SCENES.map((S, i) => {
        const len = i === SCENES.length - 1 ? durationInFrames - start : Math.round((speech * WORDS[i]) / total);
        const seq = <Sequence key={i} from={start} durationInFrames={len}><S /></Sequence>;
        start += len;
        return seq;
      })}
    </AbsoluteFill>
  );
};
