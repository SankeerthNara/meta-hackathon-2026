import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";

const FONT = "'Segoe UI', 'Nirmala UI', system-ui, sans-serif";

export const Thumbnail: React.FC = () => (
  <AbsoluteFill style={{ background: "#000", fontFamily: FONT }}>
    <Img src={staticFile("img1.png")} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
    <AbsoluteFill style={{ background: "linear-gradient(90deg, rgba(20,24,22,.92) 0%, rgba(20,24,22,.75) 45%, transparent 75%)" }} />
    <div style={{ position: "absolute", left: 90, top: 150, color: "#fff", maxWidth: 1000 }}>
      <div style={{ fontSize: 44, fontWeight: 700, color: "#ffb070", letterSpacing: 3, textTransform: "uppercase" }}>
        Child growth screening
      </div>
      <div style={{ fontSize: 170, fontWeight: 900, lineHeight: 1, marginTop: 20 }}>Poshan Lens</div>
      <div style={{ fontSize: 64, fontWeight: 700, marginTop: 40, lineHeight: 1.2 }}>
        A child's height from a<br />9-second phone video
      </div>
      <div style={{ display: "inline-block", marginTop: 50, padding: "16px 28px", background: "#c2541b", borderRadius: 14,
                    fontSize: 40, fontWeight: 700 }}>
        SAM 3.1 + Muse Spark · Meta AI
      </div>
    </div>
  </AbsoluteFill>
);
