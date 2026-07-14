---
name: Luminous Editorial
colors:
  surface: '#fcf9f8'
  surface-dim: '#dcd9d9'
  surface-bright: '#fcf9f8'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f6f3f2'
  surface-container: '#f0edec'
  surface-container-high: '#ebe7e7'
  surface-container-highest: '#e5e2e1'
  on-surface: '#1c1b1b'
  on-surface-variant: '#494454'
  inverse-surface: '#313030'
  inverse-on-surface: '#f3f0ef'
  outline: '#7b7486'
  outline-variant: '#cbc3d7'
  surface-tint: '#6d3bd7'
  primary: '#6b38d4'
  on-primary: '#ffffff'
  primary-container: '#8455ef'
  on-primary-container: '#fffbff'
  inverse-primary: '#d0bcff'
  secondary: '#4648d4'
  on-secondary: '#ffffff'
  secondary-container: '#6063ee'
  on-secondary-container: '#fffbff'
  tertiary: '#855000'
  on-tertiary: '#ffffff'
  tertiary-container: '#a76500'
  on-tertiary-container: '#fffbff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#e9ddff'
  primary-fixed-dim: '#d0bcff'
  on-primary-fixed: '#23005c'
  on-primary-fixed-variant: '#5516be'
  secondary-fixed: '#e1e0ff'
  secondary-fixed-dim: '#c0c1ff'
  on-secondary-fixed: '#07006c'
  on-secondary-fixed-variant: '#2f2ebe'
  tertiary-fixed: '#ffdcbb'
  tertiary-fixed-dim: '#ffb869'
  on-tertiary-fixed: '#2c1700'
  on-tertiary-fixed-variant: '#673d00'
  background: '#fcf9f8'
  on-background: '#1c1b1b'
  surface-variant: '#e5e2e1'
typography:
  headline-xl:
    fontFamily: Inter
    fontSize: 40px
    fontWeight: '600'
    lineHeight: 48px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 14px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 4px
  xs: 8px
  sm: 12px
  md: 16px
  lg: 24px
  xl: 32px
  xxl: 48px
  gutter: 20px
  margin-mobile: 16px
  margin-desktop: 40px
---

## Brand & Style

The design system is built on the principles of clarity, intentionality, and high-end utility. It targets creative professionals and educators who require a focused environment for high-fidelity video editing. The brand personality is "The Quiet Architect": sophisticated and powerful, yet humble enough to let the user's content remain the protagonist.

The aesthetic merges **Corporate Modernism** with **Minimalist Utility**. It draws from the structural precision of Linear, the spatial breathing room of Notion, and the tactile refinement of the Apple ecosystem. The emotional response is one of calm confidence—reducing the cognitive load of complex video timelines through generous whitespace, soft depth, and a disciplined "content-first" hierarchy.

## Colors

This design system utilizes a restricted palette to maintain a premium feel. The primary accent (Purple) is reserved exclusively for high-intent actions like "Export," "Publish," or primary CTA buttons. 

In **Light Mode**, the primary background is a warm white (#FAFAFA), providing a softer canvas than pure white to reduce eye strain. Cards and panels use subtle grays and thin borders to create containment without visual noise.

In **Dark Mode**, the interface shifts to a deep charcoal (#121212). Rather than using pure black, this depth allows for subtle "elevation" using lighter gray overlays for panels and modals, mimicking physical layers of glass and metal.

## Typography

The system relies on **Inter** for its systematic and neutral character. The typography scale is tight and functional, favoring legibility over decorative flair. 

Headlines utilize tighter letter-spacing and semi-bold weights to appear "locked in" and authoritative. Body text is optimized for long-form reading, while labels use slightly increased weight or uppercase styles to differentiate metadata from content. On mobile, large display types are aggressively scaled down to maintain the clean, "uncluttered" aesthetic within limited horizontal space.

## Layout & Spacing

The layout philosophy follows a **4px baseline grid** to ensure mathematical harmony across all components. The design utilizes a **fluid-fixed hybrid grid**: sidebars and toolbars have fixed widths (e.g., 240px for the asset library), while the main canvas and timeline stretch to fill the viewport.

Spacing is "generous by default." This design system uses wide margins (40px on desktop) to create a gallery-like feeling where the video content is the center of attention. Gutters are kept consistent at 20px to provide clear separation without breaking the visual flow of the UI.

## Elevation & Depth

Visual hierarchy is achieved through **Tonal Layering** and **Ambient Shadows**. Instead of heavy black shadows, this design system uses low-opacity, multi-layered "diffusion" shadows that make elements appear as if they are floating slightly above the surface.

- **Level 0 (Base):** The main background. 
- **Level 1 (Cards/Panels):** Raised by a 1px subtle border (#000000 0.05 opacity) and a soft 4px blur shadow.
- **Level 2 (Modals/Popovers):** Higher elevation using a 12px blur shadow with 0.1 opacity and a slight "glass" backdrop blur (8px) to maintain context of the layer beneath.
- **Level 3 (Primary Actions):** Floating buttons use a tinted shadow matching the primary accent color to draw the eye.

## Shapes

The shape language is defined by large, friendly radii that evoke a sense of modern hardware design. 
- **Small components (Inputs, Chips):** Use `rounded` (0.5rem / 8px).
- **Medium components (Buttons, Tooltips):** Use `rounded-lg` (1rem / 16px).
- **Large components (Cards, Video Player, Main Panels):** Use `rounded-xl` (1.5rem / 24px) for a distinctive, premium container feel.

All corners utilize "continuous curvature" (squircle) principles where possible to avoid the mechanical look of standard geometric rounding.

## Components

### Buttons
Primary buttons use the #8B5CF6 accent with white text. Secondary buttons are "ghost" style—transparent backgrounds with a subtle gray border in light mode, or a semi-transparent white in dark mode. Hover states should involve a subtle scale-down (0.98) to provide tactile "press" feedback.

### Inputs & Fields
Inputs are minimal: a simple underline or a very light gray fill (#F1F1F1). Focus states replace the border with a 1px Purple stroke and a soft glow.

### Cards & Panels
Cards are the primary container. They should have no visible border in most cases, instead using a slight color shift from the background and the Level 1 shadow.

### Video Timeline & Playhead
The timeline should be ultra-minimal. Background is a shade darker than the panel, with "clips" using rounded-md corners. The playhead is a single 2px Purple line with a circular handle at the top.

### Chips & Tags
Used for categories or AI-detected labels. These should have a pill-shape (rounded-full) and use a low-saturation version of the primary color to avoid distracting from the main editor.