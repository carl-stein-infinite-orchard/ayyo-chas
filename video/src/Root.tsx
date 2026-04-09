import { Composition } from "remotion";
import { ChasVideo } from "./ChasVideo";

const defaultProps = {
  flavor: "Garlic & Pickle Swirl",
  tagline: "Spice up your regrets.",
  fakeIngredients: [
    "carbonated water",
    "natural flavors",
    "citric acid",
    "essence of vampire repellent*",
    "brine dreams*",
  ],
  palette: {
    primary: "#8F7768",
    accent: "#C0D72E",
  },
  disclaimer: "May cause excessive garlic breath. You asked for this.",
  testimonial: {
    quote: "If chaos had a taste, this would be your new religion. I kissed eight people and they all cringed.",
    author: "Ruby G., Professional Party Ruiner",
  },
  videoMood: {
    energy: "unhinged" as const,
    bgTone: "#2a261a",
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
