import { CtaBand } from "@/components/welcome/cta-band"
import { DailyLoopSection } from "@/components/welcome/daily-loop-section"
import { FeaturesSection } from "@/components/welcome/features-section"
import { HeroSection } from "@/components/welcome/hero-section"
import { InstructorsSection } from "@/components/welcome/instructors-section"
import { SiteFooter } from "@/components/welcome/site-footer"
import { SiteHeader } from "@/components/welcome/site-header"
import { VisionSection } from "@/components/welcome/vision-section"

export function WelcomePage() {
  return (
    <div className="min-h-svh bg-paper font-sans text-ink antialiased">
      <a
        href="#main-content"
        className="sr-only rounded-br-lg bg-navy px-4 py-2.5 text-white focus:not-sr-only focus:fixed focus:top-0 focus:left-0 focus:z-100"
      >
        Bỏ qua phần điều hướng
      </a>

      <SiteHeader />

      <main id="main-content">
        <HeroSection />
        <VisionSection />
        <DailyLoopSection />
        <FeaturesSection />
        <InstructorsSection />
        <CtaBand />
      </main>

      <SiteFooter />
    </div>
  )
}

export default WelcomePage
