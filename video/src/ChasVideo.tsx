import {
  AbsoluteFill,
  Img,
  interpolate,
  Sequence,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { loadFont as loadAnton } from "@remotion/google-fonts/Anton";
import { loadFont as loadPermanentMarker } from "@remotion/google-fonts/PermanentMarker";
import { loadFont as loadSpaceGrotesk } from "@remotion/google-fonts/SpaceGrotesk";
import { loadFont as loadPacifico } from "@remotion/google-fonts/Pacifico";

const { fontFamily: anton } = loadAnton();
const { fontFamily: marker } = loadPermanentMarker();
const { fontFamily: grotesk } = loadSpaceGrotesk();
const { fontFamily: pacifico } = loadPacifico();

type Energy = "explosive" | "smooth" | "unhinged" | "ethereal";

interface ChasVideoProps {
  flavor: string;
  tagline: string;
  fakeIngredients: string[];
  palette: {
    primary: string;
    accent: string;
  };
  disclaimer: string;
  testimonial: {
    quote: string;
    author: string;
  };
  videoMood: {
    energy: Energy;
    bgTone: string;
  };
  canImageSrc: string;
}

// ── Mood presets ─────────────────────────────────────────────────────
interface MoodConfig {
  slamSpring: { damping: number; stiffness: number; mass: number };
  popSpring: { damping: number; stiffness: number; mass: number };
  canSpring: { damping: number; stiffness: number; mass: number };
  flashIntensity: number;
  shakeIntensity: number;
  floatSpeed: number;
  floatAmp: number;
  ringSpeed: number;
  headlineFont: string;
  questionFont: string;
  quoteFont: string;
}

const MOODS: Record<Energy, MoodConfig> = {
  explosive: {
    slamSpring: { damping: 5, stiffness: 400, mass: 0.2 },
    popSpring: { damping: 4, stiffness: 500, mass: 0.15 },
    canSpring: { damping: 8, stiffness: 80, mass: 1.2 },
    flashIntensity: 1,
    shakeIntensity: 30,
    floatSpeed: 0.06,
    floatAmp: 10,
    ringSpeed: 0.3,
    headlineFont: anton,
    questionFont: marker,
    quoteFont: marker,
  },
  smooth: {
    slamSpring: { damping: 18, stiffness: 120, mass: 0.8 },
    popSpring: { damping: 16, stiffness: 100, mass: 0.7 },
    canSpring: { damping: 20, stiffness: 40, mass: 1.8 },
    flashIntensity: 0.3,
    shakeIntensity: 0,
    floatSpeed: 0.03,
    floatAmp: 15,
    ringSpeed: 0.1,
    headlineFont: pacifico,
    questionFont: pacifico,
    quoteFont: pacifico,
  },
  unhinged: {
    slamSpring: { damping: 4, stiffness: 500, mass: 0.15 },
    popSpring: { damping: 3, stiffness: 600, mass: 0.1 },
    canSpring: { damping: 6, stiffness: 100, mass: 0.8 },
    flashIntensity: 1,
    shakeIntensity: 40,
    floatSpeed: 0.12,
    floatAmp: 20,
    ringSpeed: 0.6,
    headlineFont: marker,
    questionFont: marker,
    quoteFont: marker,
  },
  ethereal: {
    slamSpring: { damping: 25, stiffness: 60, mass: 1.2 },
    popSpring: { damping: 22, stiffness: 50, mass: 1.0 },
    canSpring: { damping: 25, stiffness: 30, mass: 2.0 },
    flashIntensity: 0.15,
    shakeIntensity: 0,
    floatSpeed: 0.02,
    floatAmp: 20,
    ringSpeed: 0.05,
    headlineFont: grotesk,
    questionFont: grotesk,
    quoteFont: pacifico,
  },
};

// ── Scene 1: "AYYO CHAS" ────────────────────────────────────────────
const AyyoChas: React.FC<{ mood: MoodConfig; bgTone: string }> = ({
  mood,
  bgTone,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const slam = spring({ frame, fps, config: mood.slamSpring });

  const shake =
    mood.shakeIntensity > 0 && frame < 10
      ? Math.sin(frame * 5) *
        interpolate(frame, [0, 10], [mood.shakeIntensity, 0])
      : 0;

  const flash = interpolate(
    frame,
    [0, 2, 6],
    [mood.flashIntensity, mood.flashIntensity * 0.8, 0],
    { extrapolateRight: "clamp" }
  );

  return (
    <AbsoluteFill
      style={{
        backgroundColor: bgTone,
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <div
        style={{
          position: "absolute",
          inset: 0,
          backgroundColor: "#FFFFFF",
          opacity: flash,
        }}
      />
      <div
        style={{
          fontSize: 360,
          fontFamily: mood.headlineFont,
          color: "#FFFFFF",
          textAlign: "center",
          transform: `scale(${slam}) translateX(${shake}px)`,
          lineHeight: 0.85,
          letterSpacing: "-0.02em",
          textTransform: "uppercase",
        }}
      >
        AYYO
        <br />
        CHAS
      </div>
    </AbsoluteFill>
  );
};

// ── Scene 2: "U DRINKIN THIS?" ──────────────────────────────────────
const UDrinkinThis: React.FC<{
  accent: string;
  mood: MoodConfig;
  bgTone: string;
}> = ({ accent, mood, bgTone }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const pop = spring({ frame, fps, config: mood.popSpring });

  const flash = interpolate(
    frame,
    [0, 2, 5],
    [mood.flashIntensity, mood.flashIntensity, 0],
    { extrapolateRight: "clamp" }
  );

  const glowSize = 80 + Math.sin(frame * 0.3) * 20;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: bgTone,
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <div
        style={{
          position: "absolute",
          inset: 0,
          backgroundColor: "#FFFFFF",
          opacity: flash,
        }}
      />
      <div
        style={{
          fontSize: 200,
          fontFamily: mood.questionFont,
          color: accent,
          textAlign: "center",
          transform: `scale(${pop})`,
          lineHeight: 1,
          textShadow: `0 0 ${glowSize}px ${accent}88, 0 0 ${glowSize * 2}px ${accent}44`,
        }}
      >
        U
        <br />
        DRINKIN
        <br />
        THIS?
      </div>
    </AbsoluteFill>
  );
};

// ── Scene 3: Can reveal ─────────────────────────────────────────────
const CanReveal: React.FC<{
  canImageSrc: string;
  primary: string;
  accent: string;
  mood: MoodConfig;
  bgTone: string;
}> = ({ canImageSrc, primary, accent, mood, bgTone }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const canSpring = spring({ frame, fps, config: mood.canSpring });

  const canY = interpolate(canSpring, [0, 1], [1200, -50]);
  const canRotation = interpolate(canSpring, [0, 1], [240, -5]);
  const canScale = interpolate(canSpring, [0, 1], [0.6, 1]);

  const settled = frame > 40;
  const floatY = settled
    ? Math.sin((frame - 40) * mood.floatSpeed) * mood.floatAmp
    : 0;
  const floatRotation = settled
    ? Math.sin((frame - 40) * mood.floatSpeed * 0.7) * 2
    : 0;

  const bgPulse = 0.15 + Math.sin(frame * 0.08) * 0.1;
  const bgRotate = frame * mood.ringSpeed;
  const ringScale = 0.8 + Math.sin(frame * 0.05) * 0.3;
  const ring2Scale = 1.0 + Math.cos(frame * 0.04) * 0.25;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: bgTone,
        justifyContent: "center",
        alignItems: "center",
        overflow: "hidden",
      }}
    >
      {/* Animated radial glow */}
      <div
        style={{
          position: "absolute",
          width: 1400,
          height: 1400,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${primary}50 0%, ${primary}15 35%, transparent 65%)`,
          opacity: bgPulse * canSpring,
          transform: `scale(${ringScale})`,
        }}
      />

      {/* Spinning ring */}
      <div
        style={{
          position: "absolute",
          width: 900,
          height: 900,
          borderRadius: "50%",
          border: `2px solid ${primary}25`,
          opacity: canSpring * 0.6,
          transform: `rotate(${bgRotate}deg) scale(${ring2Scale})`,
        }}
      />

      {/* Counter-rotating ring */}
      <div
        style={{
          position: "absolute",
          width: 1100,
          height: 1100,
          borderRadius: "50%",
          border: `1px solid ${accent}15`,
          opacity: canSpring * 0.4,
          transform: `rotate(${-bgRotate * 0.7}deg) scale(${ringScale})`,
        }}
      />

      {/* Accent streaks */}
      {[0, 72, 144, 216, 288].map((angle, i) => {
        const streakOpacity = interpolate(
          Math.sin(frame * 0.1 + i),
          [-1, 1],
          [0, 0.15]
        );
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              width: 3,
              height: 400,
              background: `linear-gradient(to bottom, transparent, ${accent}${Math.round(streakOpacity * 255)
                .toString(16)
                .padStart(2, "0")}, transparent)`,
              transform: `rotate(${angle + bgRotate * 0.5}deg)`,
              transformOrigin: "center center",
            }}
          />
        );
      })}

      {/* Can */}
      <div
        style={{
          transform: `translateY(${canY + floatY}px) rotate(${canRotation + floatRotation}deg) scale(${canScale * 1.4})`,
          filter: `drop-shadow(0 40px 100px ${primary}77)`,
        }}
      >
        <Img
          src={staticFile(canImageSrc)}
          style={{
            height: 1100,
            objectFit: "contain",
          }}
        />
      </div>
    </AbsoluteFill>
  );
};

// ── Scene 4: Fake testimonial ───────────────────────────────────────
const Testimonial: React.FC<{
  quote: string;
  author: string;
  accent: string;
  mood: MoodConfig;
  bgTone: string;
}> = ({ quote, author, accent, mood, bgTone }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const slideIn = spring({
    frame,
    fps,
    config: { damping: 12, stiffness: 100, mass: 0.8 },
  });

  const quoteX = interpolate(slideIn, [0, 1], [-600, 0]);
  const authorDelay = 15;
  const authorOpacity = interpolate(
    frame,
    [authorDelay, authorDelay + 10],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  return (
    <AbsoluteFill
      style={{
        backgroundColor: bgTone,
        justifyContent: "center",
        alignItems: "center",
        padding: 40,
      }}
    >
      <div
        style={{
          transform: `translateX(${quoteX}px)`,
          maxWidth: 1000,
        }}
      >
        <div
          style={{
            fontSize: 72,
            fontFamily: mood.quoteFont,
            color: "#FFFFFF",
            lineHeight: 1.25,
            textAlign: "center",
          }}
        >
          "{quote}"
        </div>
        <div
          style={{
            fontSize: 36,
            color: accent,
            marginTop: 40,
            textAlign: "center",
            opacity: authorOpacity,
            fontFamily: grotesk,
            fontWeight: 700,
            letterSpacing: "0.02em",
          }}
        >
          — {author}
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ── Scene 5: End card ───────────────────────────────────────────────
const EndCard: React.FC<{
  flavor: string;
  primary: string;
  accent: string;
  canImageSrc: string;
  mood: MoodConfig;
  bgTone: string;
}> = ({ flavor, primary, accent, canImageSrc, mood, bgTone }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const slam = spring({
    frame,
    fps,
    config: { damping: 8, stiffness: 200, mass: 0.4 },
  });

  const pulse = 1 + Math.sin(frame * 0.12) * 0.015;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: bgTone,
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <div
        style={{
          position: "absolute",
          width: 800,
          height: 800,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${primary}25 0%, transparent 60%)`,
        }}
      />

      <div style={{ transform: `scale(${slam})`, textAlign: "center" }}>
        <Img
          src={staticFile(canImageSrc)}
          style={{
            height: 750,
            objectFit: "contain",
            transform: `scale(${pulse})`,
            filter: `drop-shadow(0 20px 60px ${primary}55)`,
            marginBottom: 30,
          }}
        />

        <div
          style={{
            fontSize: 100,
            fontFamily: mood.headlineFont,
            color: accent,
            letterSpacing: "-0.01em",
            textTransform: "uppercase",
            textShadow: `0 0 40px ${accent}44`,
          }}
        >
          {flavor}
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ── Scene 6: Disclaimer slam ────────────────────────────────────────
const DisclaimerSlam: React.FC<{
  disclaimer: string;
  accent: string;
  mood: MoodConfig;
  bgTone: string;
}> = ({ disclaimer, accent, mood, bgTone }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const slam = spring({ frame, fps, config: mood.slamSpring });

  const flash = interpolate(
    frame,
    [0, 2, 5],
    [mood.flashIntensity, mood.flashIntensity * 0.6, 0],
    { extrapolateRight: "clamp" }
  );

  return (
    <AbsoluteFill
      style={{
        backgroundColor: bgTone,
        justifyContent: "center",
        alignItems: "center",
        padding: 40,
      }}
    >
      <div
        style={{
          position: "absolute",
          inset: 0,
          backgroundColor: accent,
          opacity: flash,
        }}
      />
      <div
        style={{
          fontSize: 64,
          fontFamily: mood.quoteFont,
          color: "#FFFFFF",
          textAlign: "center",
          transform: `scale(${slam})`,
          lineHeight: 1.2,
        }}
      >
        {disclaimer}
      </div>
    </AbsoluteFill>
  );
};

// ── Main composition ────────────────────────────────────────────────
export const ChasVideo: React.FC<ChasVideoProps> = ({
  flavor,
  tagline,
  fakeIngredients,
  palette,
  disclaimer,
  testimonial,
  videoMood,
  canImageSrc,
}) => {
  const mood = MOODS[videoMood.energy] || MOODS.explosive;
  const bg = videoMood.bgTone || "#0A0A0A";

  return (
    <AbsoluteFill style={{ backgroundColor: bg }}>
      <Sequence from={0} durationInFrames={30}>
        <AyyoChas mood={mood} bgTone={bg} />
      </Sequence>

      <Sequence from={30} durationInFrames={45}>
        <UDrinkinThis accent={palette.accent} mood={mood} bgTone={bg} />
      </Sequence>

      <Sequence from={75} durationInFrames={135}>
        <CanReveal
          canImageSrc={canImageSrc}
          primary={palette.primary}
          accent={palette.accent}
          mood={mood}
          bgTone={bg}
        />
      </Sequence>

      <Sequence from={210} durationInFrames={75}>
        <Testimonial
          quote={testimonial.quote}
          author={testimonial.author}
          accent={palette.accent}
          mood={mood}
          bgTone={bg}
        />
      </Sequence>

      <Sequence from={285} durationInFrames={60}>
        <EndCard
          flavor={flavor}
          primary={palette.primary}
          accent={palette.accent}
          canImageSrc={canImageSrc}
          mood={mood}
          bgTone={bg}
        />
      </Sequence>

      <Sequence from={345} durationInFrames={55}>
        <DisclaimerSlam
          disclaimer={disclaimer}
          accent={palette.accent}
          mood={mood}
          bgTone={bg}
        />
      </Sequence>
    </AbsoluteFill>
  );
};
