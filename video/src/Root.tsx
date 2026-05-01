import { Composition } from "remotion";
import { ChasVideo } from "./ChasVideo";

const defaultProps = {
  flavor: "Galactic Blackcurrant",
  tagline: "Outa this world, sorta illegal",
  fakeIngredients: [
    "carbonated water",
    "natural flavors",
    "citric acid",
    "a splash of alien tears*",
  ],
  palette: {
    primary: "#372948",
    accent: "#96ceb4",
  },
  disclaimer: "Might cause feelings of wanderlust and existential curiosity.",
  testimonial: {
    quote: "I drank this and now 12 astrology blogs follow me\u2014you do the math.",
    author: "Astrid Nova, Interdimensional Switchboard Operator",
  },
  videoMood: {
    energy: "ethereal" as const,
    bgTone: "#2a3040",
  },
  canImageSrc: "assets/label.png",
};

export const Root: React.FC = () => {
  return (
    <Composition
      id="ChasVideo"
      component={ChasVideo}
      durationInFrames={400}
      fps={30}
      width={1080}
      height={1920}
      defaultProps={defaultProps}
    />
  );
};
