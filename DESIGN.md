---
name: Kinetic Pulse
colors:
  surface: '#131313'
  surface-dim: '#131313'
  surface-bright: '#3a3939'
  surface-container-lowest: '#0e0e0e'
  surface-container-low: '#1c1b1b'
  surface-container: '#201f1f'
  surface-container-high: '#2a2a2a'
  surface-container-highest: '#353534'
  on-surface: '#e5e2e1'
  on-surface-variant: '#e7bcb9'
  inverse-surface: '#e5e2e1'
  inverse-on-surface: '#313030'
  outline: '#ae8885'
  outline-variant: '#5d3f3d'
  surface-tint: '#ffb3ae'
  primary: '#ffb3ae'
  on-primary: '#68000c'
  primary-container: '#e6192e'
  on-primary-container: '#fffcff'
  inverse-primary: '#c00020'
  secondary: '#ffdf9e'
  on-secondary: '#3f2e00'
  secondary-container: '#fabd00'
  on-secondary-container: '#6a4e00'
  tertiary: '#c7c6c6'
  on-tertiary: '#303031'
  tertiary-container: '#757575'
  on-tertiary-container: '#fffdfd'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#ffdad7'
  primary-fixed-dim: '#ffb3ae'
  on-primary-fixed: '#410005'
  on-primary-fixed-variant: '#930016'
  secondary-fixed: '#ffdf9e'
  secondary-fixed-dim: '#fabd00'
  on-secondary-fixed: '#261a00'
  on-secondary-fixed-variant: '#5b4300'
  tertiary-fixed: '#e4e2e2'
  tertiary-fixed-dim: '#c7c6c6'
  on-tertiary-fixed: '#1b1c1c'
  on-tertiary-fixed-variant: '#464747'
  background: '#131313'
  on-background: '#e5e2e1'
  surface-variant: '#353534'
typography:
  display-lg:
    fontFamily: Sora
    fontSize: 48px
    fontWeight: '800'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Sora
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
  headline-lg-mobile:
    fontFamily: Sora
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 36px
  body-md:
    fontFamily: Geist
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-sm:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.05em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  base: 8px
  gutter: 16px
  margin-mobile: 20px
  margin-desktop: 64px
  max-width: 1280px
---

## Brand & Style
This design system captures a high-energy, "connected" digital experience designed for a youth-centric, tech-savvy audience. The brand personality is bold, urgent, and innovative, bridging the gap between traditional symbols and future-forward technology. 

The visual style is a fusion of **Modern Corporate** precision and **High-Contrast/Glow** aesthetics. It utilizes a "Dark Mode First" philosophy, where deep blacks provide a void-like canvas for vibrant "signal" colors to pop. The interface should feel like a digital command center—precise, responsive, and illuminated by data. Key visual motifs include subtle geometric data patterns, thin line-work reminiscent of circuitry, and focused "glow" states that simulate light emission from a screen.

## Colors
The palette is rooted in a **Deep Black (#0A0A0A)** foundation to ensure maximum contrast and visual depth. 

- **Vibrant Red (#E6192E):** The primary action color, signifying energy and the core "Conectados" identity. Used for primary buttons, critical status, and key brand highlights.
- **Golden Yellow (#FFC107):** Used as a secondary signal color for warnings, highlights, and to add a "high-tech" warmth to the interface.
- **Cool Grey (#707070):** Provides structural balance, used for borders, secondary text, and inactive states to keep the UI from feeling overwhelming.
- **Signal White (#FFFFFF):** Reserved for high-readability body text and "on-dark" iconography.

Gradients should be used sparingly, primarily as "light leaks" or subtle glows behind primary components to simulate a digital signal.

## Typography
The typography strategy utilizes three distinct families to reinforce the "Conectados 3.0" tech narrative:

1.  **Sora (Headlines):** A geometric sans-serif with a futuristic edge. Use Bold or Extra Bold weights for all primary headings to create a strong, rhythmic hierarchy.
2.  **Geist (Body):** A clean, highly legible font optimized for dark backgrounds. It maintains a technical yet approachable feel for long-form content.
3.  **JetBrains Mono (Labels/Data):** Used for micro-copy, tags, and data points to provide a "coded" or "system" aesthetic that appeals to a high-tech audience.

All "Display" and "Headline" roles should use tighter letter spacing to maintain a compact, impactful look.

## Layout & Spacing
The layout follows a **Fluid Grid** system based on an 8px square rhythm. This ensures alignment across all components and reinforces the "digital grid" concept.

- **Desktop:** 12-column grid with 24px gutters. Use wide margins (64px+) to create a focused, premium feel.
- **Tablet:** 8-column grid with 16px gutters.
- **Mobile:** 4-column grid with 16px gutters and 20px side margins.

Content should be grouped into "modules" with consistent internal padding. Use larger vertical spacing (64px-80px) between sections to allow the dark background to act as a "breathing space" between high-intensity content blocks.

## Elevation & Depth
Depth is created through **Tonal Layers** and **Subtle Glows** rather than traditional shadows. In a dark UI, elevation is perceived by elements becoming lighter as they "rise" toward the user.

- **Level 0 (Background):** Pure #0A0A0A.
- **Level 1 (Cards/Containers):** #1A1A1A with a thin 1px border of #2A2A2A.
- **Level 2 (Popovers/Modals):** #222222 with a subtle Red or Grey outer glow (4px-8px blur, 10% opacity).
- **Interactive Depth:** When a user hovers over a primary element, increase the inner "glow" or saturation of the primary color to simulate an active electronic state.

## Shapes
The shape language is **Soft (0.25rem - 0.75rem)**. While the brand is high-tech, absolute sharp corners are avoided to maintain a "youthful and approachable" feel.

- **Standard Elements:** 4px (0.25rem) radius for inputs and small chips.
- **Cards & Sections:** 12px (0.75rem) radius for a modern, containerized look.
- **Icons:** Use linear icons with a 2px stroke weight to match the "connected" lines found in the logo's cross and signal waves.

## Components
- **Buttons:** Primary buttons use a solid Red background with White text. Hover states should trigger a Red outer glow. Secondary buttons use a Grey outline with a Golden Yellow text hover effect.
- **Input Fields:** Dark Grey backgrounds (#1A1A1A) with 1px borders. On focus, the border transitions to Red with a subtle "pulse" animation.
- **Chips/Tags:** Use the JetBrains Mono font. Tags should have a subtle tint of the primary color (e.g., 10% Red background with 100% Red text).
- **Cards:** Use a "Glass" effect for featured content—semi-transparent dark backgrounds with a subtle blur (8px) to let background gradients peek through.
- **Status Indicators:** Use the "Signal" icon style from the logo (concentric arcs) for loading states or connectivity indicators.
- **Progress Bars:** Utilize a gradient from Red to Golden Yellow to indicate "charging" or "connecting" states, reinforcing the kinetic energy of the brand.