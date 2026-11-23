import { loadFont as loadMontserrat } from "@remotion/google-fonts/Montserrat";
import { loadFont as loadPixelify } from "@remotion/google-fonts/PixelifySans";
import { loadFont as loadMono } from "@remotion/google-fonts/JetBrainsMono";

export const captionFont = loadMontserrat("normal", { weights: ["800", "900"], subsets: ["latin", "latin-ext"] }).fontFamily;
// Fonte dos titulos, etiquetas e lupas. Pixel combina com tema retro/games; para outro tema, troque aqui.
export const titleFont = loadPixelify("normal", { weights: ["700"], subsets: ["latin", "latin-ext"] }).fontFamily;
export const monoFont = loadMono("normal", { weights: ["500", "700"], subsets: ["latin"] }).fontFamily;
