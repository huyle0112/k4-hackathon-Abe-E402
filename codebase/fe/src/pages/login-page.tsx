import { useState, type FormEvent } from "react"
import { useNavigate } from "react-router-dom"
import { ArrowRight, CheckCircle2, Eye, EyeOff, Loader2 } from "lucide-react"

import { BrandMark } from "@/components/welcome/brand-mark"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

const DEMO_EMAIL = "demo@vinuni.edu.vn"
const DEMO_PASSWORD = "demo1234"

export function LoginPage() {
  const navigate = useNavigate()
  const [email, setEmail] = useState(DEMO_EMAIL)
  const [password, setPassword] = useState(DEMO_PASSWORD)
  const [showPassword, setShowPassword] = useState(false)
  const [remember, setRemember] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setIsSubmitting(true)
    window.setTimeout(() => navigate("/dashboard"), 600)
  }

  return (
    <div className="grid min-h-svh font-sans lg:grid-cols-[1.1fr_1fr]">
      <div className="relative hidden flex-col justify-between overflow-hidden bg-navy px-11 py-9 text-white lg:flex">
        <div
          className="pointer-events-none absolute -top-24 -right-24 size-[440px] rounded-full"
          style={{
            background:
              "radial-gradient(circle, rgba(140,36,56,0.35), transparent 70%)",
          }}
          aria-hidden="true"
        />

        <a
          href="/"
          className="relative flex items-center gap-[9px] text-[15px] font-semibold"
        >
          <BrandMark />
          <span>
            VinUni AI Thực Chiến
            <span className="mx-0.5 font-normal text-white/60">·</span>
          </span>
          <small className="text-[12.5px] font-medium text-white/60">
            VLearn
          </small>
        </a>

        <div className="relative max-w-[480px]">
          <span className="mb-4.5 block font-mono text-[11.5px] font-medium tracking-[0.11em] text-white/70 uppercase">
            VLearn · VinUni AI Thực Chiến
          </span>
          <h1 className="mb-5.5 font-display text-[clamp(30px,3.6vw,44px)] leading-[1.16] font-medium tracking-[-0.01em]">
            Học để hiểu,
            <br />
            không chỉ để trả lời.
          </h1>
          <p className="mb-8 max-w-[420px] text-[16px] leading-[1.65] text-white/80">
            VLearn giúp bạn học theo từng ngày, hỏi tutor ngay trên tài liệu
            và luyện đúng knowledge component còn yếu.
          </p>
          <div className="border-l-2 border-maroon pl-4 text-[15px] text-white/90 italic">
            “Chỗ nào em yếu, hệ thống biết và báo đúng chỗ đó.”
          </div>
        </div>

        <p className="relative text-[12.5px] text-white/60">
          © 2026 VLearn · VinUni AI Thực Chiến. Adaptive Learning Platform.
        </p>
      </div>

      <div className="flex items-center justify-center bg-paper px-6 py-12">
        <Card className="w-full max-w-[440px]">
          <CardHeader className="gap-1.5 px-8 pt-7">
            <CardTitle className="font-display text-2xl font-medium text-navy">
              Chào mừng trở lại
            </CardTitle>
            <CardDescription className="text-[14.5px] text-ink-soft">
              Đăng nhập bằng tài khoản được cấp để tiếp tục
            </CardDescription>
            <span className="mt-2 inline-flex w-fit items-center gap-1.5 rounded-full border border-ok/25 bg-ok/10 px-2.5 py-1 font-mono text-[11px] font-semibold text-ok">
              <CheckCircle2 className="size-3" />
              Đã tự điền tài khoản demo
            </span>
          </CardHeader>

          <CardContent className="px-8 pb-8">
            <form className="space-y-5" onSubmit={handleSubmit}>
              <div className="space-y-2">
                <Label
                  htmlFor="email"
                  className="font-mono text-[11px] tracking-[0.06em] text-ink-soft uppercase"
                >
                  Email đăng nhập
                </Label>
                <Input
                  id="email"
                  type="email"
                  autoComplete="username"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  className="h-11 rounded-[10px] px-3.5 text-[14.5px]"
                />
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label
                    htmlFor="password"
                    className="font-mono text-[11px] tracking-[0.06em] text-ink-soft uppercase"
                  >
                    Mật khẩu
                  </Label>
                  <a href="#" className="text-[13px] font-semibold text-maroon">
                    Quên mật khẩu?
                  </a>
                </div>
                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    autoComplete="current-password"
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                    className="h-11 rounded-[10px] px-3.5 text-[14.5px]"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword((value) => !value)}
                    className="absolute top-1/2 right-3 -translate-y-1/2 text-ink-soft transition-colors hover:text-ink"
                    aria-label={showPassword ? "Ẩn mật khẩu" : "Hiện mật khẩu"}
                  >
                    {showPassword ? (
                      <EyeOff className="size-4.5" />
                    ) : (
                      <Eye className="size-4.5" />
                    )}
                  </button>
                </div>
              </div>

              <label className="flex items-center gap-2.5 text-[13.5px] text-ink-soft">
                <Checkbox
                  checked={remember}
                  onCheckedChange={setRemember}
                />
                Ghi nhớ email của tôi
              </label>

              <Button
                type="submit"
                disabled={isSubmitting}
                className="h-11.5 w-full gap-2 rounded-[10px] bg-navy text-[15px] font-semibold text-white hover:bg-navy/90"
              >
                {isSubmitting ? (
                  <>
                    Đang đăng nhập
                    <Loader2 className="size-4 animate-spin" />
                  </>
                ) : (
                  <>
                    Đăng nhập hệ thống
                    <ArrowRight className="size-4" />
                  </>
                )}
              </Button>
            </form>

            <div className="mt-6 space-y-1.5 rounded-xl border border-line bg-paper p-4.5 text-[13px] leading-[1.65] text-ink-soft">
              <h3 className="mb-1.5 text-[14px] font-semibold text-navy">
                Đăng nhập lần đầu?
              </h3>
              <p>
                <b className="font-semibold text-ink">Tài khoản:</b> email
                bạn đã đăng ký với lớp (email trường, hoặc email cá nhân).
              </p>
              <p>
                <b className="font-semibold text-ink">Mật khẩu:</b> mã học
                viên của bạn.
              </p>
              <p>
                Cần hỗ trợ? Liên hệ{" "}
                <a
                  href="mailto:admin@vlearn.dev"
                  className="font-semibold text-maroon"
                >
                  admin@vlearn.dev
                </a>
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default LoginPage
